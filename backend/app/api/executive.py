"""F.14 Dashboard Eksekutif — ringkasan untuk pimpinan."""

from datetime import datetime, timedelta, timezone

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func

from app.extensions import db
from app.models import (
    ContentItem,
    Issue,
    KolCampaign,
    MediaBlastLog,
    Mission,
    MissionParticipation,
    OpdValidation,
)
from app.utils.auth import role_required

bp = Blueprint("executive", __name__)


@bp.get("/dashboard")
@jwt_required()
@role_required("super_admin", "pimpinan", "editor")
def executive_dashboard():
    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)

    # Issues / crisis
    issues = Issue.query.all()
    open_statuses = {"open", "validating", "producing", "approved"}
    active_issues = [i for i in issues if i.status in open_statuses]
    risk_counts = {}
    status_counts = {}
    for i in issues:
        risk_counts[i.risk_level] = risk_counts.get(i.risk_level, 0) + 1
        status_counts[i.status] = status_counts.get(i.status, 0) + 1

    critical_active = [
        i.to_dict()
        for i in sorted(
            [x for x in active_issues if x.risk_level in {"R3", "R4", "R5"}],
            key=lambda x: x.risk_level,
            reverse=True,
        )[:5]
    ]

    # Validations waiting
    waiting_validations = OpdValidation.query.filter_by(status="waiting").count()

    # Content pipeline
    content_by_status = dict(
        db.session.query(ContentItem.status, func.count(ContentItem.id))
        .group_by(ContentItem.status)
        .all()
    )

    # Media blast (7 days)
    recent_blasts = MediaBlastLog.query.filter(MediaBlastLog.sent_at >= week_ago).all()
    blast_sent = sum((b.result or {}).get("sent", 0) for b in recent_blasts)
    blast_failed = sum((b.result or {}).get("failed", 0) for b in recent_blasts)

    # ASN participation
    asn_total = MissionParticipation.query.count()
    asn_by_opd = [
        {"opd_name": r[0] or "Tanpa OPD", "total": r[1]}
        for r in (
            db.session.query(
                MissionParticipation.opd_name,
                func.count(MissionParticipation.id),
            )
            .group_by(MissionParticipation.opd_name)
            .order_by(func.count(MissionParticipation.id).desc())
            .limit(8)
            .all()
        )
    ]
    active_missions = Mission.query.filter_by(status="active").count()

    # KOL
    kol_campaigns = KolCampaign.query.all()
    kol_by_status = {}
    kol_views = 0
    for c in kol_campaigns:
        kol_by_status[c.status] = kol_by_status.get(c.status, 0) + 1
        kol_views += c.views or 0

    # Executive brief (synthetic from local data; Mata Bathin brief when integrated)
    top_risk = critical_active[0] if critical_active else None
    brief = {
        "generated_at": now.isoformat(),
        "source": "sultan_banten",
        "headline": (
            f"{len(active_issues)} isu aktif"
            + (f", prioritas {top_risk['risk_level']}: {top_risk['title']}" if top_risk else "")
        ),
        "summary": (
            f"Validasi OPD menunggu: {waiting_validations}. "
            f"Konten approved: {content_by_status.get('approved', 0) + content_by_status.get('published', 0)}. "
            f"Blast 7 hari: {len(recent_blasts)} pengiriman. "
            f"Misi ASN aktif: {active_missions}. "
            f"Reach KOL (views): {kol_views:,}."
        ),
        "recommendations": [
            "Selesaikan validasi OPD yang masih waiting sebelum produksi konten baru.",
            "Pastikan konten approved segera di-blast ke media mitra.",
            "Aktifkan Mission Board ASN untuk amplifikasi organik.",
        ],
    }

    return jsonify(
        {
            "data": {
                "generated_at": now.isoformat(),
                "kpis": {
                    "active_issues": len(active_issues),
                    "critical_issues": len(
                        [i for i in active_issues if i.risk_level in {"R3", "R4", "R5"}]
                    ),
                    "waiting_validations": waiting_validations,
                    "content_in_review": content_by_status.get("in_review", 0),
                    "blasts_7d": len(recent_blasts),
                    "blast_deliveries_7d": blast_sent,
                    "asn_participations": asn_total,
                    "active_missions": active_missions,
                    "kol_campaigns": len(kol_campaigns),
                    "kol_views": kol_views,
                },
                "risk_distribution": [
                    {"level": level, "count": risk_counts.get(level, 0)}
                    for level in ["R0", "R1", "R2", "R3", "R4", "R5"]
                ],
                "status_distribution": [
                    {"status": k, "count": v} for k, v in sorted(status_counts.items())
                ],
                "content_pipeline": [
                    {"status": k, "count": v} for k, v in sorted(content_by_status.items())
                ],
                "asn_by_opd": asn_by_opd,
                "kol_by_status": [
                    {"status": k, "count": v} for k, v in sorted(kol_by_status.items())
                ],
                "media_blast_7d": {
                    "blasts": len(recent_blasts),
                    "sent": blast_sent,
                    "failed": blast_failed,
                },
                "critical_issues": critical_active,
                "executive_brief": brief,
            }
        }
    )
