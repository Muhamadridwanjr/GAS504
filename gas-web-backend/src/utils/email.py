"""
GAS Email Service — Brevo SMTP
Beautiful HTML email templates — Light theme, Golden AI Strategy branding.
"""
import smtplib, ssl, os, logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from datetime import datetime

logger = logging.getLogger("gas.email")

SMTP_HOST    = os.getenv("BREVO_SMTP_HOST", "smtp-relay.brevo.com")
SMTP_PORT    = int(os.getenv("BREVO_SMTP_PORT", "587"))
SMTP_USER    = os.getenv("BREVO_SMTP_USER", "a4f504001@smtp-brevo.com")
SMTP_PASS    = os.getenv("BREVO_SMTP_PASS", "xsmtpsib-13d6cd17e0e3dfab1c1774d1768b87cd21a7a74b9f318d116be977b7ac1a3ee6-Cnp0W2QPJQOPqWGi")
FROM_EMAIL   = os.getenv("FROM_EMAIL", "billing@gasstrategyai.xyz")
FROM_NAME    = "Golden AI Strategy"
SUPPORT_EMAIL = "support@gasstrategyai.xyz"
SITE_URL     = os.getenv("SITE_URL", "https://www.gasstrategyai.xyz")
LOGO_URL     = "https://i.ibb.co.com/603h1JF3/photo-2026-01-27-22-14-18.jpg"
GOLD         = "#C9930A"
GOLD_LIGHT   = "#F0AA00"


# ─────────────────────────────────────────────────────────
#  BASE TEMPLATE — Light theme
# ─────────────────────────────────────────────────────────
def _base(title: str, content: str, preheader: str = "") -> str:
    year = datetime.now().year
    return f"""<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
  <title>{title}</title>
</head>
<body style="margin:0;padding:0;background:#F0F2F8;font-family:'Segoe UI',Helvetica,Arial,sans-serif;">
  {f'<div style="display:none;max-height:0;overflow:hidden;font-size:1px;color:#F0F2F8;">{preheader}</div>' if preheader else ''}
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#F0F2F8;">
    <tr><td align="center" style="padding:36px 16px 48px;">
      <table width="580" cellpadding="0" cellspacing="0" style="max-width:580px;width:100%;">

        <!-- ══ HEADER ══ -->
        <tr>
          <td style="background:#FFFFFF;border-radius:16px 16px 0 0;padding:32px 40px 28px;
                     text-align:center;border-bottom:3px solid {GOLD_LIGHT};">
            <table cellpadding="0" cellspacing="0" style="margin:0 auto;">
              <tr>
                <td style="vertical-align:middle;padding-right:12px;">
                  <img src="{LOGO_URL}" width="48" height="48"
                       style="border-radius:10px;display:block;border:2px solid #F0E8C0;"
                       alt="GAS Logo"/>
                </td>
                <td style="vertical-align:middle;text-align:left;">
                  <div style="font-size:20px;font-weight:900;color:#1A1A2E;letter-spacing:2px;line-height:1;">
                    GAS
                  </div>
                  <div style="font-size:9px;color:{GOLD};letter-spacing:3px;font-weight:700;
                               text-transform:uppercase;margin-top:2px;">
                    Golden AI Strategy
                  </div>
                </td>
              </tr>
            </table>
            <div style="margin-top:8px;height:2px;background:linear-gradient(90deg,transparent,{GOLD_LIGHT},transparent);border-radius:2px;"></div>
          </td>
        </tr>

        <!-- ══ BODY ══ -->
        <tr>
          <td style="background:#FFFFFF;padding:36px 40px;">
            {content}
          </td>
        </tr>

        <!-- ══ FOOTER ══ -->
        <tr>
          <td style="background:#F8F8FC;border-radius:0 0 16px 16px;padding:28px 40px;
                     text-align:center;border-top:1px solid #E8E8F0;">
            <table cellpadding="0" cellspacing="0" style="margin:0 auto 14px;">
              <tr>
                <td style="padding:0 6px;">
                  <a href="{SITE_URL}" style="color:{GOLD};text-decoration:none;font-size:12px;font-weight:600;">🌐 gasstrategyai.xyz</a>
                </td>
                <td style="color:#D0D0E0;font-size:12px;">|</td>
                <td style="padding:0 6px;">
                  <a href="mailto:{SUPPORT_EMAIL}" style="color:{GOLD};text-decoration:none;font-size:12px;font-weight:600;">📧 support</a>
                </td>
                <td style="color:#D0D0E0;font-size:12px;">|</td>
                <td style="padding:0 6px;">
                  <a href="https://t.me/gasstrategyai" style="color:{GOLD};text-decoration:none;font-size:12px;font-weight:600;">💬 Telegram</a>
                </td>
              </tr>
            </table>
            <p style="color:#8888A0;font-size:10px;margin:0;line-height:1.7;">
              © {year} Golden AI Strategy · Platform AI Trading Terdepan Indonesia<br/>
              Email otomatis — jangan balas. Butuh bantuan?
              <a href="mailto:{SUPPORT_EMAIL}" style="color:{GOLD};">{SUPPORT_EMAIL}</a>
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""


# ─────────────────────────────────────────────────────────
#  COMPONENTS
# ─────────────────────────────────────────────────────────
def _btn(text: str, url: str, color: str = None) -> str:
    bg = color or GOLD_LIGHT
    return f"""<div style="text-align:center;margin:28px 0 8px;">
      <a href="{url}" style="background:linear-gradient(135deg,{bg},{GOLD});color:#FFFFFF;
         font-weight:800;font-size:14px;padding:14px 40px;border-radius:10px;
         text-decoration:none;display:inline-block;letter-spacing:0.5px;
         box-shadow:0 4px 14px rgba(200,147,10,0.35);">{text}</a>
    </div>"""

def _divider() -> str:
    return '<div style="height:1px;background:#EEF0F8;margin:24px 0;"></div>'

def _badge(text: str, bg: str = "#FFF3CD", color: str = "#8B6400") -> str:
    return (f'<span style="background:{bg};color:{color};padding:3px 12px;border-radius:20px;'
            f'font-size:11px;font-weight:700;letter-spacing:0.5px;">{text}</span>')

def _info_row(label: str, value: str, last: bool = False) -> str:
    border = "" if last else "border-bottom:1px solid #F0F0F8;"
    return f"""<tr>
      <td style="padding:11px 0;{border}color:#6666A0;font-size:13px;">{label}</td>
      <td style="padding:11px 0;{border}text-align:right;color:#1A1A2E;font-size:13px;font-weight:600;">{value}</td>
    </tr>"""

def _card(content: str, bg: str = "#FAFBFF", border: str = "#E8E8F8") -> str:
    return (f'<div style="background:{bg};border:1px solid {border};border-radius:12px;'
            f'padding:22px 24px;margin:20px 0;">{content}</div>')

def _feature_row(emoji: str, title: str, desc: str) -> str:
    return f"""<tr>
      <td width="40" style="vertical-align:top;padding:8px 0;">
        <div style="width:36px;height:36px;background:#FFF8E0;border-radius:10px;
                    text-align:center;line-height:36px;font-size:18px;">{emoji}</div>
      </td>
      <td style="padding:8px 0 8px 12px;vertical-align:top;">
        <div style="font-size:13px;font-weight:700;color:#1A1A2E;">{title}</div>
        <div style="font-size:11px;color:#8888A0;margin-top:2px;">{desc}</div>
      </td>
    </tr>"""


# ─────────────────────────────────────────────────────────
#  1. WELCOME EMAIL
# ─────────────────────────────────────────────────────────
def render_welcome(username: str, full_name: str = "", plan: str = "trial") -> str:
    name = full_name or username
    is_trial = plan in ("trial", "free", "")
    plan_label = "🎁 Trial 3 Hari" if is_trial else plan.capitalize()
    plan_bg    = "#EBF5FF" if is_trial else "#FFF8E0"
    plan_color = "#1A6CBF" if is_trial else "#8B6400"

    # Pre-compute to avoid backslash-in-f-string (Python < 3.12)
    plan_span = (f'<span style="background:{plan_bg};color:{plan_color};padding:2px 10px;'
                 f'border-radius:20px;font-size:11px;font-weight:700;">{plan_label}</span>')
    username_at = f"@{username}"
    trial_card = _card(
        '<div style="display:flex;align-items:center;gap:12px;">'
        '<div style="font-size:28px;">⏳</div>'
        '<div><div style="font-weight:800;color:#1A6CBF;font-size:14px;margin-bottom:3px;">'
        'Trial Aktif — 3 Hari</div>'
        '<div style="color:#6666A0;font-size:12px;line-height:1.6;">'
        'Kamu mendapat <strong style="color:#1A1A2E;">10 Credits</strong> gratis untuk mencoba platform. '
        'Upgrade kapan saja untuk akses penuh 20+ fitur AI trading.</div></div></div>',
        bg="#F0F7FF", border="#C0D8F8"
    ) if is_trial else ""
    account_card = _card(
        '<div style="font-size:11px;font-weight:700;color:#8888A0;letter-spacing:2px;'
        'text-transform:uppercase;margin-bottom:14px;">📋 Informasi Akun</div>'
        '<table width="100%" cellpadding="0" cellspacing="0">'
        + _info_row("Username", username_at)
        + _info_row("Email", "Terverifikasi ✅")
        + _info_row("Plan Aktif", plan_span)
        + _info_row("Credits", "🪙 10 Credits (Trial)", last=True)
        + '</table>'
    )

    content = f"""
    <!-- Hero -->
    <div style="text-align:center;margin-bottom:28px;">
      <div style="font-size:44px;margin-bottom:8px;">🎉</div>
      <h1 style="font-size:26px;font-weight:900;color:#1A1A2E;margin:0 0 6px;">
        Selamat Datang, {name}!
      </h1>
      <p style="color:#6666A0;font-size:14px;margin:0;">
        Akun Golden AI Strategy kamu berhasil dibuat ✅
      </p>
    </div>

    <!-- Account card -->
    {account_card}

    <!-- Trial banner -->
    {trial_card}

    {_divider()}

    <!-- Features grid -->
    <div style="font-size:13px;font-weight:700;color:#1A1A2E;margin-bottom:14px;">
      🚀 Fitur Unggulan GAS Platform:
    </div>
    <table width="100%" cellpadding="0" cellspacing="0">
      {_feature_row("⚡", "Signal AI", "Sinyal trading real-time dengan AI terdepan")}
      {_feature_row("📊", "Technical AI", "SMC, Order Block, BOS/CHOCH, multi-TF")}
      {_feature_row("🧠", "AI Intelligence", "14 tools AI untuk analisis mendalam")}
      {_feature_row("📅", "Economic Calendar", "Kalender ekonomi + dampak pasar AI")}
      {_feature_row("💰", "Risk Manager", "Kelola risiko dengan AI yang cerdas")}
      {_feature_row("🤖", "AI Agent", "Autonomous trading assistant 24/7")}
    </table>

    {_divider()}

    {_btn("🚀 Mulai Trading Sekarang", SITE_URL)}

    <p style="color:#AAAACC;font-size:12px;text-align:center;margin:16px 0 0;line-height:1.7;">
      Pertanyaan? Hubungi kami di
      <a href="mailto:{SUPPORT_EMAIL}" style="color:{GOLD};text-decoration:none;font-weight:600;">{SUPPORT_EMAIL}</a>
      <br/>atau bergabung di komunitas Telegram kami 💬
    </p>"""

    return _base(f"Selamat Datang di GAS, {name}!", content,
                 "Akun kamu berhasil dibuat! Mulai trading cerdas dengan AI.")


# ─────────────────────────────────────────────────────────
#  2. INVOICE EMAIL
# ─────────────────────────────────────────────────────────
def render_invoice(
    username: str,
    order_id: str,
    package_label: str,
    amount_usdt: str,
    wallet_address: str,
    expires_at: str,
    credits: int,
    plan_name: str = "",
) -> str:
    plan_line = (f'<br/><span style="color:#059669;font-weight:700;">Plan: {plan_name.upper()} (30 hari)</span>'
                 if plan_name else "")
    deadline  = expires_at or "1 jam dari sekarang"

    # Pre-compute to avoid backslash-in-f-string
    oid_code   = (f'<code style="background:#F4F4F8;padding:2px 8px;border-radius:6px;'
                  f'font-size:11px;color:{GOLD};">{order_id}</code>')
    cred_line  = f"🪙 {credits} Credits{plan_line}"
    dead_line  = f"⏰ {deadline}"
    order_card = _card(
        '<div style="font-size:11px;font-weight:700;color:#8888A0;letter-spacing:2px;'
        'text-transform:uppercase;margin-bottom:14px;">📋 Detail Pesanan</div>'
        '<table width="100%" cellpadding="0" cellspacing="0">'
        + _info_row("Order ID", oid_code)
        + _info_row("Paket", package_label)
        + _info_row("Credits", cred_line)
        + _info_row("Batas Bayar", dead_line, last=True)
        + '</table>'
    )

    content = f"""
    <!-- Header icon -->
    <div style="text-align:center;margin-bottom:24px;">
      <div style="width:64px;height:64px;background:#FFF8E0;border-radius:16px;
                  border:2px solid #F0D060;display:inline-flex;align-items:center;
                  justify-content:center;font-size:30px;line-height:1;">🧾</div>
      <h1 style="font-size:22px;font-weight:900;color:#1A1A2E;margin:12px 0 4px;">
        Invoice Pembayaran
      </h1>
      <p style="color:#6666A0;font-size:13px;margin:0;">
        Halo <strong style="color:#1A1A2E;">{username}</strong> — selesaikan pembayaran untuk mengaktifkan pesananmu
      </p>
    </div>

    <!-- Order detail -->
    {order_card}

    <!-- Payment box -->
    <div style="background:linear-gradient(135deg,#FFFBF0,#FFF5D0);border:2px solid {GOLD};
                border-radius:16px;padding:32px;margin:20px 0;text-align:center;">
      <div style="font-size:11px;font-weight:800;color:#8B6400;letter-spacing:3px;
                  text-transform:uppercase;margin-bottom:14px;">
        💳 Kirim Tepat Sebesar
      </div>
      <div style="font-size:42px;font-weight:900;color:#8B4A00;line-height:1;margin-bottom:6px;
                  font-family:'Courier New',monospace;">
        {amount_usdt}
        <span style="font-size:20px;color:{GOLD};"> USDT</span>
      </div>
      <div style="font-size:11px;color:#8B6400;margin-bottom:20px;">
        ⚠️ Kirim jumlah <strong>TEPAT</strong> agar terdeteksi otomatis
      </div>

      <div style="background:white;border:1px solid #E8D070;border-radius:10px;
                  padding:16px;text-align:left;margin-bottom:14px;">
        <div style="font-size:10px;font-weight:700;color:#8888A0;letter-spacing:2px;
                    text-transform:uppercase;margin-bottom:8px;">🏦 Wallet Address Tujuan</div>
        <code style="font-size:12px;color:#1A1A2E;word-break:break-all;line-height:1.6;
                     letter-spacing:0.5px;">{wallet_address}</code>
      </div>

      <table cellpadding="0" cellspacing="0" style="margin:0 auto;">
        <tr>
          <td style="padding:0 8px;text-align:center;">
            <span style="font-size:11px;font-weight:700;color:#8B6400;">
              🔗 Network
            </span><br/>
            <span style="font-size:12px;color:#1A1A2E;font-weight:600;">Ethereum (ERC-20)</span>
          </td>
          <td style="padding:0 8px;color:#E0C060;font-size:18px;">|</td>
          <td style="padding:0 8px;text-align:center;">
            <span style="font-size:11px;font-weight:700;color:#8B6400;">🪙 Token</span><br/>
            <span style="font-size:12px;color:#1A1A2E;font-weight:600;">USDT (Tether)</span>
          </td>
        </tr>
      </table>
    </div>

    <!-- After payment info -->
    {_card(f'''
    <div style="font-size:13px;font-weight:700;color:#059669;margin-bottom:10px;">
      ✅ Setelah Pembayaran Berhasil:
    </div>
    <table cellpadding="0" cellspacing="0">
      <tr><td style="padding:4px 0;vertical-align:top;font-size:18px;width:28px;">🤖</td>
          <td style="padding:4px 0;font-size:13px;color:#444466;">Sistem otomatis deteksi dalam <strong>1–5 menit</strong></td></tr>
      <tr><td style="padding:4px 0;font-size:18px;">🪙</td>
          <td style="padding:4px 0;font-size:13px;color:#444466;"><strong>{credits} credits</strong> langsung ditambahkan ke akun kamu{plan_line}</td></tr>
      <tr><td style="padding:4px 0;font-size:18px;">📧</td>
          <td style="padding:4px 0;font-size:13px;color:#444466;">Email konfirmasi + receipt akan dikirim</td></tr>
      <tr><td style="padding:4px 0;font-size:18px;">⚡</td>
          <td style="padding:4px 0;font-size:13px;color:#444466;">Akses semua fitur langsung aktif</td></tr>
    </table>''', bg="#F0FFF8", border="#A8E0C0")}

    <!-- Warning -->
    {_card(f'''
    <div style="font-size:12px;font-weight:700;color:#C0392B;margin-bottom:8px;">⚠️ Perhatian Penting</div>
    <table cellpadding="0" cellspacing="0">
      <tr><td style="padding:3px 0;font-size:12px;color:#555570;">• Gunakan <strong>hanya network Ethereum (ERC-20)</strong> — bukan BSC/TRC20</td></tr>
      <tr><td style="padding:3px 0;font-size:12px;color:#555570;">• Kirim jumlah TEPAT yang tertera: <strong>{amount_usdt} USDT</strong></td></tr>
      <tr><td style="padding:3px 0;font-size:12px;color:#555570;">• Invoice berlaku hingga: <strong style="color:#C0392B;">{deadline}</strong></td></tr>
      <tr><td style="padding:3px 0;font-size:12px;color:#555570;">• Setelah bayar, bisa submit TX hash di dashboard untuk verifikasi cepat</td></tr>
    </table>''', bg="#FFF8F8", border="#F0C0C0")}

    <p style="color:#AAAACC;font-size:12px;text-align:center;margin:20px 0 0;line-height:1.7;">
      Sudah transfer? Buka dashboard dan klik <strong>Verify TX</strong> untuk konfirmasi instan.<br/>
      Ada kendala? Hubungi
      <a href="mailto:{SUPPORT_EMAIL}" style="color:{GOLD};text-decoration:none;font-weight:600;">{SUPPORT_EMAIL}</a>
    </p>"""

    return _base(f"Invoice #{order_id} — Golden AI Strategy", content,
                 f"Kirim {amount_usdt} USDT untuk aktifkan {package_label}")


# ─────────────────────────────────────────────────────────
#  3. PAYMENT CONFIRMATION / RECEIPT
# ─────────────────────────────────────────────────────────

def _build_tx_card(order_id, package_label, amount_usdt, credits_added,
                   new_balance, plan_expires, tx_hash, etherscan, short_tx) -> str:
    """Build transaction summary card avoiding backslash-in-f-string."""
    oid_code      = (f'<code style="background:#F4F4F8;padding:2px 8px;border-radius:6px;'
                     f'font-size:11px;color:{GOLD};">{order_id}</code>')
    amount_strong = f'<strong style="color:#059669;">{amount_usdt} USDT</strong>'
    cred_strong   = f'<strong style="color:#059669;">+{credits_added} 🪙</strong>'
    bal_strong    = f'<strong style="color:{GOLD};">{new_balance} Credits</strong>'
    tx_link       = (f'<a href="{etherscan}" style="color:#2563EB;text-decoration:none;'
                     f'font-family:monospace;font-size:10px;">{short_tx} 🔗</a>') if tx_hash else ""
    eth_div       = (f'<div style="margin-top:12px;text-align:center;">'
                     f'<a href="{etherscan}" style="color:#2563EB;font-size:11px;font-weight:600;'
                     f'text-decoration:none;">🔍 Lihat di Etherscan →</a></div>') if tx_hash else ""

    rows = (
        '<div style="font-size:11px;font-weight:700;color:#8888A0;letter-spacing:2px;'
        'text-transform:uppercase;margin-bottom:14px;">🧾 Ringkasan Transaksi</div>'
        '<table width="100%" cellpadding="0" cellspacing="0">'
        + _info_row("Order ID", oid_code)
        + _info_row("Paket", package_label)
        + _info_row("Jumlah Dibayar", amount_strong)
        + _info_row("Credits Ditambahkan", cred_strong)
        + _info_row("Saldo Credits Sekarang", bal_strong)
        + (_info_row("Langganan Aktif Hingga", plan_expires) if plan_expires else "")
        + (_info_row("TX Hash", tx_link) if tx_hash else "")
        + '</table>' + eth_div
    )
    return _card(rows, bg="#FAFFFE", border="#C0ECD8")
def render_payment_confirmation(
    username: str,
    order_id: str,
    package_label: str,
    amount_usdt: str,
    credits_added: int,
    new_balance: int,
    plan_name: str = "",
    tx_hash: str = "",
    plan_expires: str = "",
) -> str:
    etherscan = f"https://etherscan.io/tx/{tx_hash}" if tx_hash else "#"
    short_tx  = f"{tx_hash[:14]}...{tx_hash[-6:]}" if tx_hash and len(tx_hash) > 20 else tx_hash

    plan_section = ""
    if plan_name:
        expiry_txt = f"Berlaku hingga: <strong>{plan_expires}</strong>" if plan_expires else ""
        plan_color_map = {
            "essential": ("#E8F5FF", "#1560A0", "⚡"),
            "plus":      ("#EFF0FF", "#4B3CB0", "🚀"),
            "premium":   ("#FFF8E0", "#8B6400", "⭐"),
            "ultimate":  ("#F5F0FF", "#6B21A8", "👑"),
            "ultra":     ("#FFF0F3", "#9B1C3A", "🤖"),
        }
        pbg, ptxt, pem = plan_color_map.get(plan_name.lower(), ("#F0F8FF", "#1A4060", "🎯"))
        # Pre-compute expiry div to avoid backslash-in-f-string
        expiry_div = (f'<div style="font-size:11px;font-weight:700;background:white;display:inline-block;'
                      f'padding:4px 14px;border-radius:20px;color:{ptxt};">📅 {expiry_txt}</div>'
                      if plan_expires else "")
        plan_section = f"""
        <div style="background:{pbg};border:2px solid {ptxt}33;border-radius:14px;
                    padding:24px;text-align:center;margin:24px 0;">
          <div style="font-size:36px;margin-bottom:8px;">{pem}</div>
          <div style="font-size:11px;font-weight:800;color:{ptxt};letter-spacing:3px;
                      text-transform:uppercase;margin-bottom:6px;">Plan Baru Diaktifkan</div>
          <div style="font-size:28px;font-weight:900;color:{ptxt};margin-bottom:6px;">
            {plan_name.upper()}
          </div>
          <div style="font-size:12px;color:#6666A0;margin-bottom:8px;">
            Semua fitur plan {plan_name.capitalize()} kini aktif untuk kamu
          </div>
          {expiry_div}
        </div>"""

    content = f"""
    <!-- Success hero -->
    <div style="background:linear-gradient(135deg,#F0FFF8,#E0FAF0);border:2px solid #A0E0C0;
                border-radius:16px;padding:32px;text-align:center;margin-bottom:24px;">
      <div style="font-size:48px;margin-bottom:10px;">✅</div>
      <h1 style="font-size:24px;font-weight:900;color:#0A6640;margin:0 0 8px;">
        Pembayaran Berhasil!
      </h1>
      <p style="color:#3A8060;font-size:14px;margin:0;">
        Terima kasih, <strong>{username}</strong>! Transaksi kamu telah dikonfirmasi oleh sistem GAS.
      </p>
    </div>

    {plan_section}

    <!-- Transaction summary -->
    {_build_tx_card(order_id, package_label, amount_usdt, credits_added, new_balance, plan_expires, tx_hash, etherscan, short_tx)}

    <!-- Credits info -->
    <div style="background:#FFFBF0;border:1px solid #F0D060;border-radius:12px;
                padding:20px;margin:20px 0;text-align:center;">
      <div style="font-size:36px;margin-bottom:6px;">🪙</div>
      <div style="font-size:32px;font-weight:900;color:{GOLD};">{new_balance}</div>
      <div style="font-size:11px;font-weight:700;color:#8B6400;letter-spacing:1px;
                  text-transform:uppercase;margin-top:4px;">Credits Available</div>
      <div style="font-size:12px;color:#8B8060;margin-top:8px;">
        Gunakan untuk mengakses <strong>20+ fitur AI trading</strong> di platform GAS
      </div>
    </div>

    <!-- Tips -->
    {_card(f'''
    <div style="font-size:13px;font-weight:700;color:#1A1A2E;margin-bottom:12px;">💡 Tips Mulai Trading:</div>
    <table cellpadding="0" cellspacing="0">
      <tr><td style="padding:4px 0;font-size:18px;width:28px;">⚡</td>
          <td style="padding:4px 0;font-size:13px;color:#444466;">Mulai dengan <strong>Signal AI</strong> untuk sinyal trading langsung</td></tr>
      <tr><td style="padding:4px 0;font-size:18px;">📊</td>
          <td style="padding:4px 0;font-size:13px;color:#444466;">Gunakan <strong>Technical AI</strong> untuk analisis SMC mendalam</td></tr>
      <tr><td style="padding:4px 0;font-size:18px;">🧠</td>
          <td style="padding:4px 0;font-size:13px;color:#444466;">Setiap penggunaan AI memberikan XP untuk naik level</td></tr>
      <tr><td style="padding:4px 0;font-size:18px;">🏆</td>
          <td style="padding:4px 0;font-size:13px;color:#444466;">Beli Booster untuk +XP & badge eksklusif</td></tr>
    </table>''')}

    {_btn("🚀 Buka Dashboard Sekarang", SITE_URL, "#059669")}

    <p style="color:#AAAACC;font-size:11px;text-align:center;margin:16px 0 0;line-height:1.7;">
      Simpan email ini sebagai bukti pembayaran anda.<br/>
      Pertanyaan? Email kami di
      <a href="mailto:{SUPPORT_EMAIL}" style="color:{GOLD};text-decoration:none;font-weight:600;">{SUPPORT_EMAIL}</a>
    </p>"""

    return _base(f"Pembayaran Dikonfirmasi — {package_label}", content,
                 f"+{credits_added} credits berhasil ditambahkan ke akun kamu!")


# ─────────────────────────────────────────────────────────
#  4. PASSWORD RESET
# ─────────────────────────────────────────────────────────
def render_password_reset(username: str, reset_token: str, reset_url: str) -> str:
    content = f"""
    <div style="text-align:center;margin-bottom:24px;">
      <div style="font-size:44px;">🔐</div>
      <h1 style="font-size:22px;font-weight:900;color:#1A1A2E;margin:10px 0 6px;">Reset Password</h1>
      <p style="color:#6666A0;font-size:13px;margin:0;">
        Halo <strong style="color:#1A1A2E;">{username}</strong>, kami menerima permintaan reset password akun kamu.
      </p>
    </div>
    {_btn("🔑 Reset Password Saya", reset_url)}
    {_card(f'''
    <div style="font-size:12px;font-weight:700;color:#C0392B;margin-bottom:8px;">⚠️ Informasi Penting</div>
    <table cellpadding="0" cellspacing="0">
      <tr><td style="padding:3px 0;font-size:12px;color:#555570;">• Link berlaku <strong>30 menit</strong> setelah email ini diterima</td></tr>
      <tr><td style="padding:3px 0;font-size:12px;color:#555570;">• Jika tidak meminta reset, abaikan email ini</td></tr>
      <tr><td style="padding:3px 0;font-size:12px;color:#555570;">• Jangan bagikan link ini ke siapapun</td></tr>
    </table>''', bg="#FFF8F8", border="#F0C0C0")}
    <p style="color:#AAAACC;font-size:11px;text-align:center;margin:16px 0 0;line-height:1.7;">
      Jika tombol tidak berfungsi, copy link ini ke browser:<br/>
      <a href="{reset_url}" style="color:{GOLD};font-size:10px;word-break:break-all;">{reset_url}</a>
    </p>"""
    return _base("Reset Password — Golden AI Strategy", content, "Reset password akun Golden AI Strategy kamu.")


# ─────────────────────────────────────────────────────────
#  5. SUPPORT REPLY
# ─────────────────────────────────────────────────────────
def render_support_reply(
    user_name: str, user_email: str, original_subject: str,
    original_message: str, ai_reply: str, ticket_id: str = ""
) -> str:
    ticket_lbl = f" #{ticket_id}" if ticket_id else ""
    reply_html = ai_reply.replace("\n", "<br/>")
    content = f"""
    <div style="text-align:center;margin-bottom:24px;">
      <div style="font-size:36px;">💬</div>
      <h1 style="font-size:20px;font-weight:900;color:#1A1A2E;margin:10px 0 4px;">
        Balasan Support GAS
      </h1>
      <p style="color:#6666A0;font-size:12px;margin:0;">Tiket{ticket_lbl} · Re: {original_subject}</p>
    </div>
    <p style="color:#444466;font-size:14px;line-height:1.7;margin:0 0 20px;">
      Halo <strong style="color:#1A1A2E;">{user_name}</strong>, berikut jawaban untuk pertanyaan kamu:
    </p>
    <div style="background:#FAFBFF;border-left:4px solid {GOLD_LIGHT};border-radius:0 12px 12px 0;
                padding:24px;margin:0 0 20px;">
      <div style="margin-bottom:10px;">{_badge("BALASAN GAS AI SUPPORT", "#FFF8E0", "#8B6400")}</div>
      <p style="color:#1A1A2E;font-size:14px;line-height:1.8;margin:0;">{reply_html}</p>
      <p style="color:#AAAACC;font-size:11px;margin:16px 0 0;font-style:italic;">— Tim Support Golden AI Strategy</p>
    </div>
    {_card(f'''
    <div style="font-size:11px;font-weight:700;color:#8888A0;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;">Pesan Asli Kamu:</div>
    <p style="color:#6666A0;font-size:13px;line-height:1.6;margin:0;font-style:italic;">
      "{original_message[:300]}{"..." if len(original_message) > 300 else ""}"
    </p>''', bg="#F8F8FC", border="#E8E8F0")}
    {_btn("📊 Buka Dashboard", SITE_URL)}"""
    return _base(f"Re: {original_subject} — GAS Support", content,
                 f"Jawaban untuk: {original_subject}")


# ─────────────────────────────────────────────────────────
#  SEND HELPERS
# ─────────────────────────────────────────────────────────
def send_email(
    to_email: str, subject: str, html_body: str,
    from_email: str = None, from_name: str = None, reply_to: str = None
) -> bool:
    _from = from_email or FROM_EMAIL
    _name = from_name or FROM_NAME
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = formataddr((_name, _from))
    msg["To"]      = to_email
    if reply_to:
        msg["Reply-To"] = reply_to
    msg.attach(MIMEText("Email ini memerlukan HTML client.", "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))
    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
            s.ehlo(); s.starttls(context=ctx); s.login(SMTP_USER, SMTP_PASS)
            s.sendmail(_from, [to_email], msg.as_string())
        logger.info(f"Email sent → {to_email}")
        return True
    except Exception as e:
        logger.error(f"Email failed → {to_email}: {e}")
        return False


def send_welcome_email(to_email: str, username: str, full_name: str = "", plan: str = "trial") -> bool:
    html = render_welcome(username, full_name, plan)
    return send_email(to_email, f"🎉 Selamat Datang di Golden AI Strategy, {full_name or username}!",
                      html, from_name="Golden AI Strategy")


def send_invoice_email(
    to_email: str, username: str, order_id: str, package_label: str,
    amount_usdt: str, wallet_address: str, expires_at: str, credits: int, plan_name: str = ""
) -> bool:
    html = render_invoice(username, order_id, package_label, amount_usdt,
                          wallet_address, expires_at, credits, plan_name)
    return send_email(to_email, f"🧾 Invoice #{order_id} — {amount_usdt} USDT — GAS",
                      html, from_name="GAS Billing")


def send_payment_confirmation_email(
    to_email: str, username: str, order_id: str, package_label: str,
    amount_usdt: str, credits_added: int, new_balance: int,
    plan_name: str = "", tx_hash: str = "", plan_expires: str = ""
) -> bool:
    html = render_payment_confirmation(username, order_id, package_label, amount_usdt,
                                       credits_added, new_balance, plan_name, tx_hash, plan_expires)
    return send_email(to_email, f"✅ Pembayaran Dikonfirmasi — {package_label} — GAS",
                      html, from_name="GAS Billing")


def send_password_reset_email(to_email: str, username: str, reset_token: str, reset_url: str) -> bool:
    html = render_password_reset(username, reset_token, reset_url)
    return send_email(to_email, "🔐 Reset Password — Golden AI Strategy",
                      html, from_name="GAS Security")


def send_support_reply_email(
    to_email: str, user_name: str, original_subject: str,
    original_message: str, ai_reply: str, ticket_id: str = ""
) -> bool:
    html = render_support_reply(user_name, to_email, original_subject,
                                original_message, ai_reply, ticket_id)
    return send_email(to_email, f"Re: {original_subject} — GAS Support",
                      html, from_email="support@gasstrategyai.xyz",
                      from_name="GAS Support Team", reply_to="support@gasstrategyai.xyz")
