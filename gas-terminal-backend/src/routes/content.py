"""
Content routes — serve markdown template files as parsed JSON.
Endpoints:
  GET  /terminal/livenews        → parse livenews.md → list of news items
  GET  /terminal/breakingnews    → parse breakingnews.md → list of breaking items
  GET  /terminal/fundamental-md  → serve fundamental.md raw text
  GET  /terminal/content/{file}  → raw file content (editor)
  POST /terminal/content/{file}  → save file content (editor, token-auth)
"""
import os
import re
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel

router = APIRouter()

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
WIB = timezone(timedelta(hours=7))

# Simple token for editor — set via env or use default
EDITOR_TOKEN = os.getenv("EDITOR_TOKEN", "gas-editor-2026")

ALLOWED_FILES = {"livenews.md", "breakingnews.md", "fundamental.md", "sessions.md", "analysis.md", "announcement.md"}


class ContentBody(BaseModel):
    content: str


def _read_file(filename: str) -> str:
    path = os.path.join(DATA_DIR, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def _impact_from_emoji(title: str) -> str:
    """Detect impact level from leading emoji in title."""
    t = title.strip()
    if t.startswith("🔴") or t.startswith("🔥"):
        return "HIGH"
    if t.startswith("🟠") or t.startswith("🟡"):
        return "MEDIUM"
    return "LOW"


def _parse_livenews(content: str) -> list[dict]:
    """
    Parse livenews.md lines.
    Accepts formats:
      · [HH:MM] 🔴 Title | Source
      · [HH:MM] Title | Source | IMPACT
      - [HH:MM] Title | Source
    Impact auto-detected from emoji prefix (🔴=HIGH, 🟠/🟡=MEDIUM, ⚪=LOW).
    """
    items = []
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("<!--") or line.startswith("#"):
            continue
        # Strip bullet markers: · - * •
        for bullet in ("· ", "- ", "* ", "• "):
            if line.startswith(bullet):
                line = line[len(bullet):].strip()
                break
        # Must have a time tag [HH:MM]
        time_match = re.match(r"\[(\d{1,2}:\d{2})\]\s*(.*)", line)
        if not time_match:
            continue
        time_str, rest = time_match.group(1).zfill(5), time_match.group(2).strip()
        # Remove bold markers **...**
        rest = re.sub(r"\*\*(.*?)\*\*", r"\1", rest)
        parts = [p.strip() for p in rest.split("|")]
        title  = parts[0] if len(parts) > 0 else rest
        source = parts[1] if len(parts) > 1 else "GAS"
        # Impact: explicit 3rd segment > emoji prefix
        if len(parts) > 2 and parts[2].upper() in ("HIGH", "MEDIUM", "LOW", "URGENT"):
            impact = parts[2].upper()
        else:
            impact = _impact_from_emoji(title)
        items.append({
            "time":   time_str,
            "title":  title,
            "source": source.strip(),
            "impact": impact,
        })
    return items


def _parse_breakingnews(content: str) -> list[dict]:
    """
    Parse breakingnews.md. Accepts multiple formats:
      🔴 [URGENT] Text | Source
      · [URGENT] Text | Source
      - [HIGH] Text | Source
      [BREAKING] Text | Source
    """
    items = []
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("<!--") or line.startswith("#"):
            continue
        # Strip bullet markers
        for bullet in ("· ", "- ", "* ", "• "):
            if line.startswith(bullet):
                line = line[len(bullet):].strip()
                break
        # Strip leading emoji (🔴 🟠 🟡 🔵 etc.) before the tag
        line = re.sub(r"^[\U0001F7E0-\U0001F7EF\U0001F534\U0001F535\U0001F7E1\U0001F7E2\U0001F7E3\U0001F7E4\U0001F7E5\U0001F7E6\U0001F7E7\U0001F7E8\U0001F7E9\u26AA\u26AB\u2B55\U0001F504]\s*", "", line).strip()
        # Match [TAG] pattern
        tag_match = re.match(r"\[(URGENT|HIGH|MEDIUM|BREAKING|FLASH)\]\s*(.*)", line, re.IGNORECASE)
        if not tag_match:
            continue
        tag, rest = tag_match.group(1).upper(), tag_match.group(2).strip()
        # Normalize tag
        if tag == "FLASH":
            tag = "URGENT"
        parts = [p.strip() for p in rest.split("|")]
        text   = parts[0] if parts else rest
        source = parts[1] if len(parts) > 1 else ""
        if text:
            items.append({"tag": tag, "text": text, "source": source})
    return items


@router.get("/terminal/livenews")
async def get_livenews():
    """Return parsed livenews.md as JSON list."""
    content = _read_file("livenews.md")
    items = _parse_livenews(content)
    now_wib = datetime.now(WIB).strftime("%H:%M WIB")
    return {
        "status": "ok",
        "count":  len(items),
        "updated_at": now_wib,
        "news": items,
    }


@router.get("/terminal/breakingnews")
async def get_breakingnews():
    """Return parsed breakingnews.md. Empty list = no breaking news active."""
    content = _read_file("breakingnews.md")
    items = _parse_breakingnews(content)
    return {
        "status":  "ok",
        "active":  len(items) > 0,
        "items":   items,
    }


@router.get("/terminal/fundamental-md")
async def get_fundamental_md():
    """Return fundamental.md as raw markdown text."""
    content = _read_file("fundamental.md")
    return {"status": "ok", "content": content}


# ── Editor endpoints ─────────────────────────────────────────────────

@router.get("/terminal/content/{filename}")
async def get_content_raw(filename: str):
    """Return raw file content for the editor."""
    if filename not in ALLOWED_FILES:
        raise HTTPException(404, f"File not found: {filename}")
    return {"status": "ok", "filename": filename, "content": _read_file(filename)}


@router.post("/terminal/content/{filename}")
async def save_content(filename: str, body: ContentBody, x_editor_token: str = Header(None)):
    """Save raw file content. Requires X-Editor-Token header."""
    if x_editor_token != EDITOR_TOKEN:
        raise HTTPException(401, "Invalid editor token")
    if filename not in ALLOWED_FILES:
        raise HTTPException(404, f"File not allowed: {filename}")
    path = os.path.join(DATA_DIR, filename)
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(body.content)
        return {"status": "ok", "filename": filename, "saved": True}
    except Exception as e:
        raise HTTPException(500, f"Failed to save: {e}")
