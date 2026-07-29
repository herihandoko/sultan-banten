"""Build and send action feedback to Mata Bathin (PRD Lampiran B.2)."""

from __future__ import annotations

from datetime import datetime, timezone

from flask import current_app

from app.models import (
    ContentItem,
    Issue,
    KolCampaign,
    MediaBlastLog,
    MediaSlaLog,
    Mission,
    OpdValidation,
)
from app.services.mata_bathin import MataBathinClient


def build_feedback_payload(issue: Issue, notes: str | None = None) -> dict:
    validations = OpdValidation.query.filter_by(issue_id=issue.id).all()
    validated = [v for v in validations if v.status == "validated"]
    contents = ContentItem.query.filter_by(issue_id=issue.id).all()
    published = [c for c in contents if c.status in {"approved", "published"}]
    blasts = MediaBlastLog.query.filter_by(issue_id=issue.id).all()
    blast_ok = [b for b in blasts if b.status in {"sent", "partial"}]
    media_count = sum(len(b.recipients or []) for b in blast_ok)
    missions = Mission.query.filter_by(issue_id=issue.id).count()
    kols = KolCampaign.query.filter_by(issue_id=issue.id).count()

    sla_rows = []
    blast_ids = [b.id for b in blasts]
    if blast_ids:
        sla_rows = MediaSlaLog.query.filter(MediaSlaLog.blast_log_id.in_(blast_ids)).all()
    avg_minutes = None
    if sla_rows:
        mins = [r.response_minutes for r in sla_rows if r.response_minutes is not None]
        if mins:
            avg_minutes = int(sum(mins) / len(mins))

    opd_notes = "; ".join(
            f"{v.opd_name}: {(v.response_notes or str(v.response_data or ''))[:200]}"
            for v in validated
            if v.opd_name
        )

    clarification_url = None
    for c in published:
        if c.media_url:
            clarification_url = c.media_url
            break

    return {
        "alert_id": issue.mb_alert_id or f"SB-ISSUE-{issue.id}",
        "sultan_issue_id": issue.id,
        "action_taken": {
            "opd_validated": bool(validated),
            "opd_notes": opd_notes or None,
            "clarification_produced": bool(published),
            "clarification_url": clarification_url,
            "media_blast_sent": bool(blast_ok),
            "media_count": media_count,
            "asn_missions_created": missions,
            "kol_engaged": kols,
        },
        "outcome": {
            "media_publication_time_avg": (
                f"{avg_minutes} minutes" if avg_minutes is not None else None
            ),
            "issue_status": issue.status,
            "notes": notes
            or f"Feedback otomatis dari SULTAN BANTEN — status {issue.status}",
        },
        "submitted_at": datetime.now(timezone.utc).isoformat(),
    }


def push_issue_feedback(issue: Issue, notes: str | None = None) -> dict:
    """
    Fail-open: always build payload; attempt POST if Mata Bathin configured.
    Returns {ok, sent, payload, reason}.
    """
    payload = build_feedback_payload(issue, notes=notes)
    base = (current_app.config.get("MATA_BATHIN_BASE_URL") or "").strip()
    if not base:
        current_app.logger.info(
            "Mata Bathin feedback queued locally (no BASE_URL): alert_id=%s",
            payload.get("alert_id"),
        )
        return {"ok": True, "sent": False, "payload": payload, "reason": "not_configured"}

    client = MataBathinClient()
    sent = client.send_feedback(payload)
    if not sent:
        current_app.logger.warning(
            "Mata Bathin feedback failed (fail-open): alert_id=%s",
            payload.get("alert_id"),
        )
        return {"ok": True, "sent": False, "payload": payload, "reason": "send_failed"}

    current_app.logger.info(
        "Mata Bathin feedback sent: alert_id=%s", payload.get("alert_id")
    )
    return {"ok": True, "sent": True, "payload": payload, "reason": "sent"}
