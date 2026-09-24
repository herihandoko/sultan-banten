"""Mata Bathin connector — consume alerts and send feedback."""

from __future__ import annotations

import time
from typing import Any

import requests
from flask import current_app

from flask import current_app

from app.extensions import db
from app.models import Issue, IssueEvidence
from app.models.issue import public_actions


class MataBathinClient:
    """REST client with retry + circuit-breaker style fail-open."""

    def __init__(self):
        self.base_url = (current_app.config.get("MATA_BATHIN_BASE_URL") or "").rstrip("/")
        self.api_key = current_app.config.get("MATA_BATHIN_API_KEY") or ""
        self.timeout = current_app.config.get("MATA_BATHIN_TIMEOUT", 10)
        self.max_retries = current_app.config.get("MATA_BATHIN_MAX_RETRIES", 3)

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            headers["X-API-Key"] = self.api_key
        return headers

    def _request(self, method: str, path: str, **kwargs) -> requests.Response | None:
        if not self.base_url:
            return None

        url = f"{self.base_url}{path}"
        last_error: Exception | None = None
        for attempt in range(self.max_retries):
            try:
                response = requests.request(
                    method,
                    url,
                    headers=self._headers(),
                    timeout=self.timeout,
                    **kwargs,
                )
                response.raise_for_status()
                return response
            except requests.RequestException as exc:
                last_error = exc
                time.sleep(2**attempt)
        current_app.logger.warning("Mata Bathin request failed: %s", last_error)
        return None

    def health_check(self) -> bool:
        response = self._request("GET", "/health")
        return response is not None and response.ok

    def send_feedback(self, payload: dict[str, Any]) -> bool:
        response = self._request("POST", "/api/v1/feedback", json=payload)
        return response is not None


def ingest_crisis_alert(payload: dict[str, Any]) -> tuple[Issue, bool]:
    """Upsert Issue from Mata Bathin crisis_alert payload (Lampiran B.1)."""
    alert_id = payload.get("alert_id")
    existing = Issue.query.filter_by(mb_alert_id=alert_id).first() if alert_id else None

    risk = payload.get("severity") or payload.get("risk_level") or "R0"
    assessment = payload.get("risk_assessment") or {}

    if existing:
        existing.title = payload.get("title") or existing.title
        existing.summary = payload.get("issue_summary") or existing.summary
        existing.why_now = payload.get("why_now") or existing.why_now
        existing.risk_level = risk
        existing.risk_assessment = assessment
        existing.recommended_actions = public_actions(payload.get("recommended_actions"))
        existing.narrative_card = payload.get("narrative_card")
        issue = existing
        created = False
    else:
        issue = Issue(
            mb_alert_id=alert_id,
            title=payload.get("title") or "Alert tanpa judul",
            summary=payload.get("issue_summary"),
            why_now=payload.get("why_now"),
            risk_level=risk,
            risk_assessment=assessment,
            recommended_actions=public_actions(payload.get("recommended_actions")),
            narrative_card=payload.get("narrative_card"),
            status="open",
            source=payload.get("source")
            or ("sipantau" if str(alert_id or "").startswith("sipantau-") else "mata_bathin"),
            project_id=(
                payload.get("project_id")
                or (assessment.get("sipantau_keyword_id") if isinstance(assessment, dict) else None)
            ),
        )
        db.session.add(issue)
        db.session.flush()
        created = True

    # Keep project linkage up to date on upsert
    incoming_project = payload.get("project_id") or (
        assessment.get("sipantau_keyword_id") if isinstance(assessment, dict) else None
    )
    if incoming_project:
        issue.project_id = str(incoming_project)
        if isinstance(issue.risk_assessment, dict):
            issue.risk_assessment = {
                **issue.risk_assessment,
                "sipantau_keyword_id": str(incoming_project),
            }
        elif assessment:
            issue.risk_assessment = {
                **(assessment if isinstance(assessment, dict) else {}),
                "sipantau_keyword_id": str(incoming_project),
            }

    evidence_url = payload.get("evidence_pack_url")
    assessment_dict = assessment if isinstance(assessment, dict) else {}
    outlet = (
        payload.get("outlet")
        or payload.get("source_name")
        or assessment_dict.get("outlet")
        or assessment_dict.get("author_name")
        or assessment_dict.get("platform")
    )
    if evidence_url:
        evidence_url = str(evidence_url).strip()
        # Google News RSS links can exceed VARCHAR(500)
        if len(evidence_url) > 2000:
            evidence_url = evidence_url[:2000]
        if evidence_url and not any(e.url == evidence_url for e in (issue.evidence or [])):
            from app.models.issue import _hostname_label, _pretty_platform

            source_name = None
            if outlet and str(outlet).strip().lower() not in {
                "sipantau",
                "mata_bathin",
                "manual",
                "news",
                "blog",
                "media",
                "media online",
            }:
                pretty = _pretty_platform(str(outlet))
                source_name = pretty or str(outlet)
            source_name = source_name or _hostname_label(evidence_url) or None
            if not source_name:
                source_name = "Media"
            db.session.add(
                IssueEvidence(
                    issue_id=issue.id,
                    title="Evidence Pack",
                    url=evidence_url,
                    source_name=str(source_name)[:150],
                    evidence_type="other",
                )
            )

    # Enrich assessment with outlet for list badges
    if outlet and isinstance(issue.risk_assessment, dict):
        issue.risk_assessment = {
            **issue.risk_assessment,
            "outlet": str(outlet)[:80],
        }

    from app.services.alerts import maybe_alert_on_issue

    # Fire F.02 alert for R3+ (new or risk elevated) — never fail the ingest
    try:
        if created or risk in {"R3", "R4", "R5"}:
            maybe_alert_on_issue(issue, force=created)
    except Exception as exc:  # noqa: BLE001
        current_app.logger.warning("crisis alert side-effect failed: %s", exc)

    db.session.commit()
    return issue, created
