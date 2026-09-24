"""Email + WhatsApp to a role, with a link back into SIAGAPIM."""

from __future__ import annotations

import logging
import os

from flask import has_request_context, request

from app.models import ContentItem, Issue, OpdValidation, Role, User
from app.services.messaging import send_email, send_whatsapp

logger = logging.getLogger(__name__)

_TYPE_LABEL = {
    "text_release": "Rilis teks",
    "infographic": "Infografis",
    "video": "Video",
}


def public_url(path: str) -> str:
    """Absolute app URL. Uses PUBLIC_APP_URL when set, otherwise the incoming host."""
    configured = (os.getenv("PUBLIC_APP_URL") or "").strip().rstrip("/")
    if configured:
        base = configured
    elif has_request_context():
        proto = (request.headers.get("X-Forwarded-Proto") or request.scheme or "http").split(",")[0].strip()
        host = (request.headers.get("X-Forwarded-Host") or request.host or "").split(",")[0].strip()
        base = f"{proto}://{host}".rstrip("/")
    else:
        base = ""
    suffix = path if str(path).startswith("/") else f"/{path}"
    return f"{base}{suffix}"


def _active_users(role_code: str) -> list[User]:
    return (
        User.query.join(Role)
        .filter(User.is_active.is_(True), Role.code == role_code)
        .order_by(User.full_name)
        .all()
    )


def notify_users(users: list[User], *, subject: str, body: str, empty_label: str) -> list[dict]:
    """Send email and WhatsApp. A failed channel does not raise."""
    people = [person for person in users if person]
    if not people:
        return [
            {"channel": "whatsapp", "status": "skipped", "error": f"Tidak ada {empty_label} yang bisa dihubungi"},
            {"channel": "email", "status": "skipped", "error": f"Tidak ada {empty_label} yang bisa dihubungi"},
        ]

    results = []
    for person in people:
        name = person.full_name or person.username
        try:
            if person.phone:
                results.append(send_whatsapp(person.phone, body))
            else:
                results.append(
                    {
                        "channel": "whatsapp",
                        "to": name,
                        "status": "skipped",
                        "error": "Nomor WhatsApp kosong",
                    }
                )
        except Exception as exc:  # noqa: BLE001
            logger.exception("WhatsApp notify failed for user %s", person.id)
            results.append({"channel": "whatsapp", "to": name, "status": "failed", "error": str(exc)})
        try:
            if person.email:
                results.append(send_email(person.email, subject, body))
            else:
                results.append(
                    {
                        "channel": "email",
                        "to": name,
                        "status": "skipped",
                        "error": "Email kosong",
                    }
                )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Email notify failed for user %s", person.id)
            results.append({"channel": "email", "to": name, "status": "failed", "error": str(exc)})
    return results


def _opd_note(issue: Issue) -> tuple[str, str]:
    rows = (
        OpdValidation.query.filter_by(issue_id=issue.id, status="validated")
        .order_by(OpdValidation.responded_at.desc())
        .all()
    )
    names: list[str] = []
    note = ""
    for row in rows:
        if row.opd_name and row.opd_name not in names:
            names.append(row.opd_name)
        if not note and (row.response_notes or "").strip():
            note = row.response_notes.strip()
    who = ", ".join(names) if names else "OPD"
    return who, note


def notify_editors_content_ready(issue: Issue) -> list[dict]:
    """Email + WhatsApp ke editor setelah verifikasi OPD selesai."""
    who, note = _opd_note(issue)
    create_link = public_url(f"/konten?issue_id={issue.id}")
    latest = (
        ContentItem.query.filter_by(issue_id=issue.id)
        .order_by(ContentItem.updated_at.desc())
        .first()
    )
    lines = [
        "Verifikasi OPD selesai. Berita ini siap dibuatkan konten.",
        "",
        f"Isu: {issue.title}",
        f"OPD: {who}",
    ]
    if note:
        lines.append(f"Catatan: {note}")
    lines.extend(["", "Buat konten:", create_link])
    if latest:
        lines.extend(["", "Naskah yang sudah ada:", public_url(f"/konten/{latest.id}")])
    subject = f"Siap dibuatkan konten — {issue.title}"
    return notify_users(
        _active_users("editor"),
        subject=subject,
        body="\n".join(lines),
        empty_label="editor",
    )


def notify_pimpinan_review(item: ContentItem, submitter: User | None) -> list[dict]:
    """Email + WhatsApp ke pimpinan saat editor mengajukan review."""
    who = (submitter.full_name or submitter.username) if submitter else "Editor"
    kind = _TYPE_LABEL.get(item.content_type, item.content_type or "Naskah")
    issue_title = item.issue.title if item.issue else "-"
    link = public_url(f"/konten/{item.id}")
    subject = f"Naskah menunggu persetujuan — {item.title}"
    body = "\n".join(
        [
            "Ada naskah yang menunggu persetujuan.",
            "",
            f"Judul: {item.title}",
            f"Jenis: {kind}",
            f"Isu: {issue_title}",
            f"Diajukan oleh: {who}",
            "",
            "Buka naskah:",
            link,
        ]
    )
    return notify_users(
        _active_users("pimpinan"),
        subject=subject,
        body=body,
        empty_label="pimpinan",
    )
