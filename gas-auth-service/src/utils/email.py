"""
GAS Email Utility — Auth service.
Sends OTP and welcome emails via Brevo SMTP.
Light theme, real GAS logo, professional format.
"""
import smtplib
import ssl
import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from datetime import datetime

logger = logging.getLogger("gas.auth.email")

SMTP_HOST = os.getenv("BREVO_SMTP_HOST", "smtp-relay.brevo.com")
SMTP_PORT = int(os.getenv("BREVO_SMTP_PORT", "587"))
SMTP_USER = os.getenv("BREVO_SMTP_USER", "a4f504001@smtp-brevo.com")
SMTP_PASS = os.getenv("BREVO_SMTP_PASS", "xsmtpsib-13d6cd17e0e3dfab1c1774d1768b87cd21a7a74b9f318d116be977b7ac1a3ee6-Cnp0W2QPJQOPqWGi")
FROM_EMAIL = os.getenv("FROM_EMAIL", "billing@gasstrategyai.xyz")
SUPPORT_EMAIL = "support@gasstrategyai.xyz"
SITE_URL = os.getenv("SITE_URL", "https://www.gasstrategyai.xyz")
LOGO_URL = "https://i.ibb.co.com/603h1JF3/photo-2026-01-27-22-14-18.jpg"

# ── Colours (light theme) ──────────────────────────────────────────────────
C_BG      = "#F0F2F8"
C_CARD    = "#FFFFFF"
C_HEADER  = "#FDFAF2"
C_BORDER  = "#E8D9A0"
C_GOLD    = "#C9930A"
C_GOLD2   = "#F0AA00"
C_TEXT    = "#1A1A2E"
C_MUTED   = "#6B7280"
C_LIGHT   = "#9CA3AF"
C_GREEN   = "#059669"
C_RED     = "#DC2626"
C_BLUE    = "#1D4ED8"
C_INFO_BG = "#EFF6FF"
C_INFO_BD = "#BFDBFE"
C_WARN_BG = "#FEF9C3"
C_WARN_BD = "#FDE047"
C_ERR_BG  = "#FEF2F2"
C_ERR_BD  = "#FECACA"


def _base(title: str, content: str) -> str:
    year = datetime.now().year
    return f"""<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
  <title>{title}</title>
</head>
<body style="margin:0;padding:0;background:{C_BG};font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:{C_BG};min-height:100vh;">
    <tr><td align="center" style="padding:40px 16px;">
      <table width="600" cellpadding="0" cellspacing="0"
             style="max-width:600px;width:100%;border-radius:16px;overflow:hidden;
                    box-shadow:0 4px 24px rgba(0,0,0,0.10);">

        <!-- ── HEADER ── -->
        <tr><td style="background:{C_HEADER};border-radius:16px 16px 0 0;
                        padding:32px 40px 24px;text-align:center;
                        border:1.5px solid {C_BORDER};border-bottom:none;">
          <table align="center" cellpadding="0" cellspacing="0">
            <tr>
              <td style="padding-right:14px;vertical-align:middle;">
                <img src="{LOGO_URL}" width="52" height="52" alt="GAS"
                     style="border-radius:10px;border:2px solid {C_GOLD};display:block;"/>
              </td>
              <td style="vertical-align:middle;text-align:left;">
                <div style="font-size:22px;font-weight:900;color:{C_GOLD};letter-spacing:2px;line-height:1;">GAS</div>
                <div style="font-size:10px;color:{C_MUTED};letter-spacing:3px;font-weight:600;
                             text-transform:uppercase;margin-top:3px;">Golden AI Strategy</div>
              </td>
            </tr>
          </table>
        </td></tr>

        <!-- ── GOLD DIVIDER ── -->
        <tr><td style="background:linear-gradient(90deg,{C_BORDER},{C_GOLD2},{C_BORDER});height:2px;"></td></tr>

        <!-- ── BODY ── -->
        <tr><td style="background:{C_CARD};padding:40px 40px 32px;
                        border:1.5px solid {C_BORDER};border-top:none;border-bottom:none;">
          {content}
        </td></tr>

        <!-- ── FOOTER ── -->
        <tr><td style="background:{C_HEADER};border-radius:0 0 16px 16px;
                        padding:24px 40px;text-align:center;
                        border:1.5px solid {C_BORDER};border-top:1.5px solid {C_BORDER};">
          <p style="color:{C_GOLD};font-size:13px;font-weight:700;margin:0 0 4px;">Golden AI Strategy</p>
          <p style="color:{C_MUTED};font-size:11px;margin:0 0 12px;">Platform AI Trading Terdepan Indonesia 🇮🇩</p>
          <p style="margin:0 0 8px;">
            <a href="{SITE_URL}" style="color:{C_GOLD};text-decoration:none;font-size:12px;font-weight:600;">
              🌐 gasstrategyai.xyz
            </a>
            &nbsp;&nbsp;·&nbsp;&nbsp;
            <a href="mailto:{SUPPORT_EMAIL}"
               style="color:{C_GOLD};text-decoration:none;font-size:12px;font-weight:600;">
              📧 support@gasstrategyai.xyz
            </a>
          </p>
          <p style="color:{C_LIGHT};font-size:10px;margin:0;">© {year} Golden AI Strategy. All rights reserved.</p>
        </td></tr>

      </table>
    </td></tr>
  </table>
</body></html>"""


def _btn(text: str, url: str, bg: str = None) -> str:
    bg = bg or C_GOLD
    return f"""<div style="text-align:center;margin:28px 0;">
  <a href="{url}"
     style="background:{bg};color:#FFFFFF;font-weight:800;font-size:14px;
            padding:14px 40px;border-radius:8px;text-decoration:none;
            display:inline-block;letter-spacing:0.5px;">{text}</a>
</div>"""


def _info_row(label: str, value: str, color: str = None) -> str:
    vc = color or C_TEXT
    return f"""<tr>
  <td style="padding:10px 0;border-bottom:1px solid #F3F4F6;">
    <span style="color:{C_MUTED};font-size:13px;">{label}</span>
  </td>
  <td style="padding:10px 0;border-bottom:1px solid #F3F4F6;text-align:right;">
    <span style="color:{vc};font-size:13px;font-weight:600;">{value}</span>
  </td>
</tr>"""


def _card(content: str, bg: str = "#F9FAFB", border: str = "#E5E7EB") -> str:
    return f"""<div style="background:{bg};border:1.5px solid {border};
                border-radius:12px;padding:22px 24px;margin:18px 0;">
  {content}
</div>"""


# ── OTP Email ─────────────────────────────────────────────────────────────

def render_otp(otp: str, username: str = "") -> str:
    name = username or "Trader"
    content = f"""
    <!-- Greeting -->
    <h2 style="color:{C_TEXT};font-size:22px;font-weight:800;margin:0 0 6px;">
      🔐 Verifikasi Email Kamu
    </h2>
    <p style="color:{C_MUTED};font-size:14px;line-height:1.7;margin:0 0 28px;">
      Halo <strong style="color:{C_TEXT};">{name}</strong>, masukkan kode OTP berikut
      untuk menyelesaikan pendaftaran akun <strong>Golden AI Strategy</strong> kamu.
    </p>

    <!-- OTP Box -->
    <div style="background:linear-gradient(135deg,{C_WARN_BG},{C_HEADER});
                border:2px solid {C_GOLD2};border-radius:16px;
                padding:36px 24px;text-align:center;margin:0 0 24px;">
      <p style="color:{C_MUTED};font-size:11px;font-weight:700;letter-spacing:4px;
                text-transform:uppercase;margin:0 0 14px;">Kode OTP Kamu</p>
      <p style="color:{C_GOLD};font-size:52px;font-weight:900;letter-spacing:18px;
                margin:0;font-family:'Courier New',monospace;">{otp}</p>
      <p style="color:{C_MUTED};font-size:12px;margin:14px 0 0;">
        ⏱️ Berlaku selama <strong style="color:{C_TEXT};">10 menit</strong>
      </p>
    </div>

    <!-- Warning -->
    <div style="background:{C_ERR_BG};border:1.5px solid {C_ERR_BD};
                border-radius:10px;padding:14px 18px;margin:0 0 20px;">
      <p style="color:{C_RED};font-size:13px;margin:0;font-weight:600;">
        🚫 Jangan bagikan kode ini ke siapapun!
      </p>
      <p style="color:{C_RED};font-size:12px;margin:6px 0 0;opacity:0.8;">
        Tim GAS <strong>tidak pernah</strong> meminta kode OTP kamu melalui pesan apapun.
      </p>
    </div>

    <!-- Info -->
    <p style="color:{C_LIGHT};font-size:12px;text-align:center;margin:20px 0 0;">
      Tidak mendaftar? Abaikan email ini — kode akan kedaluwarsa otomatis.
    </p>
    """
    return _base("Kode OTP — Golden AI Strategy", content)


# ── Welcome Email ─────────────────────────────────────────────────────────

def render_welcome(username: str, full_name: str = "") -> str:
    name = full_name or username
    features = [
        ("📊", "Technical AI", "Analisis teknikal real-time berbasis AI"),
        ("⚡", "Signal AI", "Sinyal entry/exit presisi tinggi"),
        ("🔔", "Alert System", "Notifikasi harga & pola instan"),
        ("🌍", "Session Tracker", "Pantau sesi London, NY, Asia"),
        ("📰", "Calendar & News", "Kalender ekonomi & berita pasar"),
        ("🏦", "Fundamental AI", "Data makro & fundamental analisis"),
    ]
    feature_rows = "".join(
        f"""<tr>
          <td style="padding:10px 0;border-bottom:1px solid #F3F4F6;width:36px;">
            <span style="font-size:20px;">{icon}</span>
          </td>
          <td style="padding:10px 0;border-bottom:1px solid #F3F4F6;padding-left:12px;">
            <strong style="color:{C_TEXT};font-size:13px;">{feat}</strong>
            <div style="color:{C_MUTED};font-size:12px;margin-top:1px;">{desc}</div>
          </td>
          <td style="padding:10px 0;border-bottom:1px solid #F3F4F6;text-align:right;">
            <span style="background:#D1FAE5;color:{C_GREEN};font-size:10px;font-weight:700;
                          padding:3px 9px;border-radius:20px;">✓ Aktif</span>
          </td>
        </tr>"""
        for icon, feat, desc in features
    )

    content = f"""
    <!-- Hero -->
    <h1 style="color:{C_TEXT};font-size:26px;font-weight:900;margin:0 0 4px;">
      🎉 Selamat Datang, {name}!
    </h1>
    <p style="color:{C_GOLD};font-size:13px;font-weight:700;margin:0 0 20px;letter-spacing:0.5px;">
      Akun Golden AI Strategy kamu berhasil dibuat ✅
    </p>
    <p style="color:{C_MUTED};font-size:14px;line-height:1.8;margin:0 0 24px;">
      Selamat bergabung di komunitas trader AI terdepan Indonesia! 🇮🇩
      Platform GAS dirancang untuk membantu kamu membuat keputusan trading
      yang lebih cerdas menggunakan kecerdasan buatan terkini.
    </p>

    <!-- Trial Banner -->
    <div style="background:{C_INFO_BG};border:1.5px solid {C_INFO_BD};
                border-radius:12px;padding:18px 22px;margin:0 0 24px;">
      <p style="color:{C_BLUE};font-size:13px;font-weight:800;margin:0 0 6px;">
        🎁 Trial 3 Hari — 10 Credits Gratis!
      </p>
      <p style="color:{C_MUTED};font-size:13px;margin:0;line-height:1.6;">
        Nikmati akses penuh selama 3 hari untuk menjelajahi semua fitur GAS.
        Upgrade kapan saja untuk akses tak terbatas.
      </p>
    </div>

    <!-- Account Info -->
    {_card(f'''
      <p style="color:{C_MUTED};font-size:11px;font-weight:700;letter-spacing:2px;
                text-transform:uppercase;margin:0 0 14px;">📋 Informasi Akun</p>
      <table width="100%" cellpadding="0" cellspacing="0">
        {_info_row("Username", f"@{username}")}
        {_info_row("Plan Aktif", "🎁 Trial · 3 Hari", C_BLUE)}
        {_info_row("Credits", "10 Credits", C_GOLD)}
        {_info_row("Status", "✅ Aktif", C_GREEN)}
      </table>
    ''')}

    <!-- Features List -->
    <p style="color:{C_MUTED};font-size:11px;font-weight:700;letter-spacing:2px;
              text-transform:uppercase;margin:24px 0 12px;">🚀 Fitur yang Tersedia</p>
    <table width="100%" cellpadding="0" cellspacing="0"
           style="border:1.5px solid #E5E7EB;border-radius:12px;overflow:hidden;">
      {feature_rows}
    </table>

    <!-- Upgrade Note -->
    <div style="background:{C_WARN_BG};border:1.5px solid {C_WARN_BD};
                border-radius:10px;padding:14px 18px;margin:20px 0;">
      <p style="color:#92400E;font-size:13px;margin:0;font-weight:600;">
        💡 18 Fitur AI Trading Canggih Tersedia
      </p>
      <p style="color:#92400E;font-size:12px;margin:6px 0 0;opacity:0.8;">
        Upgrade ke Essential, Plus, Premium, atau Ultimate untuk membuka semua fitur termasuk
        AI Backtesting, Smart Scanner, dan Mentor AI.
      </p>
    </div>

    {_btn("🚀 Mulai Trading Sekarang", SITE_URL, C_GOLD)}

    <p style="color:{C_LIGHT};font-size:12px;text-align:center;margin:8px 0 0;">
      Butuh bantuan?
      <a href="mailto:{SUPPORT_EMAIL}" style="color:{C_GOLD};font-weight:600;">{SUPPORT_EMAIL}</a>
    </p>
    """
    return _base(f"Selamat Datang di GAS, {name}!", content)


# ── Send helpers ──────────────────────────────────────────────────────────

def send_email(to_email: str, subject: str, html_body: str,
               from_name: str = "Golden AI Strategy") -> bool:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = formataddr((from_name, FROM_EMAIL))
    msg["To"] = to_email
    msg.attach(MIMEText("Email ini memerlukan HTML email client.", "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))
    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
            s.ehlo()
            s.starttls(context=ctx)
            s.login(SMTP_USER, SMTP_PASS)
            s.sendmail(FROM_EMAIL, [to_email], msg.as_string())
        logger.info(f"Email sent → {to_email}")
        return True
    except Exception as e:
        logger.error(f"Email failed → {to_email}: {e}")
        return False


def send_otp_email(to_email: str, otp: str, username: str = "") -> bool:
    html = render_otp(otp, username)
    return send_email(to_email, f"🔐 Kode OTP: {otp} — Golden AI Strategy", html)


def send_welcome_email(to_email: str, username: str, full_name: str = "") -> bool:
    html = render_welcome(username, full_name)
    name = full_name or username
    return send_email(to_email, f"🎉 Selamat Datang di Golden AI Strategy, {name}!", html)
