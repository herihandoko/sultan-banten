"""F.02 Alert dispatcher — web + mock WhatsApp/Telegram."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.extensions import db
from app.models import CrisisAlert, Issue
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
    """Mock outbound notifications for demo."""
    body = f"{title}\n\n{message}"
    return {
        "web": {"channel": "web", "status": "queued"},
        "whatsapp": send_whatsapp("6281200009999", body),  # demo desk number
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
