"""F.10 Mission Board ASN + F.11 Log Partisipasi."""

from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import func

from app.extensions import db
from app.models import AuditLog, Issue, Mission, MissionParticipation, User
from app.utils.auth import get_current_user, role_required
from app.utils.pagination import paginate

bp = Blueprint("missions", __name__)

ACTION_TYPES = {"like", "share", "comment", "like_share_comment"}


def _mission_payload(mission: Mission, user: User | None = None) -> dict:
    data = mission.to_dict(include_stats=True)
    data["participations"] = [
        {
            **p.to_dict(),
            "user_name": User.query.get(p.user_id).full_name if User.query.get(p.user_id) else None,
        }
        for p in sorted(mission.participations, key=lambda x: x.completed_at or datetime.min, reverse=True)
    ]
    if user:
        data["joined"] = any(p.user_id == user.id for p in mission.participations)
    return data


@bp.get("")
@jwt_required()
@role_required("super_admin", "editor", "asn", "pimpinan", "media_kol_admin")
def list_missions():
    status = request.args.get("status", "active")
    q = (request.args.get("q") or "").strip()
    action_type = request.args.get("action_type")
    query = Mission.query
    if status != "all":
        query = query.filter_by(status=status)
    if action_type:
        query = query.filter_by(action_type=action_type)
    if q:
        like = f"%{q}%"
        query = query.filter(
            db.or_(
                Mission.title.ilike(like),
                Mission.instruction.ilike(like),
                Mission.target_url.ilike(like),
            )
        )
    query = query.order_by(Mission.created_at.desc())
    user = get_current_user()
    return jsonify(paginate(query, lambda m: _mission_payload(m, user)))


@bp.get("/stats")
@jwt_required()
@role_required("super_admin", "editor", "pimpinan", "media_kol_admin")
def participation_stats():
    """Rekap partisipasi ASN per OPD (F.11)."""
    rows = (
        db.session.query(
            MissionParticipation.opd_name,
            func.count(MissionParticipation.id).label("total"),
        )
        .group_by(MissionParticipation.opd_name)
        .order_by(func.count(MissionParticipation.id).desc())
        .all()
    )
    return jsonify(
        {
            "data": [
                {"opd_name": r.opd_name or "Tanpa OPD", "total": r.total} for r in rows
            ],
            "grand_total": sum(r.total for r in rows),
        }
    )


@bp.get("/issues-options")
@jwt_required()
@role_required("super_admin", "editor", "media_kol_admin")
def issue_options():
    issues = Issue.query.order_by(Issue.created_at.desc()).limit(50).all()
    return jsonify(
        {
            "data": [
                {"id": i.id, "title": i.title, "status": i.status, "risk_level": i.risk_level}
                for i in issues
            ]
        }
    )


@bp.get("/<int:mission_id>")
@jwt_required()
@role_required("super_admin", "editor", "asn", "pimpinan", "media_kol_admin")
def get_mission(mission_id: int):
    mission = Mission.query.get_or_404(mission_id)
    return jsonify({"data": _mission_payload(mission, get_current_user())})


@bp.post("")
@jwt_required()
@role_required("super_admin", "editor", "media_kol_admin")
def create_mission():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    instruction = (data.get("instruction") or "").strip()
    if not title or not instruction:
        return jsonify({"error": "Judul dan instruksi wajib diisi"}), 400

    action_type = data.get("action_type", "like_share_comment")
    if action_type not in ACTION_TYPES:
        return jsonify({"error": f"action_type: {', '.join(sorted(ACTION_TYPES))}"}), 400

    issue_id = data.get("issue_id")
    if issue_id and not Issue.query.get(issue_id):
        return jsonify({"error": "Isu tidak ditemukan"}), 404

    user = get_current_user()
    starts_at = _parse_dt(data.get("starts_at"))
    ends_at = _parse_dt(data.get("ends_at"))

    mission = Mission(
        issue_id=issue_id,
        title=title,
        instruction=instruction,
        target_url=data.get("target_url"),
        action_type=action_type,
        target_count=int(data.get("target_count") or 0),
        starts_at=starts_at,
        ends_at=ends_at,
        status="active",
        created_by=user.id if user else None,
    )
    db.session.add(mission)
    db.session.flush()
    db.session.add(
        AuditLog(
            user_id=user.id if user else None,
            action="create_mission",
            entity_type="mission",
            entity_id=mission.id,
            ip_address=request.remote_addr,
        )
    )
    db.session.commit()
    return jsonify({"data": _mission_payload(mission, user)}), 201


@bp.patch("/<int:mission_id>/status")
@jwt_required()
@role_required("super_admin", "editor", "media_kol_admin")
def update_mission_status(mission_id: int):
    mission = Mission.query.get_or_404(mission_id)
    data = request.get_json(silent=True) or {}
    new_status = data.get("status")
    if new_status not in {"active", "completed", "cancelled"}:
        return jsonify({"error": "status: active, completed, cancelled"}), 400
    mission.status = new_status
    db.session.commit()
    return jsonify({"data": _mission_payload(mission, get_current_user())})


@bp.post("/<int:mission_id>/join")
@jwt_required()
@role_required("super_admin", "asn")
def join_mission(mission_id: int):
    """ASN mencatat partisipasi (F.11)."""
    mission = Mission.query.get_or_404(mission_id)
    if mission.status != "active":
        return jsonify({"error": "Misi tidak aktif"}), 400

    user = get_current_user()
    existing = MissionParticipation.query.filter_by(
        mission_id=mission.id, user_id=user.id
    ).first()
    if existing:
        return jsonify({"error": "Anda sudah mencatat partisipasi untuk misi ini"}), 409

    data = request.get_json(silent=True) or {}
    participation = MissionParticipation(
        mission_id=mission.id,
        user_id=user.id,
        opd_name=data.get("opd_name") or user.opd_name,
        proof_url=data.get("proof_url"),
        notes=data.get("notes"),
    )
    db.session.add(participation)

    # Auto-complete mission if target reached
    if mission.target_count and len(mission.participations) + 1 >= mission.target_count:
        mission.status = "completed"

    db.session.add(
        AuditLog(
            user_id=user.id,
            action="join_mission",
            entity_type="mission",
            entity_id=mission.id,
            ip_address=request.remote_addr,
        )
    )
    db.session.commit()
    return jsonify({"data": _mission_payload(mission, user)}), 201


def _parse_dt(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
