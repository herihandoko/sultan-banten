"""Intel overview dashboard — KPIs from SIPANTAU + active Crisis Room issues."""

from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import requests
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import func

from app.models import (
    ContentItem,
    EditorialAgenda,
    Issue,
    KolCampaign,
    KolPartner,
    MediaBlastLog,
    MediaPartner,
    MediaSlaLog,
    Mission,
    MissionParticipation,
    OpdValidation,
)
from app.utils.auth import get_current_user, role_required
from app.utils.project_scope import filter_issues_query, filter_query_by_issue_ids, request_project_id
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


def _lookback_days() -> int:
    raw = (request.args.get("days") or "").strip()
    try:
        days = int(raw) if raw else 7
    except ValueError:
        return 7
    return days if days in {1, 3, 7, 30} else 7


def _as_utc(dt: datetime | None) -> datetime | None:
    if not dt:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def _fetch_sipantau_dashboard(keyword_id: str | None = None, days: int = 7) -> dict | None:
    base = _sipantau_base()
    if not base:
        return None
    params = {"days": days}
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


_MONTHS = ("Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des")


def _empty_trend(days: int) -> dict:
    today = datetime.now(ZoneInfo("Asia/Jakarta"))
    labels = []
    for offset in range(days - 1, -1, -1):
        day = today - timedelta(days=offset)
        labels.append("Hari ini" if days == 1 else f"{day.day} {_MONTHS[day.month - 1]}")
    zeros = [0] * days
    return {"labels": labels, "positif": zeros, "negatif": zeros}


def _stub_metrics(days: int = 7) -> dict:
    return {
        "source": "sipantau_stub",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "days": days,
        "kpis": {
            "total_mention": 0,
            "sentiment_negative_pct": 0,
            "reach": 0,
            "active_issues": 0,
        },
        "trend_7d": _empty_trend(days),
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


_CONTENT_LABEL = {
    "draft": "Draf",
    "in_review": "Menunggu persetujuan",
    "approved": "Disetujui",
    "rejected": "Ditolak",
    "published": "Telah terbit",
}
_AGENDA_LABEL = {
    "planned": "Direncanakan",
    "in_production": "Produksi",
    "ready": "Siap tayang",
    "published": "Terbit",
    "cancelled": "Dibatalkan",
}
_MISSION_ACTION = {
    "like": "Menyukai",
    "share": "Membagikan",
    "comment": "Memberi komentar",
    "like_share_comment": "Menyukai, membagikan, dan mengomentari",
}


def _card(label, value, hint, tone):
    return {"label": label, "value": value, "hint": hint, "tone": tone}


def _task(title, meta, href):
    return {"title": title, "meta": meta, "href": href}


def _build_home(user, project_id: str | None) -> dict:
    role = user.role.code if user and user.role else "editor"
    name = (user.full_name if user else "") or "Pengguna"
    first = name

    if role == "pimpinan":
        return _home_pimpinan(project_id, first)
    if role == "media_kol_admin":
        return _home_media(first)
    if role == "opd_admin":
        return _home_opd(user, first)
    if role == "asn":
        return _home_asn(user, project_id, first)
    if role == "editor":
        return _home_editor(project_id, first)
    return _home_admin(project_id, first)


def _home_admin(project_id, first):
    queue = _work_queue(project_id)
    return {
        "layout": "monitor",
        "role": "super_admin",
        "eyebrow": "Super Admin",
        "title": f"Selamat datang, {first}",
        "subtitle": "Pantauan percakapan dan antrean yang masih menunggu tindakan.",
        "cards": queue["cards"],
        "tasks": queue["tasks"],
        "tasks_title": "Perlu ditindaklanjuti",
        "tasks_empty": "Tidak ada antrean yang mendesak.",
    }


def _home_editor(project_id, first):
    queue = _work_queue(project_id)
    return {
        "layout": "monitor",
        "role": "editor",
        "eyebrow": "Tim editor",
        "title": f"Pekerjaan hari ini, {first}",
        "subtitle": "Naskah, validasi, dan isu yang masih perlu diselesaikan.",
        "cards": queue["cards"],
        "tasks": queue["tasks"],
        "tasks_title": "Antrean produksi",
        "tasks_empty": "Antrean produksi sedang kosong.",
    }


def _work_queue(project_id):
    content_q = db.session.query(ContentItem.status, func.count(ContentItem.id))
    content_q = filter_query_by_issue_ids(content_q, ContentItem.issue_id, project_id)
    by_status = dict(content_q.group_by(ContentItem.status).all())
    val_q = OpdValidation.query.filter_by(status="waiting")
    val_q = filter_query_by_issue_ids(val_q, OpdValidation.issue_id, project_id)
    waiting = val_q.count()
    drafts = (
        filter_query_by_issue_ids(ContentItem.query, ContentItem.issue_id, project_id)
        .filter(ContentItem.status.in_(["draft", "in_review", "rejected"]))
        .order_by(ContentItem.updated_at.desc())
        .limit(5)
        .all()
    )
    pending_vals = (
        val_q.order_by(OpdValidation.requested_at.asc()).limit(4).all()
    )
    tasks = [
        _task(
            item.issue.title if item.issue else f"Validasi #{item.id}",
            f"Validasi · {item.opd_name}",
            "/validasi-opd",
        )
        for item in pending_vals
    ]
    tasks.extend(
        _task(item.title, _CONTENT_LABEL.get(item.status, item.status), f"/konten/{item.id}")
        for item in drafts
    )
    return {
        "cards": [
            _card("Draf", by_status.get("draft", 0), "Naskah yang masih disusun", "sky"),
            _card("Menunggu persetujuan", by_status.get("in_review", 0), "Perlu keputusan pimpinan", "amber"),
            _card("Validasi OPD", waiting, "Belum dijawab perangkat daerah", "rose"),
            _card("Siap sebar", by_status.get("approved", 0), "Konten yang sudah disetujui", "emerald"),
        ],
        "tasks": tasks[:6],
    }


def _home_pimpinan(project_id, first):
    issues = filter_issues_query(Issue.query, project_id).all()
    active = [i for i in issues if i.status in OPEN_STATUSES]
    critical = [i for i in active if i.risk_level in {"R3", "R4", "R5"}]
    critical.sort(key=lambda i: i.risk_level, reverse=True)
    waiting = filter_query_by_issue_ids(
        OpdValidation.query.filter_by(status="waiting"),
        OpdValidation.issue_id,
        project_id,
    ).count()
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    blasts = filter_query_by_issue_ids(
        MediaBlastLog.query.filter(MediaBlastLog.sent_at >= week_ago),
        MediaBlastLog.issue_id,
        project_id,
    ).count()
    return {
        "layout": "brief",
        "role": "pimpinan",
        "eyebrow": "Pimpinan",
        "title": f"Ringkasan untuk {first}",
        "subtitle": "Isu yang masih ditangani dan keputusan yang belum selesai.",
        "cards": [
            _card("Isu aktif", len(active), "Masih dalam penanganan", "sky"),
            _card("Risiko tinggi", len(critical), "Tingkat R3 ke atas", "rose"),
            _card("Validasi menunggu", waiting, "Belum dijawab OPD", "amber"),
            _card("Blast 7 hari", blasts, "Pengiriman ke mitra media", "emerald"),
        ],
        "tasks": [
            _task(
                i.title,
                f"{i.risk_level} · {_CONTENT_LABEL.get(i.status, {'open': 'Terbuka', 'validating': 'Validasi', 'producing': 'Produksi', 'approved': 'Disetujui', 'disseminated': 'Telah disebar', 'closed': 'Ditutup'}.get(i.status, i.status))}",
                f"/issues/{i.id}",
            )
            for i in critical[:5]
        ],
        "tasks_title": "Isu prioritas",
        "tasks_empty": "Tidak ada isu berisiko tinggi yang masih terbuka.",
        "links": [
            {"label": "Dashboard eksekutif", "href": "/executive"},
            {"label": "Crisis Room", "href": "/crisis-room"},
            {"label": "Unduh laporan", "href": "/reports"},
        ],
    }


def _home_media(first):
    partners = MediaPartner.query.filter_by(is_active=True).count()
    logs = MediaSlaLog.query.order_by(MediaSlaLog.created_at.desc()).limit(80).all()
    compliant = sum(1 for log in logs if log.sla_compliant)
    rate = round(100 * compliant / len(logs)) if logs else 0
    upcoming = (
        EditorialAgenda.query.filter(
            EditorialAgenda.planned_date >= date.today(),
            EditorialAgenda.status != "cancelled",
        )
        .order_by(EditorialAgenda.planned_date.asc())
        .limit(5)
        .all()
    )
    campaigns = (
        KolCampaign.query.filter(KolCampaign.status.in_(["planned", "in_progress"]))
        .order_by(KolCampaign.created_at.desc())
        .limit(4)
        .all()
    )
    partners_by_id = {p.id: p.name for p in KolPartner.query.all()}
    return {
        "layout": "desk",
        "role": "media_kol_admin",
        "eyebrow": "Media dan KOL",
        "title": f"Ruang tayang, {first}",
        "subtitle": "Kepatuhan mitra, agenda editorial, dan kampanye yang masih berjalan.",
        "cards": [
            _card("Mitra aktif", partners, "Media yang bisa dihubungi", "sky"),
            _card("Kepatuhan SLA", f"{rate}%", "Tayang dalam 60 menit", "emerald" if rate >= 60 else "amber"),
            _card("Agenda mendatang", len(upcoming), "Jadwal yang belum dibatalkan", "amber"),
            _card("Kampanye berjalan", len(campaigns), "KOL yang belum selesai", "violet"),
        ],
        "tasks": [
            _task(
                item.title,
                f"{item.planned_date.strftime('%d %b')} · {_AGENDA_LABEL.get(item.status, item.status)}",
                "/agenda",
            )
            for item in upcoming
        ]
        + [
            _task(
                item.title,
                partners_by_id.get(item.kol_id, "KOL"),
                "/kol",
            )
            for item in campaigns
        ],
        "tasks_title": "Jadwal dan kampanye",
        "tasks_empty": "Belum ada agenda atau kampanye yang menunggu.",
        "links": [
            {"label": "Media Hub", "href": "/media-hub"},
            {"label": "Agenda", "href": "/agenda"},
            {"label": "KOL", "href": "/kol"},
        ],
    }


def _home_opd(user, first):
    from app.api.validations import _scoped_validation_query

    waiting_q = _scoped_validation_query(user).filter_by(status="waiting")
    rows = waiting_q.order_by(OpdValidation.requested_at.asc()).limit(6).all()
    opd = (user.opd_name if user else "") or "perangkat daerah Anda"
    return {
        "layout": "desk",
        "role": "opd_admin",
        "eyebrow": "Admin OPD",
        "title": f"Validasi untuk {first}",
        "subtitle": f"Permintaan klarifikasi yang ditujukan ke {opd}.",
        "cards": [
            _card("Menunggu jawaban", waiting_q.count(), "Perlu ditanggapi", "amber"),
            _card("Sudah dijawab", _scoped_validation_query(user).filter(OpdValidation.status != "waiting").count(), "Tervalidasi atau ditolak", "emerald"),
        ],
        "tasks": [
            _task(
                item.issue.title if item.issue else f"Validasi #{item.id}",
                item.opd_name,
                "/validasi-opd",
            )
            for item in rows
        ],
        "tasks_title": "Permintaan yang belum dijawab",
        "tasks_empty": "Tidak ada permintaan validasi yang menunggu.",
        "links": [{"label": "Buka validasi OPD", "href": "/validasi-opd"}],
    }


def _home_asn(user, project_id, first):
    joined = {
        row.mission_id
        for row in MissionParticipation.query.filter_by(user_id=user.id).all()
    }
    active_q = Mission.query.filter_by(status="active")
    active_q = filter_query_by_issue_ids(active_q, Mission.issue_id, project_id)
    active = active_q.order_by(Mission.created_at.desc()).all()
    open_all = [m for m in active if m.id not in joined]
    open_missions = open_all[:5]
    return {
        "layout": "desk",
        "role": "asn",
        "eyebrow": "ASN Banten",
        "title": f"Misi Anda, {first}",
        "subtitle": "Amplifikasi resmi yang masih bisa diikuti.",
        "cards": [
            _card("Misi terbuka", len(open_all), "Belum Anda ikuti", "sky"),
            _card("Sudah diikuti", len(joined), "Partisipasi yang tercatat", "emerald"),
            _card("Misi berjalan", len(active), "Di project yang dipilih", "amber"),
        ],
        "tasks": [
            _task(
                m.title,
                f"{_MISSION_ACTION.get(m.action_type, 'Aksi')} · {len(m.participations)}/{m.target_count or 0}",
                "/missions",
            )
            for m in open_missions
        ],
        "tasks_title": "Misi yang bisa diikuti",
        "tasks_empty": "Semua misi aktif sudah Anda ikuti.",
        "links": [{"label": "Buka mission board", "href": "/missions"}],
    }


@bp.get("")
@jwt_required()
@role_required("super_admin", "editor", "pimpinan", "media_kol_admin", "opd_admin", "asn")
def intel_dashboard():
    """
    Ringkasan intelijen untuk beranda.
    Metrik mention/sentimen/reach: dari SIPANTAU (fallback stub jika down).
    Alert isu aktif: dari database Crisis Room.
    Query: project_id / keyword_id — filter KPI + isu terkait project SIPANTAU.
    """
    project_id = (request.args.get("project_id") or request.args.get("keyword_id") or "").strip() or None
    days = _lookback_days()
    jakarta = ZoneInfo("Asia/Jakarta")
    start_local = datetime.now(jakarta).replace(hour=0, minute=0, second=0, microsecond=0)
    since = (start_local - timedelta(days=days - 1)).astimezone(timezone.utc)
    user = get_current_user()
    role = user.role.code if user and user.role else ""
    home = _build_home(user, project_id)
    if role not in {"super_admin", "editor"}:
        return jsonify(
            {
                "data": {
                    "source": "role_home",
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                    "project_id": project_id,
                    "home": home,
                    "kpis": {},
                    "alerts": [],
                    "platforms": [],
                    "trend_7d": None,
                }
            }
        )

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

    # Pull fresh SIPANTAU negatives into Crisis Room when source=sipantau
    try:
        from app.services.app_settings import get_news_source
        from app.services.sipantau_sync import sync_sipantau_crises

        if get_news_source() == "sipantau":
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

    active = [
        issue
        for issue in active
        if (_as_utc(issue.created_at) or since) >= since
    ]

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

    sip = _fetch_sipantau_dashboard(project_id, days) or _stub_metrics(days)
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
                "days": days,
                "trend_7d": sip.get("trend_7d") or _empty_trend(days),
                "alerts": alerts,
                "platforms": sip.get("platforms") or [],
                "home": home,
            }
        }
    )
