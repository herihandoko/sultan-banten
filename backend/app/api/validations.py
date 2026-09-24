"""F.03 — Validasi Data ke OPD Teknis."""

from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models import AuditLog, Issue, OpdValidation, User
from app.services.alerts import notify_content_ready
from app.utils.auth import get_current_user, role_required
from app.utils.pagination import paginate
from app.utils.project_scope import filter_query_by_issue_ids, request_project_id

bp = Blueprint("validations", __name__)


def _scoped_validation_query(user):
    """Daftar validasi sesuai peran dan project yang sedang dipilih."""
    query = OpdValidation.query
    query = filter_query_by_issue_ids(query, OpdValidation.issue_id, request_project_id())
    if user and user.role and user.role.code == "opd_admin":
        filters = [OpdValidation.assigned_to == user.id]
        if user.opd_name:
            filters.append(OpdValidation.opd_name == user.opd_name)
        query = query.filter(db.or_(*filters))
    return query


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
            "source_label": item.issue.primary_source_label(),
            "source_url": item.issue.primary_source_url(),
            "evidence": [e.to_dict() for e in item.issue.evidence],
        }
    return data


def _validation_url(validation_id: int) -> str:
    from app.services.role_notify import public_url

    return public_url(f"/validasi-opd?id={validation_id}")


def _opd_admins(opd_name: str) -> list[User]:
    from app.models import Role

    return (
        User.query.join(Role)
        .filter(
            User.is_active.is_(True),
            User.opd_name == opd_name,
            Role.code == "opd_admin",
        )
        .all()
    )


def _notify_validation_request(issue, validation, requester, recipients: list[User]) -> list[dict]:
    """Email + WhatsApp ke admin OPD. Kegagalan kirim tidak membatalkan permintaan."""
    from app.services.messaging import send_email, send_whatsapp

    people = [person for person in recipients if person]
    who = (requester.full_name or requester.username) if requester else "SIAGAPIM"
    notes = (validation.request_notes or "").strip() or "-"
    link = _validation_url(validation.id)
    subject = f"Permintaan validasi isu — {issue.title}"
    body = (
        "Permintaan validasi data dari SIAGAPIM.\n\n"
        f"Isu: {issue.title}\n"
        f"OPD: {validation.opd_name}\n"
        f"Catatan: {notes}\n"
        f"Diminta oleh: {who}\n\n"
        "Buka permintaan validasi:\n"
        f"{link}"
    )

    if not people:
        return [
            {
                "channel": "whatsapp",
                "status": "skipped",
                "error": "Tidak ada admin OPD yang bisa dihubungi",
            },
            {
                "channel": "email",
                "status": "skipped",
                "error": "Tidak ada admin OPD yang bisa dihubungi",
            },
        ]

    results = []
    for person in people:
        name = person.full_name or person.username
        if person.phone:
            results.append(send_whatsapp(person.phone, body))
        else:
            results.append(
                {
                    "channel": "whatsapp",
                    "to": name,
                    "status": "skipped",
                    "error": "Nomor WhatsApp admin kosong",
                }
            )
        if person.email:
            results.append(send_email(person.email, subject, body))
        else:
            results.append(
                {
                    "channel": "email",
                    "to": name,
                    "status": "skipped",
                    "error": "Email admin kosong",
                }
            )
    return results


@bp.get("")
@jwt_required()
@role_required("super_admin", "editor", "opd_admin", "pimpinan")
def list_validations():
    user = get_current_user()
    status = request.args.get("status")
    q = (request.args.get("q") or "").strip()
    query = _scoped_validation_query(user)

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


@bp.get("/summary")
@jwt_required()
@role_required("super_admin", "editor", "opd_admin", "pimpinan")
def validation_summary():
    """Jumlah permintaan yang masih menunggu, untuk badge menu."""
    user = get_current_user()
    waiting = _scoped_validation_query(user).filter_by(status="waiting").count()
    return jsonify({"data": {"waiting": waiting}})


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

    explicit_assignee = bool(data.get("assigned_to"))
    targets = [assignee] if explicit_assignee and assignee else _opd_admins(opd_name)
    delivery = _notify_validation_request(issue, validation, user, targets)
    payload = _validation_payload(validation, include_issue=True)
    payload["delivery"] = delivery
    return jsonify({"data": payload}), 201


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
            notify_content_ready(issue)
            from app.services.role_notify import notify_editors_content_ready

            try:
                notify_editors_content_ready(issue)
            except Exception:
                from flask import current_app

                current_app.logger.exception("Gagal mengirim notifikasi konten ke editor")
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
