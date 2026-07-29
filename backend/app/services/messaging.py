"""Mock delivery gateways for WhatsApp & Email (demo-ready)."""

from __future__ import annotations

import random
from typing import Any


def send_whatsapp(to: str, message: str) -> dict[str, Any]:
    """Simulate WA Gateway send. Always succeeds in demo unless number empty."""
    if not to:
        return {"channel": "whatsapp", "to": to, "status": "failed", "error": "Nomor WA kosong"}
    return {
        "channel": "whatsapp",
        "to": to,
        "status": "sent",
        "message_id": f"WA-{random.randint(100000, 999999)}",
        "preview": message[:120],
    }


def send_email(to: str, subject: str, body: str) -> dict[str, Any]:
    """Simulate Email Gateway send."""
    if not to:
        return {"channel": "email", "to": to, "status": "failed", "error": "Email kosong"}
    return {
        "channel": "email",
        "to": to,
        "status": "sent",
        "message_id": f"EM-{random.randint(100000, 999999)}",
        "subject": subject,
        "preview": body[:120],
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
