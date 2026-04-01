"""
GAS Support System — AI-powered customer support with email auto-reply.
Uses Anthropic Claude to generate professional Indonesian support responses.
"""
import json
import logging
import os
import time
import uuid
from typing import Optional

import httpx
import redis.asyncio as aioredis
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, EmailStr

from ...core.dependencies import get_current_user_info

logger = logging.getLogger("gas.support")

router = APIRouter(tags=["Support"])

KIMI_API_KEY   = os.getenv("KIMI_API_KEY_SUPPORT", "sk-oqNrlbAvX2K0027o31RaokOZtbAdX2oyIepS2ixCClrLyH10")
KIMI_BASE_URL  = "https://api.moonshot.cn/v1"
KIMI_MODEL     = "moonshot-v1-8k"
REDIS_URL         = os.getenv("REDIS_URL", "redis://gas-redis:6379/0")
SITE_URL          = os.getenv("SITE_URL", "https://www.gasstrategyai.xyz")

_redis_client: Optional[aioredis.Redis] = None


async def _get_redis() -> aioredis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)
    return _redis_client


# ─────────────────────────────────────────────
#  Knowledge Base untuk AI Support
# ─────────────────────────────────────────────
GAS_KNOWLEDGE = """
Golden AI Strategy (GAS) adalah platform AI trading terdepan untuk trader Indonesia.

PLANS & HARGA (Pembayaran USDT ERC-20):
- Essential: $2.99/bulan → 100 credits, akses: Technical AI, Signal AI, Alert, Session
- Plus: $5.99/bulan → 200 credits, + Correlation, Fundamental, Calendar, Sentiment, Risk Manager
- Premium: $11.99/bulan → 400 credits, + Hybrid System, Drawdown Recovery, Market Briefing, Psychology Coach, Journal, Prop Firm
- Ultimate: $19.99/bulan → 700 credits, + Scanner (15cr), Backtesting (20cr), AI Mentor (10cr)

TOP-UP CREDITS:
- 50 Credits: $0.99 USDT
- 150 Credits: $2.49 USDT
- 500 Credits: $6.99 USDT

BOOSTER PACKS:
- Bronze: $1.99 USDT → +50 credits + XP bonus
- Silver: $4.99 USDT → +150 credits + XP bonus
- Gold: $9.99 USDT → +350 credits + XP bonus

CARA BAYAR:
1. Masuk ke dashboard → klik upgrade plan atau top-up
2. Salin wallet address: 0xf8ef68F41B609B06210ebe7d045FA111F2034518
3. Kirim TEPAT jumlah USDT yang tertera (via Ethereum ERC-20 network)
4. Sistem otomatis verifikasi dalam 1-5 menit
5. Submit TX hash di dashboard untuk verifikasi lebih cepat

18 FITUR AI:
Technical AI, Signal AI, Smart Alert, Session Optimizer, Correlation Tracker,
Fundamental Analysis AI, Economic Calendar AI, Sentiment Market AI, Risk Manager AI,
Hybrid System AI, Drawdown Recovery, AI Market Briefing, Psychology Coach AI,
AI Trade Journal, Prop Firm Assistant, Multi-Symbol Scanner, AI Backtesting Engine, AI Mentor Mode

SISTEM KREDIT & LEVEL:
- Setiap penggunaan fitur mengurangi credits
- XP diperoleh dari penggunaan fitur
- Level 1-20 dengan reward XP
- Booster pack menambah XP dan credits sekaligus

KONTAK:
- Support: support@gasstrategyai.xyz
- Billing: billing@gasstrategyai.xyz
- Website: https://www.gasstrategyai.xyz
"""

SYSTEM_PROMPT = f"""Kamu adalah AI Customer Support untuk Golden AI Strategy (GAS) — platform AI trading.
Kamu berbicara dalam Bahasa Indonesia yang profesional, ramah, dan membantu.
Berikan jawaban yang akurat, ringkas (maks 3-4 paragraf), dan solusi yang actionable.
Selalu akhiri dengan menawarkan bantuan lebih lanjut.

PENGETAHUAN PRODUK:
{GAS_KNOWLEDGE}

ATURAN:
- Gunakan Bahasa Indonesia formal namun ramah
- Jangan menyebutkan kompetitor
- Jika pertanyaan di luar scope GAS, arahkan ke support@gasstrategyai.xyz
- Selalu professional dan positif
- Format: paragraf biasa, bukan bullet list panjang (kecuali perlu)
"""


# ─────────────────────────────────────────────
#  Schemas
# ─────────────────────────────────────────────
class ContactRequest(BaseModel):
    name: str
    email: str
    subject: str
    message: str


class SupportReplyRequest(BaseModel):
    ticket_id: str
    reply_message: str


# ─────────────────────────────────────────────
#  AI Reply Generator
# ─────────────────────────────────────────────
async def _generate_ai_reply(subject: str, message: str) -> str:
    """Call Kimi AI (Moonshot) to generate support reply in Indonesian."""
    user_msg = f"Subjek: {subject}\n\nPesan dari pelanggan:\n{message}"

    payload = {
        "model":      KIMI_MODEL,
        "max_tokens": 1024,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_msg},
        ],
    }
    headers = {
        "Authorization": f"Bearer {KIMI_API_KEY}",
        "Content-Type":  "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{KIMI_BASE_URL}/chat/completions",
                json=payload,
                headers=headers,
            )
            data = resp.json()
            if resp.status_code == 200:
                choices = data.get("choices", [])
                if choices:
                    return choices[0]["message"]["content"]
    except Exception as e:
        logger.error(f"Kimi AI error: {e}")

    return (
        "Terima kasih telah menghubungi Golden AI Strategy! "
        "Tim support kami telah menerima pesan Anda dan akan membalas dalam 1x24 jam. "
        "Untuk pertanyaan mendesak, silakan kirim email ke support@gasstrategyai.xyz.\n\n"
        "Salam hangat,\nTim Support Golden AI Strategy"
    )


# ─────────────────────────────────────────────
#  Endpoints
# ─────────────────────────────────────────────
@router.post("/support/contact")
async def submit_support_ticket(
    req: ContactRequest,
    background_tasks: BackgroundTasks,
):
    """
    Submit a support ticket. AI reply is generated and emailed automatically.
    No auth required — anyone can contact support.
    """
    ticket_id = f"TKT-{int(time.time())}-{uuid.uuid4().hex[:6].upper()}"

    # Store ticket in Redis
    r = await _get_redis()
    ticket = {
        "ticket_id": ticket_id,
        "name":      req.name,
        "email":     req.email,
        "subject":   req.subject,
        "message":   req.message,
        "status":    "open",
        "created_at": time.time(),
    }
    await r.set(f"support:ticket:{ticket_id}", json.dumps(ticket), ex=86400 * 90)
    await r.lpush("support:ticket_list", ticket_id)
    await r.ltrim("support:ticket_list", 0, 999)

    # Generate AI reply and send email in background
    background_tasks.add_task(
        _process_support_ticket_bg,
        ticket_id, req.name, req.email, req.subject, req.message, r
    )

    return {
        "status":    "submitted",
        "ticket_id": ticket_id,
        "message":   (
            f"Tiket support #{ticket_id} berhasil dikirim! "
            "Balasan otomatis akan dikirim ke email Anda dalam beberapa menit. "
            "Tim kami juga akan follow-up jika diperlukan."
        ),
    }


@router.get("/support/ticket/{ticket_id}")
async def get_ticket_status(
    ticket_id: str,
    user_info: dict = Depends(get_current_user_info),
):
    """Get support ticket status (authenticated users only)."""
    r = await _get_redis()
    raw = await r.get(f"support:ticket:{ticket_id}")
    if not raw:
        raise HTTPException(status_code=404, detail="Tiket tidak ditemukan")
    ticket = json.loads(raw)
    return ticket


@router.get("/support/tickets")
async def list_tickets(user_info: dict = Depends(get_current_user_info)):
    """Admin: list all support tickets."""
    if not user_info["is_admin"]:
        raise HTTPException(status_code=403, detail="Hanya admin yang bisa melihat semua tiket")
    r = await _get_redis()
    ticket_ids = await r.lrange("support:ticket_list", 0, 49)
    tickets = []
    for tid in ticket_ids:
        raw = await r.get(f"support:ticket:{tid}")
        if raw:
            tickets.append(json.loads(raw))
    return {"tickets": tickets, "total": len(tickets)}


@router.post("/support/reply/{ticket_id}")
async def admin_reply_ticket(
    ticket_id: str,
    req: SupportReplyRequest,
    background_tasks: BackgroundTasks,
    user_info: dict = Depends(get_current_user_info),
):
    """Admin: manually reply to a support ticket and email the user."""
    if not user_info["is_admin"]:
        raise HTTPException(status_code=403, detail="Hanya admin yang bisa membalas tiket")

    r = await _get_redis()
    raw = await r.get(f"support:ticket:{ticket_id}")
    if not raw:
        raise HTTPException(status_code=404, detail="Tiket tidak ditemukan")

    ticket = json.loads(raw)
    ticket["status"] = "replied"
    ticket["reply"]  = req.reply_message
    ticket["replied_at"] = time.time()
    await r.set(f"support:ticket:{ticket_id}", json.dumps(ticket), ex=86400 * 90)

    background_tasks.add_task(
        _send_support_reply_bg,
        ticket["email"], ticket["name"], ticket["subject"],
        ticket["message"], req.reply_message, ticket_id
    )

    return {"status": "ok", "message": f"Balasan dikirim ke {ticket['email']}"}


# ─────────────────────────────────────────────
#  Background helpers
# ─────────────────────────────────────────────
async def _process_support_ticket_bg(
    ticket_id: str,
    name: str,
    email: str,
    subject: str,
    message: str,
    r: aioredis.Redis,
):
    """Generate AI reply and send email for a support ticket."""
    try:
        ai_reply = await _generate_ai_reply(subject, message)

        # Update ticket with AI reply
        raw = await r.get(f"support:ticket:{ticket_id}")
        if raw:
            ticket = json.loads(raw)
            ticket["ai_reply"]    = ai_reply
            ticket["ai_replied_at"] = time.time()
            ticket["status"]      = "ai_replied"
            await r.set(f"support:ticket:{ticket_id}", json.dumps(ticket), ex=86400 * 90)

        # Send email reply
        _send_support_reply_bg(email, name, subject, message, ai_reply, ticket_id)

    except Exception as e:
        logger.error(f"Support ticket processing error: {e}")


def _send_support_reply_bg(
    email: str, name: str, subject: str,
    original_message: str, reply: str, ticket_id: str
):
    try:
        from ...utils.email import send_support_reply_email
        send_support_reply_email(
            to_email=email,
            user_name=name,
            original_subject=subject,
            original_message=original_message,
            ai_reply=reply,
            ticket_id=ticket_id,
        )
    except Exception as e:
        logger.error(f"Support reply email error: {e}")
