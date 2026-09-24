"""F.02 Alert dispatcher — web + mock WhatsApp/Telegram."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.extensions import db
from app.models import CrisisAlert, Issue, OpdValidation
from app.services.messaging import send_whatsapp

CRITICAL_LEVELS = {"R3", "R4", "R5"}
RESPONSE_SLA_HOURS = 2  # overdue if R3+ still open/validating after this


def _mock_telegram(chat: str, text: str) -> dict:
    if not chat:
        return {"channel": "telegram", "status": "failed", "error": "chat id kosong"}
    return {
        "channel": "telegram",
        "to": chat,
        "status": "sent",
        "preview": text[:120],
    }


def dispatch_channels(title: str, message: str) -> dict:
    """Outbound notifications: web queue + WhatsApp (Fonnte) + telegram mock."""
    from app.services.app_settings import messaging_value

    body = f"{title}\n\n{message}"
    wa_to = messaging_value("CRISIS_WA_NUMBER", "").strip()
    wa_result = (
        send_whatsapp(wa_to, body)
        if wa_to
        else {"channel": "whatsapp", "status": "skipped", "error": "Nomor WhatsApp krisis belum diisi"}
    )
    return {
        "web": {"channel": "web", "status": "queued"},
        "whatsapp": wa_result,
        "telegram": _mock_telegram("@sultan_banten_crisis", body),
    }


def create_crisis_alert(
    *,
    issue: Issue | None,
    alert_type: str,
    title: str,
    message: str,
    risk_level: str | None = None,
    severity: str = "high",
) -> CrisisAlert:
    delivery = dispatch_channels(title, message)
    alert = CrisisAlert(
        issue_id=issue.id if issue else None,
        alert_type=alert_type,
        title=title,
        message=message,
        risk_level=risk_level or (issue.risk_level if issue else None),
        severity=severity,
        channels=["web", "whatsapp", "telegram"],
        delivery_status=delivery,
        is_read=False,
    )
    db.session.add(alert)
    db.session.flush()
    return alert


def notify_content_ready(issue: Issue) -> CrisisAlert | None:
    """Web-only notice for editors once OPD verification moves an issue to producing.

    Does not send WhatsApp or Telegram. Skips if an unread notice already exists.
    """
    existing = (
        CrisisAlert.query.filter_by(
            issue_id=issue.id,
            alert_type="content_ready",
            is_read=False,
        )
        .order_by(CrisisAlert.created_at.desc())
        .first()
    )
    if existing:
        return existing

    rows = (
        OpdValidation.query.filter_by(issue_id=issue.id, status="validated")
        .order_by(OpdValidation.responded_at.desc())
        .all()
    )
    names = []
    note = ""
    for row in rows:
        if row.opd_name and row.opd_name not in names:
            names.append(row.opd_name)
        if not note and (row.response_notes or "").strip():
            note = row.response_notes.strip()
    who = ", ".join(names) if names else "OPD"
    if note:
        message = f"Validasi {who} selesai. Catatan OPD: {note}"
    else:
        message = f"Validasi {who} selesai. Berita ini menunggu naskah klarifikasi."
    alert = CrisisAlert(
        issue_id=issue.id,
        alert_type="content_ready",
        title=f"Siap dibuatkan konten: {issue.title}",
        message=message,
        risk_level=issue.risk_level,
        severity="info",
        channels=["web"],
        delivery_status={"web": {"channel": "web", "status": "queued"}},
        is_read=False,
    )
    db.session.add(alert)
    db.session.flush()
    return alert


def notify_review_pending(issue: Issue, content) -> CrisisAlert | None:
    """Web bell for pimpinan when an editor submits a draft for approval."""
    existing = (
        CrisisAlert.query.filter_by(
            issue_id=issue.id if issue else None,
            alert_type="content_review",
            is_read=False,
        )
        .order_by(CrisisAlert.created_at.desc())
        .all()
    )
    for row in existing:
        if (row.delivery_status or {}).get("content_id") == content.id:
            return row

    alert = CrisisAlert(
        issue_id=issue.id if issue else None,
        alert_type="content_review",
        title=f"Naskah menunggu persetujuan: {content.title}",
        message="Editor mengajukan review. Buka naskah untuk menyetujui atau mengembalikan.",
        risk_level=issue.risk_level if issue else None,
        severity="info",
        channels=["web"],
        delivery_status={
            "web": {"channel": "web", "status": "queued"},
            "content_id": content.id,
        },
        is_read=False,
    )
    db.session.add(alert)
    db.session.flush()
    return alert


def maybe_alert_on_issue(issue: Issue, *, force: bool = False) -> CrisisAlert | None:
    """Create R3+ alert when issue is created/updated to elevated risk."""
    if issue.risk_level not in CRITICAL_LEVELS:
        return None

    # Avoid duplicate unread risk alerts for same issue
    if not force:
        existing = (
            CrisisAlert.query.filter_by(
                issue_id=issue.id,
                alert_type="risk_threshold",
                is_read=False,
            )
            .order_by(CrisisAlert.created_at.desc())
            .first()
        )
        if existing:
            return existing

    severity = "critical" if issue.risk_level in {"R4", "R5"} else "high"
    return create_crisis_alert(
        issue=issue,
        alert_type="risk_threshold",
        title=f"ALERT {issue.risk_level}: {issue.title}",
        message=(
            issue.why_now
            or issue.summary
            or f"Isu dengan tingkat risiko {issue.risk_level} memerlukan respons segera."
        ),
        risk_level=issue.risk_level,
        severity=severity,
    )


def scan_overdue_responses() -> list[CrisisAlert]:
    """Alert when R3+ issues exceed response SLA without progress."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=RESPONSE_SLA_HOURS)
    candidates = (
        Issue.query.filter(
            Issue.risk_level.in_(list(CRITICAL_LEVELS)),
            Issue.status.in_(["open", "validating"]),
            Issue.created_at <= cutoff,
        )
        .all()
    )
    created: list[CrisisAlert] = []
    for issue in candidates:
        already = (
            CrisisAlert.query.filter_by(issue_id=issue.id, alert_type="response_overdue")
            .filter(CrisisAlert.created_at >= cutoff)
            .first()
        )
        if already:
            continue
        alert = create_crisis_alert(
            issue=issue,
            alert_type="response_overdue",
            title=f"OVERDUE {issue.risk_level}: {issue.title}",
            message=(
                f"Batas waktu respons ({RESPONSE_SLA_HOURS} jam) terlampaui. "
                f"Status saat ini: {issue.status}."
            ),
            risk_level=issue.risk_level,
            severity="critical",
        )
        created.append(alert)
    if created:
        db.session.commit()
    return created
