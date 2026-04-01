"""
GAS Bot — Trading Style Keyboard (plan-aware)
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from src.config import get_plan_cfg

STYLES = [
    ("scalping",  "⚡ Scalping",    "M1 · M5 · M15"),
    ("intraday",  "🌅 Day Trading", "M15 · H1 · H4"),
    ("swing",     "🌊 Swing",       "H4 · D1"),
    ("position",  "🏔 Position",    "D1 · W1"),
]

STYLE_LABELS = {
    "scalping":  "⚡ Scalping \\(M1–M15\\)",
    "intraday":  "🌅 Day Trading \\(M15–H1\\)",
    "swing":     "🌊 Swing \\(H4–D1\\)",
    "position":  "🏔 Position \\(D1–W1\\)",
}


def style_keyboard(pair: str, flow_type: str = "analysis", plan: str = "free") -> InlineKeyboardMarkup:
    cfg = get_plan_cfg(plan)
    allowed_styles = cfg.get("styles", set(s[0] for s in STYLES))
    buttons = []
    for style_id, label, tf in STYLES:
        locked = style_id not in allowed_styles
        btn_text = f"🔒 {label}  ·  {tf}" if locked else f"{label}  ·  {tf}"
        buttons.append([
            InlineKeyboardButton(
                btn_text,
                callback_data=f"style_{flow_type}_{style_id}_{pair}",
            )
        ])
    buttons.append([InlineKeyboardButton("🔙 Pilih Pair", callback_data=f"nav_pairs_{flow_type}")])
    return InlineKeyboardMarkup(buttons)


def confirm_analysis_keyboard(pair: str, style: str, cost: int, flow_type: str = "signal") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                f"✅ Mulai  (−{cost} cr)",
                callback_data=f"exec_{flow_type}_{pair}_{style}",
            ),
            InlineKeyboardButton("❌ Batal", callback_data=f"nav_market_{flow_type}"),
        ]
    ])
