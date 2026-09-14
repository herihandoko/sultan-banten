"""F.02 Crisis Alert API."""

from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models import CrisisAlert
from app.services.alerts import create_crisis_alert, scan_overdue_responses
from app.utils.auth import get_current_user, role_required
from app.utils.pagination import paginate
from app.utils.project_scope import filter_query_by_issue_ids, request_project_id

bp = Blueprint("alerts", __name__)


@bp.get("")
@jwt_required()
@role_required("super_admin", "editor", "pimpinan", "media_kol_admin")
def list_alerts():
    unread_only = request.args.get("unread") == "1"
    query = CrisisAlert.query
    query = filter_query_by_issue_ids(query, CrisisAlert.issue_id, request_project_id())
    if unread_only:
        query = query.filter_by(is_read=False)
    query = query.order_by(CrisisAlert.created_at.desc())
    result = paginate(query, lambda a: a.to_dict(), default_per_page=20)
    unread_q = CrisisAlert.query.filter_by(is_read=False)
    unread_q = filter_query_by_issue_ids(unread_q, CrisisAlert.issue_id, request_project_id())
    result["unread_count"] = unread_q.count()
    return jsonify(result)


@bp.post("/<int:alert_id>/read")
@jwt_required()
@role_required("super_admin", "editor", "pimpinan", "media_kol_admin")
def mark_read(alert_id: int):
    alert = CrisisAlert.query.get_or_404(alert_id)
    alert.is_read = True
    alert.read_at = datetime.now(timezone.utc)
    db.session.commit()
    return jsonify({"data": alert.to_dict()})


@bp.post("/read-all")
@jwt_required()
@role_required("super_admin", "editor", "pimpinan", "media_kol_admin")
def mark_all_read():
    now = datetime.now(timezone.utc)
    CrisisAlert.query.filter_by(is_read=False).update(
        {"is_read": True, "read_at": now},
        synchronize_session=False,
    )
    db.session.commit()
    return jsonify({"message": "ok"})


@bp.post("/scan-overdue")
@jwt_required()
@role_required("super_admin", "editor")
def scan_overdue():
    """Manual/cron trigger: cek isu R3+ yang lewat batas respons."""
    created = scan_overdue_responses()
    return jsonify({"created": len(created), "data": [a.to_dict() for a in created]})


@bp.post("/test")
@jwt_required()
@role_required("super_admin")
def test_alert():
    """Kirim alert demo untuk uji widget."""
    user = get_current_user()
    alert = create_crisis_alert(
        issue=None,
        alert_type="manual",
        title="TEST ALERT SIAGAPIM",
        message=f"Alert uji dari {user.full_name if user else 'system'}. Channel web + WA + Telegram (mock).",
        risk_level="R3",
        severity="high",
    )
    db.session.commit()
    return jsonify({"data": alert.to_dict()}), 201
