"""Intel overview dashboard — KPIs from SIPANTAU + active Crisis Room issues."""

from datetime import datetime, timezone

import requests
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import jwt_required

from app.models import Issue
from app.utils.auth import role_required
from app.utils.project_scope import filter_issues_query, request_project_id
from app.extensions import db

bp = Blueprint("dashboard", __name__)

OPEN_STATUSES = {"open", "validating", "producing", "approved"}


def _relative_time(dt: datetime | None) -> str:
    if not dt:
        return "—"
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    delta = datetime.now(timezone.utc) - dt
    minutes = int(delta.total_seconds() // 60)
    if minutes < 1:
        return "baru saja"
    if minutes < 60:
        return f"{minutes} menit lalu"
    hours = minutes // 60
    if hours < 24:
        return f"{hours} jam lalu"
    days = hours // 24
    return f"{days} hari lalu"


def _severity_from_risk(level: str) -> str:
    if level in {"R4", "R5"}:
        return "tinggi"
    if level in {"R2", "R3"}:
        return "sedang"
    return "rendah"


def _sipantau_headers() -> dict[str, str]:
    headers = {"Accept": "application/json"}
    internal_key = current_app.config.get("SIPANTAU_INTERNAL_KEY") or ""
    if internal_key:
        headers["X-Internal-Key"] = internal_key
    auth = request.headers.get("Authorization")
    if auth:
        headers["Authorization"] = auth
    return headers


def _sipantau_base() -> str:
    return (current_app.config.get("SIPANTAU_INTERNAL_URL") or "").rstrip("/")


def _fetch_sipantau_dashboard(keyword_id: str | None = None) -> dict | None:
    base = _sipantau_base()
    if not base:
        return None
    params = {}
    if keyword_id:
        params["keyword_id"] = keyword_id
    try:
        res = requests.get(
            f"{base}/api/export/dashboard",
            headers=_sipantau_headers(),
            params=params,
            timeout=current_app.config.get("SIPANTAU_TIMEOUT", 8),
        )
        if not res.ok:
            current_app.logger.warning("SIPANTAU dashboard export HTTP %s", res.status_code)
            return None
        body = res.json()
        return body.get("data") if isinstance(body, dict) else None
    except requests.RequestException as exc:
        current_app.logger.warning("SIPANTAU dashboard export failed: %s", exc)
        return None


def _fetch_sipantau_projects() -> list[dict] | None:
    base = _sipantau_base()
    if not base:
        return None
    try:
        res = requests.get(
            f"{base}/api/keywords",
            headers=_sipantau_headers(),
            timeout=current_app.config.get("SIPANTAU_TIMEOUT", 8),
        )
        if not res.ok:
            current_app.logger.warning("SIPANTAU keywords HTTP %s", res.status_code)
            return None
        body = res.json()
        rows = body.get("data") if isinstance(body, dict) else None
        if not isinstance(rows, list):
            return None
        projects = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            pid = row.get("id")
            if not pid:
                continue
            projects.append(
                {
                    "id": str(pid),
                    "name": row.get("name") or row.get("keyword") or str(pid),
                    "keyword": row.get("keyword") or "",
                    "avatar_emoji": row.get("avatarEmoji") or row.get("avatar_emoji") or "📡",
                    "total_mentions": row.get("totalMentions") or row.get("total_mentions") or 0,
                }
            )
        return projects
    except requests.RequestException as exc:
        current_app.logger.warning("SIPANTAU keywords failed: %s", exc)
        return None


def _stub_metrics() -> dict:
    return {
        "source": "sipantau_stub",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "kpis": {
            "total_mention": 0,
            "sentiment_negative_pct": 0,
            "reach": 0,
            "active_issues": 0,
        },
        "trend_7d": {
            "labels": ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"],
            "positif": [0, 0, 0, 0, 0, 0, 0],
            "negatif": [0, 0, 0, 0, 0, 0, 0],
        },
        "platforms": [
            {"key": "twitter", "label": "X/Twitter", "count": 0},
            {"key": "news", "label": "Portal berita", "count": 0},
            {"key": "instagram", "label": "Instagram", "count": 0},
        ],
    }


@bp.get("/projects")
@jwt_required()
@role_required("super_admin", "editor", "pimpinan", "media_kol_admin", "opd_admin")
def list_projects():
    """Daftar project SIPANTAU (keyword) untuk filter topbar SIAGAPIM."""
    projects = _fetch_sipantau_projects()
    if projects is None:
        return jsonify({"data": [], "source": "unavailable"}), 200
    return jsonify({"data": projects, "source": "sipantau"})


@bp.get("")
@jwt_required()
@role_required("super_admin", "editor", "pimpinan", "media_kol_admin", "opd_admin")
def intel_dashboard():
    """
    Ringkasan intelijen untuk beranda.
    Metrik mention/sentimen/reach: dari SIPANTAU (fallback stub jika down).
    Alert isu aktif: dari database Crisis Room.
    Query: project_id / keyword_id — filter KPI + isu terkait project SIPANTAU.
    """
    project_id = (request.args.get("project_id") or request.args.get("keyword_id") or "").strip() or None

    projects = _fetch_sipantau_projects() or []
    project_meta = next((p for p in projects if p["id"] == project_id), None) if project_id else None

    issues_q = filter_issues_query(Issue.query.order_by(Issue.created_at.desc()), project_id)
    # Align with Crisis Room: hide seed/demo issues from "isu aktif"
    issues_q = issues_q.filter(
        db.or_(
            Issue.mb_alert_id.is_(None),
            ~Issue.mb_alert_id.ilike("SEED-%"),
        )
    )
    issues = issues_q.all()
    active = [i for i in issues if i.status in OPEN_STATUSES]

    # Pull fresh SIPANTAU negatives into Crisis Room when dashboard loads
    try:
        from app.services.sipantau_sync import sync_sipantau_crises

        sync_sipantau_crises(project_id)
        issues = filter_issues_query(Issue.query.order_by(Issue.created_at.desc()), project_id)
        issues = issues.filter(
            db.or_(
                Issue.mb_alert_id.is_(None),
                ~Issue.mb_alert_id.ilike("SEED-%"),
            )
        ).all()
        active = [i for i in issues if i.status in OPEN_STATUSES]
    except Exception as exc:  # noqa: BLE001
        current_app.logger.warning("dashboard crisis sync skipped: %s", exc)

    alerts = []
    for issue in active[:6]:
        alerts.append(
            {
                "id": issue.id,
                "title": issue.title,
                "severity": _severity_from_risk(issue.risk_level),
                "risk_level": issue.risk_level,
                "status": issue.status,
                "ago": _relative_time(issue.updated_at or issue.created_at),
            }
        )

    sip = _fetch_sipantau_dashboard(project_id) or _stub_metrics()
    kpis = dict(sip.get("kpis") or {})
    kpis["active_issues"] = len(active)

    return jsonify(
        {
            "data": {
                "source": sip.get("source") or "sipantau",
                "updated_at": sip.get("updated_at") or datetime.now(timezone.utc).isoformat(),
                "project_id": project_id,
                "project": project_meta,
                "kpis": kpis,
                "trend_7d": sip.get("trend_7d")
                or {
                    "labels": ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"],
                    "positif": [0, 0, 0, 0, 0, 0, 0],
                    "negatif": [0, 0, 0, 0, 0, 0, 0],
                },
                "alerts": alerts,
                "platforms": sip.get("platforms") or [],
            }
        }
    )
