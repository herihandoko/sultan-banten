"""Intel overview dashboard — ringkasan situasi publik (Mata Bathin style)."""

from datetime import datetime, timedelta, timezone

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from app.models import Issue
from app.utils.auth import role_required

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


@bp.get("")
@jwt_required()
@role_required("super_admin", "editor", "pimpinan", "media_kol_admin", "opd_admin")
def intel_dashboard():
    """
    Ringkasan intelijen untuk beranda.
    Metrik mention/sentimen/reach: stub demo (nanti diganti Mata Bathin API).
    Alert isu aktif: dari database Crisis Room.
    """
    issues = Issue.query.order_by(Issue.created_at.desc()).all()
    active = [i for i in issues if i.status in OPEN_STATUSES]

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

    # Demo fallback if no active issues — mirror lampiran
    if not alerts:
        alerts = [
            {
                "id": None,
                "title": "Isu jembatan rusak",
                "severity": "tinggi",
                "risk_level": "R4",
                "status": "open",
                "ago": "12 menit lalu",
            },
            {
                "id": None,
                "title": "Keluhan layanan RSUD",
                "severity": "sedang",
                "risk_level": "R2",
                "status": "open",
                "ago": "40 menit lalu",
            },
            {
                "id": None,
                "title": "Hoaks bansos palsu",
                "severity": "sedang",
                "risk_level": "R3",
                "status": "validating",
                "ago": "1 jam lalu",
            },
        ]

    # Deterministic demo series (Sen–Min) — replace with Mata Bathin later
    trend = {
        "labels": ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"],
        "positif": [42, 48, 45, 58, 55, 62, 60],
        "negatif": [38, 35, 40, 32, 36, 28, 30],
    }

    platforms = [
        {"key": "twitter", "label": "X/Twitter", "count": 1920},
        {"key": "news", "label": "Portal berita", "count": 840},
        {"key": "instagram", "label": "Instagram", "count": 1150},
        {"key": "whatsapp", "label": "Grup WA", "count": 902},
    ]

    total_mention = sum(p["count"] for p in platforms)
    # Scale to look like lampiran (~4812) while staying consistent with platform sum
    if total_mention < 4000:
        total_mention = 4812

    return jsonify(
        {
            "data": {
                "source": "mata_bathin_stub",
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "kpis": {
                    "total_mention": total_mention,
                    "sentiment_negative_pct": 31,
                    "reach": 2_100_000,
                    "active_issues": len(active) if active else 7,
                },
                "trend_7d": trend,
                "alerts": alerts,
                "platforms": platforms,
            }
        }
    )
