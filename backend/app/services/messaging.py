"""WhatsApp (Fonnte) + Email (SMTP) delivery for Media Hub blast & alerts."""

from __future__ import annotations

import logging
import os
import smtplib
import ssl
from email.message import EmailMessage
from typing import Any

import requests

logger = logging.getLogger(__name__)

FONNTE_SEND_URL = "https://api.fonnte.com/send"


def _cfg(key: str, default: str = "") -> str:
    try:
        from flask import current_app, has_app_context

        if has_app_context():
            val = current_app.config.get(key)
            if val is not None and str(val) != "":
                return str(val)
    except Exception:
        pass
    return os.getenv(key, default)


def _truthy(key: str, default: str = "false") -> bool:
    return _cfg(key, default).strip().lower() in {"1", "true", "yes", "on"}


def messaging_status() -> dict[str, Any]:
    """Public status (no secrets) for Media Hub UI."""
    mail_enabled = _truthy("MAIL_ENABLED")
    fonnte_token = bool(_cfg("FONNTE_TOKEN").strip())
    return {
        "mail": {
            "enabled": mail_enabled,
            "host": _cfg("MAIL_HOST") if mail_enabled else None,
            "port": int(_cfg("MAIL_PORT", "587") or 587) if mail_enabled else None,
            "from": _cfg("MAIL_FROM_ADDRESS") if mail_enabled else None,
            "from_name": _cfg("MAIL_FROM_NAME") if mail_enabled else None,
            "encryption": _cfg("MAIL_ENCRYPTION", "tls") if mail_enabled else None,
        },
        "whatsapp": {
            "provider": "fonnte",
            "enabled": fonnte_token,
            "api_url": FONNTE_SEND_URL if fonnte_token else None,
        },
    }


def normalize_wa_number(raw: str) -> str:
    """Normalize ID numbers for Fonnte (digits only; leave leading 0 for countryCode)."""
    digits = "".join(c for c in (raw or "") if c.isdigit())
    if digits.startswith("62") and len(digits) > 10:
        # Fonnte accepts 62…; countryCode=62 also ok — keep as-is
        return digits
    return digits


def send_whatsapp(to: str, message: str) -> dict[str, Any]:
    """Send WhatsApp via Fonnte API. Falls back to mock only if FONNTE_MOCK=true."""
    target = normalize_wa_number(to)
    if not target:
        return {"channel": "whatsapp", "to": to, "status": "failed", "error": "Nomor WA kosong"}

    token = _cfg("FONNTE_TOKEN").strip()
    if not token:
        if _truthy("FONNTE_MOCK", "false"):
            return {
                "channel": "whatsapp",
                "to": target,
                "status": "sent",
                "message_id": "WA-MOCK",
                "preview": (message or "")[:120],
                "provider": "mock",
            }
        return {
            "channel": "whatsapp",
            "to": target,
            "status": "failed",
            "error": "FONNTE_TOKEN belum dikonfigurasi",
        }

    payload = {
        "target": target,
        "message": message or "",
        "countryCode": _cfg("FONNTE_COUNTRY_CODE", "62"),
        "delay": _cfg("FONNTE_DELAY", "2"),
    }
    try:
        resp = requests.post(
            FONNTE_SEND_URL,
            data=payload,
            headers={"Authorization": token},
            timeout=float(_cfg("FONNTE_TIMEOUT", "20") or 20),
        )
        data: dict[str, Any]
        try:
            data = resp.json() if resp.content else {}
        except ValueError:
            data = {"raw": resp.text[:500]}

        ok = bool(data.get("status")) and resp.status_code < 400
        message_ids = data.get("id") or []
        if isinstance(message_ids, list):
            message_id = ",".join(str(x) for x in message_ids) if message_ids else None
        else:
            message_id = str(message_ids) if message_ids else None

        if ok:
            return {
                "channel": "whatsapp",
                "to": target,
                "status": "sent",
                "message_id": message_id or data.get("requestid"),
                "preview": (message or "")[:120],
                "provider": "fonnte",
                "provider_detail": data.get("detail"),
            }

        reason = data.get("reason") or data.get("detail") or f"HTTP {resp.status_code}"
        logger.warning("Fonnte send failed to=%s reason=%s", target, reason)
        return {
            "channel": "whatsapp",
            "to": target,
            "status": "failed",
            "error": str(reason),
            "provider": "fonnte",
            "provider_response": data,
        }
    except requests.RequestException as err:
        logger.exception("Fonnte request error")
        return {
            "channel": "whatsapp",
            "to": target,
            "status": "failed",
            "error": str(err),
            "provider": "fonnte",
        }


def send_email(to: str, subject: str, body: str) -> dict[str, Any]:
    """Send email via SMTP when MAIL_ENABLED=true."""
    to_addr = (to or "").strip()
    if not to_addr:
        return {"channel": "email", "to": to, "status": "failed", "error": "Email kosong"}

    if not _truthy("MAIL_ENABLED"):
        if _truthy("MAIL_MOCK", "false"):
            return {
                "channel": "email",
                "to": to_addr,
                "status": "sent",
                "message_id": "EM-MOCK",
                "subject": subject,
                "preview": (body or "")[:120],
                "provider": "mock",
            }
        return {
            "channel": "email",
            "to": to_addr,
            "status": "failed",
            "error": "MAIL_ENABLED=false — aktifkan di env untuk kirim email",
        }

    host = _cfg("MAIL_HOST").strip()
    port = int(_cfg("MAIL_PORT", "587") or 587)
    username = _cfg("MAIL_USERNAME").strip()
    password = _cfg("MAIL_PASSWORD")
    encryption = _cfg("MAIL_ENCRYPTION", "tls").strip().lower()
    from_addr = _cfg("MAIL_FROM_ADDRESS").strip() or username
    from_name = _cfg("MAIL_FROM_NAME").strip() or from_addr

    if not host or not from_addr:
        return {
            "channel": "email",
            "to": to_addr,
            "status": "failed",
            "error": "MAIL_HOST / MAIL_FROM_ADDRESS belum lengkap",
        }

    msg = EmailMessage()
    msg["Subject"] = subject or "(tanpa subjek)"
    msg["From"] = f"{from_name} <{from_addr}>"
    msg["To"] = to_addr
    msg.set_content(body or "")

    try:
        if encryption == "ssl":
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(host, port, timeout=30, context=context) as smtp:
                if username:
                    smtp.login(username, password)
                smtp.send_message(msg)
        else:
            with smtplib.SMTP(host, port, timeout=30) as smtp:
                smtp.ehlo()
                if encryption in {"tls", "starttls", "1", "true"}:
                    context = ssl.create_default_context()
                    smtp.starttls(context=context)
                    smtp.ehlo()
                if username:
                    smtp.login(username, password)
                smtp.send_message(msg)

        return {
            "channel": "email",
            "to": to_addr,
            "status": "sent",
            "message_id": f"smtp:{from_addr}",
            "subject": subject,
            "preview": (body or "")[:120],
            "provider": "smtp",
        }
    except (smtplib.SMTPException, OSError, TimeoutError) as err:
        logger.exception("SMTP send failed")
        return {
            "channel": "email",
            "to": to_addr,
            "status": "failed",
            "error": str(err),
            "provider": "smtp",
        }


def deliver_to_partner(
    partner: dict[str, Any],
    channel: str,
    subject: str,
    body: str,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    use_wa = channel in {"whatsapp", "both"}
    use_email = channel in {"email", "both"}

    if use_wa:
        results.append(send_whatsapp(partner.get("whatsapp") or "", body))
    if use_email:
        results.append(send_email(partner.get("email") or "", subject, body))
    return results
