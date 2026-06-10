import os
import smtplib
import yaml
import requests
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import List, Dict

CONFIG_FILE = "/app/config/config.yml"

_last_notified: datetime = None
_MIN_INTERVAL_HOURS = 1


def load_config():
    if not Path(CONFIG_FILE).exists():
        return None
    with open(CONFIG_FILE, "r") as f:
        return yaml.safe_load(f)


def check_and_notify(certificates: List[Dict]):
    global _last_notified

    config = load_config()
    if not config:
        return

    now = datetime.now()
    if _last_notified and (now - _last_notified).total_seconds() < _MIN_INTERVAL_HOURS * 3600:
        return

    expired  = [c for c in certificates if c["days_remaining"] < 0]
    critical = [c for c in certificates if 0 <= c["days_remaining"] <= 10]
    warning  = [c for c in certificates if 10 < c["days_remaining"] <= 20]

    if not (expired or critical or warning):
        return

    _send_telegram(_build_telegram_message(expired, critical, warning, certificates), config)
    _send_email(_build_email_subject(expired, critical), _build_email_body(expired, critical, warning, certificates), config)
    _send_google_chat(_build_google_chat_message(expired, critical, warning, certificates), config)
    _last_notified = now


# --- Telegram ---

def _send_telegram(message: str, config: dict):
    try:
        tg = config.get("notifications", {}).get("telegram", {})
        if not tg.get("enabled"):
            return
        url = f"https://api.telegram.org/bot{tg['bot_token']}/sendMessage"
        requests.post(url, json={"chat_id": tg["chat_id"], "text": message, "parse_mode": "HTML"}, timeout=10)
    except Exception as e:
        print(f"[notifier] Telegram error: {e}")


def _build_telegram_message(expired, critical, warning, all_certs):
    msg = "🔐 <b>CertWatch-Pro — Alerta de Certificados</b>\n\n"

    if expired:
        msg += f"🔴 <b>EXPIRADOS ({len(expired)}):</b>\n"
        for c in expired[:5]:
            msg += f"  • {c['hostname']}: {c['subject']}\n"
            msg += f"    Expirado há {abs(c['days_remaining'])} dias\n"
        if len(expired) > 5:
            msg += f"  ... e mais {len(expired) - 5}\n"
        msg += "\n"

    if critical:
        msg += f"🟠 <b>CRÍTICOS ({len(critical)}):</b>\n"
        for c in critical[:5]:
            msg += f"  • {c['hostname']}: {c['subject']}\n"
            msg += f"    Expira em {c['days_remaining']} dias\n"
        if len(critical) > 5:
            msg += f"  ... e mais {len(critical) - 5}\n"
        msg += "\n"

    if warning:
        msg += f"🟡 <b>ATENÇÃO ({len(warning)}):</b>\n"
        for c in warning[:5]:
            msg += f"  • {c['hostname']}: {c['subject']}\n"
            msg += f"    Expira em {c['days_remaining']} dias\n"
        if len(warning) > 5:
            msg += f"  ... e mais {len(warning) - 5}\n"

    msg += f"\n📊 Total monitorado: {len(all_certs)} certificados"
    return msg


# --- Google Chat ---

def _send_google_chat(message: str, config: dict):
    try:
        gc = config.get("notifications", {}).get("google_chat", {})
        if not gc.get("enabled"):
            return
        requests.post(gc["webhook_url"], json={"text": message}, timeout=10)
    except Exception as e:
        print(f"[notifier] Google Chat error: {e}")


def _build_google_chat_message(expired, critical, warning, all_certs):
    lines = ["🔐 *CertWatch-Pro — Alerta de Certificados*\n"]

    if expired:
        lines.append(f"🔴 *EXPIRADOS ({len(expired)}):*")
        for c in expired[:5]:
            lines.append(f"  • `{c['hostname']}` — {c['subject']}")
            lines.append(f"    Expirado há {abs(c['days_remaining'])} dias")
        if len(expired) > 5:
            lines.append(f"  ... e mais {len(expired) - 5}")
        lines.append("")

    if critical:
        lines.append(f"🟠 *CRÍTICOS ({len(critical)}):*")
        for c in critical[:5]:
            lines.append(f"  • `{c['hostname']}` — {c['subject']}")
            lines.append(f"    Expira em {c['days_remaining']} dias")
        if len(critical) > 5:
            lines.append(f"  ... e mais {len(critical) - 5}")
        lines.append("")

    if warning:
        lines.append(f"🟡 *ATENÇÃO ({len(warning)}):*")
        for c in warning[:5]:
            lines.append(f"  • `{c['hostname']}` — {c['subject']}")
            lines.append(f"    Expira em {c['days_remaining']} dias")
        if len(warning) > 5:
            lines.append(f"  ... e mais {len(warning) - 5}")
        lines.append("")

    lines.append(f"📊 Total monitorado: {len(all_certs)} certificados")
    return "\n".join(lines)


# --- Email ---

def _send_email(subject: str, body_html: str, config: dict):
    try:
        em = config.get("notifications", {}).get("email", {})
        if not em.get("enabled"):
            return

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = em["from"]
        msg["To"]      = ", ".join(em["to"])
        msg.attach(MIMEText(body_html, "html", "utf-8"))

        with smtplib.SMTP(em["smtp_server"], em["smtp_port"]) as server:
            server.ehlo()
            server.starttls()
            server.login(em["smtp_user"], em["smtp_password"])
            server.sendmail(em["from"], em["to"], msg.as_string())
    except Exception as e:
        print(f"[notifier] Email error: {e}")


def _build_email_subject(expired, critical):
    if expired:
        return f"🔴 CertWatch-Pro: {len(expired)} certificado(s) EXPIRADO(S)"
    return f"🟠 CertWatch-Pro: {len(critical)} certificado(s) crítico(s)"


def _build_email_body(expired, critical, warning, all_certs):
    rows = ""

    def make_rows(certs, color, label):
        result = ""
        for c in certs:
            days = c["days_remaining"]
            days_text = f"Expirado há {abs(days)} dias" if days < 0 else f"Expira em {days} dias"
            result += f"""
            <tr>
                <td style="padding:8px;border-bottom:1px solid #eee;">
                    <span style="background:{color};color:white;padding:3px 8px;border-radius:4px;font-size:12px;">{label}</span>
                </td>
                <td style="padding:8px;border-bottom:1px solid #eee;font-weight:bold;">{c['hostname']}</td>
                <td style="padding:8px;border-bottom:1px solid #eee;">{c['subject']}</td>
                <td style="padding:8px;border-bottom:1px solid #eee;color:{color};font-weight:bold;">{days_text}</td>
                <td style="padding:8px;border-bottom:1px solid #eee;">{c['not_after']}</td>
            </tr>"""
        return result

    rows += make_rows(expired,  "#e74c3c", "EXPIRADO")
    rows += make_rows(critical, "#e67e22", "CRÍTICO")
    rows += make_rows(warning,  "#f39c12", "ATENÇÃO")

    return f"""
    <html><body style="font-family:Arial,sans-serif;margin:0;padding:20px;background:#f5f5f5;">
        <div style="max-width:800px;margin:0 auto;background:white;border-radius:8px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.1);">
            <div style="background:linear-gradient(135deg,#667eea,#764ba2);padding:30px;color:white;">
                <h1 style="margin:0;font-size:24px;">🔐 CertWatch-Pro</h1>
                <p style="margin:5px 0 0;opacity:0.9;">Alerta de Certificados SSL/TLS</p>
            </div>
            <div style="padding:20px;">
                <table style="width:100%;border-collapse:collapse;">
                    <thead>
                        <tr style="background:#f8f9fa;">
                            <th style="padding:10px;text-align:left;border-bottom:2px solid #ddd;">Status</th>
                            <th style="padding:10px;text-align:left;border-bottom:2px solid #ddd;">Servidor</th>
                            <th style="padding:10px;text-align:left;border-bottom:2px solid #ddd;">Certificado</th>
                            <th style="padding:10px;text-align:left;border-bottom:2px solid #ddd;">Situação</th>
                            <th style="padding:10px;text-align:left;border-bottom:2px solid #ddd;">Expira em</th>
                        </tr>
                    </thead>
                    <tbody>{rows}</tbody>
                </table>
                <p style="margin-top:20px;color:#666;font-size:13px;">
                    Total monitorado: {len(all_certs)} certificados
                </p>
            </div>
        </div>
    </body></html>
    """
