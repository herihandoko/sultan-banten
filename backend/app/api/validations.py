"""F.03 — Validasi Data ke OPD Teknis."""

from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models import AuditLog, Issue, OpdValidation, User
from app.utils.auth import get_current_user, role_required
from app.utils.pagination import paginate
from app.utils.project_scope import filter_query_by_issue_ids, request_project_id

bp = Blueprint("validations", __name__)


def _validation_payload(item: OpdValidation, include_issue: bool = False) -> dict:
    data = item.to_dict()
    if include_issue and item.issue:
        data["issue"] = {
            "id": item.issue.id,
            "title": item.issue.title,
            "summary": item.issue.summary,
            "why_now": item.issue.why_now,
            "risk_level": item.issue.risk_level,
            "status": item.issue.status,
            "evidence": [e.to_dict() for e in item.issue.evidence],
        }
    return data


@bp.get("")
@jwt_required()
@role_required("super_admin", "editor", "opd_admin", "pimpinan")
def list_validations():
    user = get_current_user()
    status = request.args.get("status")
    q = (request.args.get("q") or "").strip()
    query = OpdValidation.query
    query = filter_query_by_issue_ids(query, OpdValidation.issue_id, request_project_id())

    # OPD admin only sees validations for their OPD (or assigned to them)
    if user and user.role and user.role.code == "opd_admin":
        filters = [OpdValidation.assigned_to == user.id]
        if user.opd_name:
            filters.append(OpdValidation.opd_name == user.opd_name)
        query = query.filter(db.or_(*filters))

    if status:
        query = query.filter_by(status=status)
    if q:
        like = f"%{q}%"
        query = query.outerjoin(Issue).filter(
            db.or_(
                OpdValidation.opd_name.ilike(like),
                OpdValidation.response_notes.ilike(like),
                Issue.title.ilike(like),
            )
        )

    query = query.order_by(OpdValidation.requested_at.desc())
    return jsonify(paginate(query, lambda i: _validation_payload(i, include_issue=True)))


@bp.get("/<int:validation_id>")
@jwt_required()
@role_required("super_admin", "editor", "opd_admin", "pimpinan")
def get_validation(validation_id: int):
    item = OpdValidation.query.get_or_404(validation_id)
    user = get_current_user()
    if user and user.role and user.role.code == "opd_admin":
        allowed = item.assigned_to == user.id or (
            user.opd_name and item.opd_name == user.opd_name
        )
        if not allowed:
            return jsonify({"error": "Forbidden"}), 403
    return jsonify({"data": _validation_payload(item, include_issue=True)})


@bp.post("/issues/<int:issue_id>")
@jwt_required()
@role_required("super_admin", "editor")
def request_validation(issue_id: int):
    """Kirim permintaan validasi data ke OPD teknis."""
    issue = Issue.query.get_or_404(issue_id)
    data = request.get_json(silent=True) or {}
    from app.models import Opd

    opd_id = data.get("opd_id")
    opd_name = (data.get("opd_name") or "").strip()
    opd = None
    if opd_id:
        opd = Opd.query.filter_by(id=opd_id, is_active=True).first()
    elif opd_name:
        opd = Opd.query.filter_by(name=opd_name, is_active=True).first()
    if not opd:
        return jsonify({"error": "Pilih OPD dari master OPD"}), 400
    opd_name = opd.name

    user = get_current_user()
    assigned_to = data.get("assigned_to")
    if assigned_to:
        assignee = User.query.get(assigned_to)
        if not assignee:
            return jsonify({"error": "User OPD tidak ditemukan"}), 400
        if assignee.opd_name and assignee.opd_name != opd_name:
            return jsonify({"error": "User OPD tidak sesuai dengan OPD yang dipilih"}), 400
    else:
        # Auto-assign first active OPD admin matching opd_name
        from app.models import Role

        assignee = (
            User.query.join(Role)
            .filter(
                User.is_active.is_(True),
                User.opd_name == opd_name,
                Role.code == "opd_admin",
            )
            .first()
        )
        assigned_to = assignee.id if assignee else None

    validation = OpdValidation(
        issue_id=issue.id,
        opd_name=opd_name,
        requested_by=user.id if user else None,
        assigned_to=assigned_to,
        status="waiting",
        request_notes=data.get("request_notes"),
    )
    db.session.add(validation)
    db.session.flush()

    if issue.status == "open":
        issue.status = "validating"

    db.session.add(
        AuditLog(
            user_id=user.id if user else None,
            action="request_opd_validation",
            entity_type="opd_validation",
            entity_id=validation.id,
            details={"issue_id": issue.id, "opd_name": opd_name, "opd_id": opd.id},
            ip_address=request.remote_addr,
        )
    )
    db.session.commit()
    return jsonify({"data": _validation_payload(validation, include_issue=True)}), 201


@bp.patch("/<int:validation_id>/respond")
@jwt_required()
@role_required("super_admin", "opd_admin")
def respond_validation(validation_id: int):
    """OPD merespon: validated | rejected."""
    item = OpdValidation.query.get_or_404(validation_id)
    if item.status != "waiting":
        return jsonify({"error": "Validasi sudah direspon"}), 400

    user = get_current_user()
    if user and user.role and user.role.code == "opd_admin":
        allowed = item.assigned_to == user.id or (
            user.opd_name and item.opd_name == user.opd_name
        )
        if not allowed:
            return jsonify({"error": "Forbidden"}), 403

    data = request.get_json(silent=True) or {}
    decision = data.get("status")
    if decision not in {"validated", "rejected"}:
        return jsonify({"error": "Status harus validated atau rejected"}), 400

    item.status = decision
    item.response_notes = data.get("response_notes")
    item.response_data = data.get("response_data")
    item.responded_at = datetime.now(timezone.utc)
    if not item.assigned_to and user:
        item.assigned_to = user.id

    # If all validations for issue are done and at least one validated → producing
    issue = item.issue
    siblings = OpdValidation.query.filter_by(issue_id=issue.id).all()
    if siblings and all(s.status != "waiting" for s in siblings):
        if any(s.status == "validated" for s in siblings):
            issue.status = "producing"
        else:
            issue.status = "open"

    db.session.add(
        AuditLog(
            user_id=user.id if user else None,
            action="respond_opd_validation",
            entity_type="opd_validation",
            entity_id=item.id,
            details={"status": decision, "issue_id": issue.id},
            ip_address=request.remote_addr,
        )
    )
    db.session.commit()
    return jsonify({"data": _validation_payload(item, include_issue=True)})


@bp.get("/opd-options")
@jwt_required()
@role_required("super_admin", "editor")
def opd_options():
    """Daftar OPD admin yang bisa ditugaskan."""
    from app.models import Role

    users = (
        User.query.join(Role)
        .filter(User.is_active.is_(True), Role.code == "opd_admin")
        .order_by(User.opd_name, User.full_name)
        .all()
    )
    return jsonify(
        {
            "data": [
                {
                    "id": u.id,
                    "full_name": u.full_name,
                    "opd_name": u.opd_name,
                    "username": u.username,
                }
                for u in users
            ]
        }
    )
