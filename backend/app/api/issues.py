"""Crisis Room issue endpoints."""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models import AuditLog, Issue, IssueEvidence
from app.utils.auth import get_current_user, role_required
from app.utils.pagination import paginate

bp = Blueprint("issues", __name__)


# Allow OPD to list issues they are validating (via validation assignment)
@bp.get("")
@jwt_required()
@role_required("super_admin", "editor", "pimpinan", "media_kol_admin", "opd_admin")
def list_issues():
    status = request.args.get("status")
    risk_level = request.args.get("risk_level")
    source = request.args.get("source")
    q = (request.args.get("q") or "").strip()
    user = get_current_user()
    query = Issue.query

    if user and user.role and user.role.code == "opd_admin":
        from app.models import OpdValidation

        issue_ids = [
            v.issue_id
            for v in OpdValidation.query.filter(
                db.or_(
                    OpdValidation.assigned_to == user.id,
                    OpdValidation.opd_name == (user.opd_name or ""),
                )
            ).all()
        ]
        query = query.filter(Issue.id.in_(issue_ids or [-1]))

    if status:
        query = query.filter_by(status=status)
    if risk_level:
        query = query.filter_by(risk_level=risk_level)
    if source:
        query = query.filter_by(source=source)
    if q:
        like = f"%{q}%"
        query = query.filter(
            db.or_(
                Issue.title.ilike(like),
                Issue.summary.ilike(like),
                Issue.mb_alert_id.ilike(like),
            )
        )
    query = query.order_by(Issue.created_at.desc())
    return jsonify(paginate(query, lambda i: i.to_dict()))


@bp.get("/<int:issue_id>")
@jwt_required()
@role_required("super_admin", "editor", "pimpinan", "opd_admin", "media_kol_admin")
def get_issue(issue_id: int):
    issue = Issue.query.get_or_404(issue_id)
    user = get_current_user()
    if user and user.role and user.role.code == "opd_admin":
        from app.models import OpdValidation

        allowed = OpdValidation.query.filter(
            OpdValidation.issue_id == issue.id,
            db.or_(
                OpdValidation.assigned_to == user.id,
                OpdValidation.opd_name == (user.opd_name or ""),
            ),
        ).first()
        if not allowed:
            return jsonify({"error": "Forbidden"}), 403
    return jsonify({"data": issue.to_dict(include_relations=True)})


@bp.post("")
@jwt_required()
@role_required("super_admin", "editor")
def create_issue():
    """Manual issue input (fallback when Mata Bathin is unavailable)."""
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"error": "Judul isu wajib diisi"}), 400

    user = get_current_user()
    issue = Issue(
        title=title,
        summary=data.get("summary"),
        why_now=data.get("why_now"),
        risk_level=data.get("risk_level", "R0"),
        risk_assessment=data.get("risk_assessment"),
        recommended_actions=data.get("recommended_actions"),
        narrative_card=data.get("narrative_card"),
        status="open",
        source="manual",
        created_by=user.id if user else None,
        mb_alert_id=data.get("mb_alert_id"),
    )
    db.session.add(issue)
    db.session.flush()

    for item in data.get("evidence") or []:
        db.session.add(
            IssueEvidence(
                issue_id=issue.id,
                title=item.get("title"),
                url=item.get("url"),
                source_name=item.get("source_name"),
                evidence_type=item.get("evidence_type"),
                snippet=item.get("snippet"),
            )
        )

    db.session.add(
        AuditLog(
            user_id=user.id if user else None,
            action="create_issue",
            entity_type="issue",
            entity_id=issue.id,
            details={"source": "manual"},
            ip_address=request.remote_addr,
        )
    )

    from app.services.alerts import maybe_alert_on_issue

    maybe_alert_on_issue(issue, force=True)

    db.session.commit()
    return jsonify({"data": issue.to_dict(include_relations=True)}), 201


@bp.patch("/<int:issue_id>/status")
@jwt_required()
@role_required("super_admin", "editor")
def update_issue_status(issue_id: int):
    issue = Issue.query.get_or_404(issue_id)
    data = request.get_json(silent=True) or {}
    new_status = data.get("status")
    allowed = {"open", "validating", "producing", "approved", "disseminated", "closed"}
    if new_status not in allowed:
        return jsonify({"error": f"Status tidak valid. Pilih: {', '.join(sorted(allowed))}"}), 400

    old = issue.status
    issue.status = new_status
    if new_status == "closed" and not issue.closed_at:
        from datetime import datetime, timezone

        issue.closed_at = datetime.now(timezone.utc)

    user = get_current_user()
    db.session.add(
        AuditLog(
            user_id=user.id if user else None,
            action="update_issue_status",
            entity_type="issue",
            entity_id=issue.id,
            details={"from": old, "to": new_status},
            ip_address=request.remote_addr,
        )
    )
    db.session.commit()

    feedback_result = None
    if new_status in {"disseminated", "closed"}:
        from app.services.feedback import push_issue_feedback

        feedback_result = push_issue_feedback(
            issue, notes=data.get("feedback_notes")
        )

    payload = issue.to_dict()
    if feedback_result is not None:
        payload["mata_bathin_feedback"] = {
            "sent": feedback_result.get("sent"),
            "reason": feedback_result.get("reason"),
        }
    return jsonify({"data": payload})
