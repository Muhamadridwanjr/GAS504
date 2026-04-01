"""
GAS Admin API — Comprehensive admin endpoints.
All endpoints require is_admin=True from JWT/header.
"""
import json
import logging
import os
import time
from datetime import datetime, timezone
from typing import Optional

import httpx
import redis.asyncio as aioredis
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel

from ...core.dependencies import get_current_user_info
from ...utils.email import send_email, render_welcome

logger = logging.getLogger("gas.admin")

router = APIRouter(tags=["Admin"])

REDIS_URL       = os.getenv("REDIS_URL", "redis://gas-redis:6379/0")
AUTH_SERVICE    = os.getenv("AUTH_SERVICE_URL", "http://gas-auth-service:8001")
INTERNAL_KEY    = os.getenv("INTERNAL_API_KEY", "gas-internal-key-2026")
SITE_URL        = os.getenv("SITE_URL", "https://www.gasstrategyai.xyz")

_redis_client: Optional[aioredis.Redis] = None

PLAN_CREDITS = {
    "essential": 100, "plus": 200,
    "premium": 400,   "ultimate": 700, "free": 20,
}


async def _r() -> aioredis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)
    return _redis_client


def _require_admin(user_info: dict = Depends(get_current_user_info)) -> dict:
    if not user_info["is_admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user_info


# ─────────────────────────────────────────────
#  DASHBOARD STATS
# ─────────────────────────────────────────────
@router.get("/admin/stats")
async def get_admin_stats(_=Depends(_require_admin)):
    """System-wide statistics aggregated from Redis."""
    r = await _r()

    # Collect all user keys
    user_keys = await r.keys("user:*:plan")
    plan_counts = {"free": 0, "essential": 0, "plus": 0, "premium": 0, "ultimate": 0}
    total_credits_distributed = 0
    total_credits_remaining   = 0

    for key in user_keys:
        plan = (await r.get(key)) or "free"
        plan_counts[plan] = plan_counts.get(plan, 0) + 1

    credit_keys = await r.keys("user:*:credits")
    for key in credit_keys:
        val = await r.get(key)
        if val:
            total_credits_remaining += int(val)

    # Count all ERC20 transactions
    payment_keys = await r.keys("erc20:order:*")
    completed_payments = 0
    total_revenue_usdt = 0.0
    for pk in payment_keys:
        raw = await r.get(pk)
        if raw:
            data = json.loads(raw)
            if data.get("status") == "completed":
                completed_payments += 1
                try:
                    total_revenue_usdt += float(data.get("amount_usdt", 0))
                except Exception:
                    pass

    # Count support tickets
    ticket_list = await r.lrange("support:ticket_list", 0, -1)
    open_tickets = 0
    for tid in ticket_list:
        raw = await r.get(f"support:ticket:{tid}")
        if raw:
            t = json.loads(raw)
            if t.get("status") in ("open", "pending"):
                open_tickets += 1

    # Recent logins (stored as log events)
    recent_logs = await r.lrange("admin:activity_log", 0, 19)

    return {
        "plans":               plan_counts,
        "total_users":         sum(plan_counts.values()),
        "total_credits_active": total_credits_remaining,
        "completed_payments":  completed_payments,
        "total_revenue_usdt":  round(total_revenue_usdt, 2),
        "open_support_tickets": open_tickets,
        "recent_logs":         [json.loads(l) for l in recent_logs],
        "generated_at":        datetime.utcnow().isoformat(),
    }


# ─────────────────────────────────────────────
#  USER MANAGEMENT
# ─────────────────────────────────────────────
@router.get("/admin/users")
async def admin_list_users(
    skip: int = 0,
    limit: int = 50,
    search: str = "",
    _=Depends(_require_admin),
):
    """List all users from auth-service + enrich with Redis data."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{AUTH_SERVICE}/v1/admin/users",
                params={"skip": skip, "limit": limit, "search": search},
                headers={"X-Internal-Key": INTERNAL_KEY},
            )
            if resp.status_code != 200:
                raise HTTPException(status_code=502, detail="Auth service error")
            auth_data = resp.json()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Auth service unreachable: {e}")
        # Fallback: return empty list
        return {"users": [], "total": 0, "error": "Auth service unreachable"}

    # Enrich each user with Redis data
    r = await _r()
    enriched = []
    for u in auth_data["users"]:
        uid = u["id"]
        plan    = (await r.get(f"user:{uid}:plan")) or "free"
        credits = int((await r.get(f"user:{uid}:credits")) or 0)
        xp      = int((await r.get(f"user:{uid}:xp")) or 0)
        email_stored = (await r.get(f"user:{uid}:email")) or u.get("email", "")
        enriched.append({
            **u,
            "plan":    plan,
            "credits": credits,
            "xp":      xp,
            "email":   email_stored or u.get("email", ""),
        })

    return {
        "users": enriched,
        "total": auth_data.get("total", len(enriched)),
    }


class SetPlanRequest(BaseModel):
    plan: str
    credits: Optional[int] = None


@router.post("/admin/users/{user_id}/set-plan")
async def admin_set_user_plan(
    user_id: str,
    req: SetPlanRequest,
    _=Depends(_require_admin),
):
    """Set user plan and optionally credits."""
    valid_plans = {"free", "essential", "plus", "premium", "ultimate"}
    if req.plan not in valid_plans:
        raise HTTPException(status_code=400, detail=f"Invalid plan. Must be one of {valid_plans}")

    r = await _r()
    await r.set(f"user:{user_id}:plan", req.plan)

    credits = req.credits if req.credits is not None else PLAN_CREDITS.get(req.plan, 20)
    await r.set(f"user:{user_id}:credits", str(credits))

    # Log activity
    await _log_activity(r, "admin_set_plan", f"Set user {user_id} to plan={req.plan} credits={credits}")

    return {"status": "ok", "user_id": user_id, "plan": req.plan, "credits": credits}


class SetCreditsRequest(BaseModel):
    credits: int
    operation: str = "set"  # "set" | "add" | "subtract"


@router.post("/admin/users/{user_id}/set-credits")
async def admin_set_user_credits(
    user_id: str,
    req: SetCreditsRequest,
    _=Depends(_require_admin),
):
    """Set, add, or subtract credits for a user."""
    r = await _r()
    current = int((await r.get(f"user:{user_id}:credits")) or 0)

    if req.operation == "add":
        new_val = current + req.credits
    elif req.operation == "subtract":
        new_val = max(0, current - req.credits)
    else:
        new_val = req.credits

    await r.set(f"user:{user_id}:credits", str(new_val))
    await _log_activity(r, "admin_set_credits", f"Set user {user_id} credits: {current} → {new_val}")

    return {"status": "ok", "user_id": user_id, "credits": new_val, "previous": current}


@router.post("/admin/users/{user_id}/toggle-active")
async def admin_toggle_user(user_id: str, _=Depends(_require_admin)):
    """Toggle user active status in auth-service."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.patch(
                f"{AUTH_SERVICE}/v1/admin/users/{user_id}/toggle-active",
                headers={"X-Internal-Key": INTERNAL_KEY},
            )
            return resp.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Auth service error: {e}")


# ─────────────────────────────────────────────
#  PAYMENT OVERVIEW
# ─────────────────────────────────────────────
@router.get("/admin/payments")
async def admin_list_payments(
    limit: int = 50,
    status_filter: str = "",
    _=Depends(_require_admin),
):
    """List all ERC20 payment orders."""
    r = await _r()
    keys = await r.keys("erc20:order:*")

    payments = []
    for key in keys:
        raw = await r.get(key)
        if raw:
            data = json.loads(raw)
            if not status_filter or data.get("status") == status_filter:
                payments.append(data)

    # Sort by created_at desc
    payments.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    return {
        "payments": payments[:limit],
        "total":    len(payments),
        "completed": sum(1 for p in payments if p.get("status") == "completed"),
        "pending":   sum(1 for p in payments if p.get("status") == "pending"),
        "expired":   sum(1 for p in payments if p.get("status") not in ("completed", "pending")),
    }


# ─────────────────────────────────────────────
#  SUPPORT TICKETS
# ─────────────────────────────────────────────
@router.get("/admin/support")
async def admin_list_tickets(limit: int = 50, _=Depends(_require_admin)):
    r = await _r()
    ticket_ids = await r.lrange("support:ticket_list", 0, limit - 1)
    tickets = []
    for tid in ticket_ids:
        raw = await r.get(f"support:ticket:{tid}")
        if raw:
            tickets.append(json.loads(raw))
    return {
        "tickets": tickets,
        "total": len(tickets),
        "open": sum(1 for t in tickets if t.get("status") == "open"),
        "replied": sum(1 for t in tickets if "replied" in t.get("status", "")),
    }


class AdminReplyRequest(BaseModel):
    reply: str


@router.post("/admin/support/{ticket_id}/reply")
async def admin_reply_support(
    ticket_id: str,
    req: AdminReplyRequest,
    background_tasks: BackgroundTasks,
    _=Depends(_require_admin),
):
    """Send a manual reply to a support ticket."""
    r = await _r()
    raw = await r.get(f"support:ticket:{ticket_id}")
    if not raw:
        raise HTTPException(status_code=404, detail="Ticket not found")
    ticket = json.loads(raw)
    ticket["status"] = "replied"
    ticket["reply"] = req.reply
    ticket["replied_at"] = time.time()
    await r.set(f"support:ticket:{ticket_id}", json.dumps(ticket), ex=86400 * 90)

    background_tasks.add_task(
        _send_support_reply_bg,
        ticket.get("email", ""), ticket.get("name", "User"),
        ticket.get("subject", "Support"), ticket.get("message", ""),
        req.reply, ticket_id,
    )
    return {"status": "ok", "message": f"Reply sent to {ticket.get('email')}"}


# ─────────────────────────────────────────────
#  EMAIL / SMTP TESTER
# ─────────────────────────────────────────────
class TestEmailRequest(BaseModel):
    to_email: str
    email_type: str = "test"  # test | welcome | invoice | payment


@router.post("/admin/email/test")
async def admin_test_email(req: TestEmailRequest, _=Depends(_require_admin)):
    """Send a test email to verify SMTP configuration."""
    from ...utils.email import send_email, render_welcome, render_invoice, render_payment_confirmation

    try:
        if req.email_type == "welcome":
            html = render_welcome("testuser", "Test User", "ultimate")
            subject = "🎉 Test: Welcome Email — Golden AI Strategy"
        elif req.email_type == "invoice":
            html = render_invoice(
                "testuser", "GAS-TEST-001", "Ultimate Plan",
                "19.9942", "0xf8ef68F41B609B06210ebe7d045FA111F2034518",
                "2026-03-15 12:00 UTC", 700, "ultimate"
            )
            subject = "📋 Test: Invoice Email — Golden AI Strategy"
        elif req.email_type == "payment":
            html = render_payment_confirmation(
                "testuser", "GAS-TEST-001", "Ultimate Plan",
                "19.9942", 700, 700, "ultimate", "0xabc123..."
            )
            subject = "✅ Test: Payment Confirmation — Golden AI Strategy"
        else:
            # Generic test email
            from ...utils.email import _base_template, _button
            html = _base_template(
                "GAS Admin SMTP Test",
                f"""
                <h1 style="color:#E2E8F0;font-size:22px;font-weight:800;margin:0 0 16px;">
                  ✅ SMTP Test Berhasil!
                </h1>
                <p style="color:#A0AEC0;font-size:14px;line-height:1.7;margin:0 0 16px;">
                  Email ini dikirim dari admin panel Golden AI Strategy.<br/>
                  Konfigurasi Brevo SMTP Anda berjalan dengan baik.
                </p>
                <div style="background:#111827;border:1px solid rgba(245,166,35,0.2);border-radius:10px;padding:16px;margin:16px 0;">
                  <p style="color:#718096;font-size:12px;margin:0 0 8px;font-weight:700;">SERVER INFO:</p>
                  <p style="color:#E2E8F0;font-size:12px;margin:0;font-family:monospace;">
                    SMTP: smtp-relay.brevo.com:587<br/>
                    FROM: billing@gasstrategyai.xyz<br/>
                    TO: {req.to_email}<br/>
                    TIME: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
                  </p>
                </div>
                {_button("🚀 Buka Admin Panel", SITE_URL)}
                """,
                "Test email dari GAS Admin Panel"
            )
            subject = "✅ GAS Admin SMTP Test — Golden AI Strategy"

        success = send_email(to_email=req.to_email, subject=subject, html_body=html)
        if success:
            return {"status": "ok", "message": f"Email berhasil dikirim ke {req.to_email}", "type": req.email_type}
        else:
            raise HTTPException(status_code=500, detail="Email gagal dikirim. Cek konfigurasi SMTP.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# ─────────────────────────────────────────────
#  SYSTEM LOGS
# ─────────────────────────────────────────────
@router.get("/admin/logs")
async def admin_get_logs(limit: int = 100, _=Depends(_require_admin)):
    """Get recent system activity logs from Redis."""
    r = await _r()
    raw_logs = await r.lrange("admin:activity_log", 0, limit - 1)
    logs = [json.loads(l) for l in raw_logs]

    # Also get recent ERC20 processed transactions
    processed_keys = await r.keys("erc20:processed_tx:*")
    return {
        "activity_logs": logs,
        "total_logs": len(logs),
        "processed_tx_count": len(processed_keys),
    }


@router.delete("/admin/logs")
async def admin_clear_logs(_=Depends(_require_admin)):
    """Clear admin activity logs."""
    r = await _r()
    await r.delete("admin:activity_log")
    return {"status": "ok", "message": "Logs cleared"}


# ─────────────────────────────────────────────
#  SYSTEM HEALTH
# ─────────────────────────────────────────────
@router.get("/admin/health")
async def admin_system_health(_=Depends(_require_admin)):
    """Check health of all services."""
    services = {
        "redis":          {"url": REDIS_URL,                                "status": "unknown"},
        "auth_service":   {"url": f"{AUTH_SERVICE}/v1/health",              "status": "unknown"},
        "strategy_core":  {"url": os.getenv("STRATEGY_CORE_URL", "") + "/health", "status": "unknown"},
    }

    # Check Redis
    try:
        r = await _r()
        await r.ping()
        services["redis"]["status"] = "healthy"
    except Exception as e:
        services["redis"]["status"] = f"error: {e}"

    # Check other services via HTTP
    async with httpx.AsyncClient(timeout=5) as client:
        for name, svc in services.items():
            if name == "redis":
                continue
            try:
                resp = await client.get(svc["url"])
                services[name]["status"] = "healthy" if resp.status_code < 400 else f"http_{resp.status_code}"
            except Exception as e:
                services[name]["status"] = f"error"

    overall = "healthy" if all(s["status"] == "healthy" for s in services.values()) else "degraded"
    return {"overall": overall, "services": services, "checked_at": datetime.utcnow().isoformat()}


# ─────────────────────────────────────────────
#  Broadcast Announcement (email all users)
# ─────────────────────────────────────────────
class BroadcastRequest(BaseModel):
    subject: str
    message: str
    target_plan: str = "all"  # "all" | "ultimate" | "premium" | "plus" | "essential"


@router.post("/admin/broadcast")
async def admin_broadcast_email(
    req: BroadcastRequest,
    background_tasks: BackgroundTasks,
    _=Depends(_require_admin),
):
    """Send announcement email to all (or filtered) users. Runs in background."""
    background_tasks.add_task(_do_broadcast, req.subject, req.message, req.target_plan)
    return {
        "status": "queued",
        "message": f"Broadcast '{req.subject}' sedang dikirim ke target plan={req.target_plan}",
    }


# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────
async def _log_activity(r: aioredis.Redis, action: str, detail: str):
    entry = json.dumps({
        "action": action,
        "detail": detail,
        "ts":     datetime.utcnow().isoformat(),
    })
    await r.lpush("admin:activity_log", entry)
    await r.ltrim("admin:activity_log", 0, 999)


def _send_support_reply_bg(email, name, subject, original_message, reply, ticket_id):
    try:
        from ...utils.email import send_support_reply_email
        send_support_reply_email(
            to_email=email, user_name=name, original_subject=subject,
            original_message=original_message, ai_reply=reply, ticket_id=ticket_id,
        )
    except Exception as e:
        logger.error(f"Support reply email error: {e}")


async def _do_broadcast(subject: str, message: str, target_plan: str):
    """Background: fetch all users and send email."""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"{AUTH_SERVICE}/v1/admin/users",
                params={"limit": 500},
                headers={"X-Internal-Key": INTERNAL_KEY},
            )
            if resp.status_code != 200:
                return
            users = resp.json().get("users", [])

        r = await _r()
        from ...utils.email import _base_template, _button, send_email

        html = _base_template(
            subject,
            f"""
            <h1 style="color:#E2E8F0;font-size:22px;font-weight:800;margin:0 0 16px;">
              📢 Pengumuman dari Golden AI Strategy
            </h1>
            <div style="background:#111827;border:1px solid rgba(245,166,35,0.2);border-radius:12px;padding:24px;margin:20px 0;">
              <p style="color:#E2E8F0;font-size:14px;line-height:1.8;margin:0;">{message.replace(chr(10), '<br/>')}</p>
            </div>
            {_button("🚀 Buka Platform GAS", SITE_URL)}
            """,
            subject
        )

        count = 0
        for u in users:
            email = u.get("email", "")
            if not email:
                continue
            user_plan = (await r.get(f"user:{u['id']}:plan")) or "free"
            if target_plan != "all" and user_plan != target_plan:
                continue
            send_email(to_email=email, subject=f"📢 {subject}", html_body=html)
            count += 1

        await _log_activity(r, "broadcast_email", f"Sent '{subject}' to {count} users (filter: {target_plan})")
    except Exception as e:
        logger.error(f"Broadcast error: {e}")
