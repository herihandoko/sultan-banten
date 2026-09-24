"""F.04 — Hub Konten Klarifikasi + approval."""

from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models import AuditLog, ContentApproval, ContentItem, CrisisAlert, Issue
from app.utils.auth import get_current_user, role_required
from app.utils.pagination import paginate
from app.utils.project_scope import filter_issues_query, filter_query_by_issue_ids, request_project_id

bp = Blueprint("content", __name__)

CONTENT_TYPES = {"text_release", "infographic", "video"}
EDITABLE_STATUSES = {"draft", "rejected"}


def _content_payload(item: ContentItem, include_approvals: bool = False, include_issue: bool = False):
    data = item.to_dict(include_approvals=include_approvals)
    if include_issue and item.issue:
        data["issue"] = {
            "id": item.issue.id,
            "title": item.issue.title,
            "status": item.issue.status,
            "risk_level": item.issue.risk_level,
            "narrative_card": item.issue.narrative_card,
            "summary": item.issue.summary,
        }
    return data


@bp.get("")
@jwt_required()
@role_required("super_admin", "editor", "pimpinan")
def list_content():
    status = request.args.get("status")
    issue_id = request.args.get("issue_id", type=int)
    content_type = request.args.get("content_type")
    q = (request.args.get("q") or "").strip()
    query = ContentItem.query
    query = filter_query_by_issue_ids(query, ContentItem.issue_id, request_project_id())
    if status:
        query = query.filter_by(status=status)
    if issue_id:
        query = query.filter_by(issue_id=issue_id)
    if content_type:
        query = query.filter_by(content_type=content_type)
    if q:
        like = f"%{q}%"
        query = query.filter(
            db.or_(
                ContentItem.title.ilike(like),
                ContentItem.body.ilike(like),
            )
        )
    query = query.order_by(ContentItem.updated_at.desc())
    payload = paginate(query, lambda i: _content_payload(i, include_issue=True))
    payload["summary"] = _content_summary()
    return jsonify(payload)


def _content_summary():
    """Hitungan pipeline konten di proyek aktif, lepas dari filter halaman."""

    def scoped():
        return filter_query_by_issue_ids(
            ContentItem.query, ContentItem.issue_id, request_project_id()
        )

    by_status = {row[0]: row[1] for row in scoped().with_entities(ContentItem.status, db.func.count()).group_by(ContentItem.status)}
    by_type = {
        row[0]: row[1]
        for row in scoped().with_entities(ContentItem.content_type, db.func.count()).group_by(ContentItem.content_type)
    }
    return {
        "total": sum(by_status.values()),
        "by_status": {
            "draft": by_status.get("draft", 0),
            "in_review": by_status.get("in_review", 0),
            "approved": by_status.get("approved", 0),
            "rejected": by_status.get("rejected", 0),
            "published": by_status.get("published", 0),
        },
        "by_type": {
            "text_release": by_type.get("text_release", 0),
            "infographic": by_type.get("infographic", 0),
            "video": by_type.get("video", 0),
        },
    }


@bp.get("/issues-ready")
@jwt_required()
@role_required("super_admin", "editor")
def issues_ready_for_content():
    """Isu yang siap / sedang produksi konten."""
    issues_q = Issue.query.filter(Issue.status.in_(["validating", "producing", "approved", "open"]))
    issues_q = filter_issues_query(issues_q, request_project_id())
    issues = issues_q.order_by(Issue.updated_at.desc()).all()
    return jsonify(
        {
            "data": [
                {
                    "id": i.id,
                    "title": i.title,
                    "status": i.status,
                    "risk_level": i.risk_level,
                    "narrative_card": i.narrative_card,
                    "summary": i.summary,
                }
                for i in issues
            ]
        }
    )


@bp.get("/<int:content_id>")
@jwt_required()
@role_required("super_admin", "editor", "pimpinan")
def get_content(content_id: int):
    item = ContentItem.query.get_or_404(content_id)
    return jsonify({"data": _content_payload(item, include_approvals=True, include_issue=True)})


@bp.post("")
@jwt_required()
@role_required("super_admin", "editor")
def create_content():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    content_type = data.get("content_type")
    issue_id = data.get("issue_id")

    if not title:
        return jsonify({"error": "Judul konten wajib diisi"}), 400
    if content_type not in CONTENT_TYPES:
        return jsonify({"error": f"Tipe konten: {', '.join(sorted(CONTENT_TYPES))}"}), 400
    if not issue_id:
        return jsonify({"error": "issue_id wajib"}), 400

    issue = Issue.query.get(issue_id)
    if not issue:
        return jsonify({"error": "Isu tidak ditemukan"}), 404

    user = get_current_user()
    item = ContentItem(
        issue_id=issue.id,
        title=title,
        content_type=content_type,
        body=data.get("body"),
        media_url=data.get("media_url"),
        status="draft",
        created_by=user.id if user else None,
    )
    db.session.add(item)

    if issue.status in {"open", "validating", "producing"}:
        issue.status = "producing"

    now = datetime.now(timezone.utc)
    CrisisAlert.query.filter_by(
        issue_id=issue.id,
        alert_type="content_ready",
        is_read=False,
    ).update({"is_read": True, "read_at": now}, synchronize_session=False)

    db.session.flush()
    db.session.add(
        AuditLog(
            user_id=user.id if user else None,
            action="create_content",
            entity_type="content_item",
            entity_id=item.id,
            details={"issue_id": issue.id, "content_type": content_type},
            ip_address=request.remote_addr,
        )
    )
    db.session.commit()
    return jsonify({"data": _content_payload(item, include_issue=True)}), 201


@bp.patch("/<int:content_id>")
@jwt_required()
@role_required("super_admin", "editor")
def update_content(content_id: int):
    item = ContentItem.query.get_or_404(content_id)
    if item.status not in EDITABLE_STATUSES:
        return jsonify({"error": "Konten hanya bisa diedit saat draft/rejected"}), 400

    data = request.get_json(silent=True) or {}
    if "title" in data:
        title = (data.get("title") or "").strip()
        if not title:
            return jsonify({"error": "Judul tidak boleh kosong"}), 400
        item.title = title
    if "body" in data:
        item.body = data.get("body")
    if "media_url" in data:
        item.media_url = data.get("media_url")
    if "content_type" in data:
        if data["content_type"] not in CONTENT_TYPES:
            return jsonify({"error": "Tipe konten tidak valid"}), 400
        item.content_type = data["content_type"]

    # Editing a rejected item returns it to draft
    if item.status == "rejected":
        item.status = "draft"

    user = get_current_user()
    db.session.add(
        AuditLog(
            user_id=user.id if user else None,
            action="update_content",
            entity_type="content_item",
            entity_id=item.id,
            ip_address=request.remote_addr,
        )
    )
    db.session.commit()
    return jsonify({"data": _content_payload(item, include_approvals=True, include_issue=True)})


@bp.post("/<int:content_id>/submit")
@jwt_required()
@role_required("super_admin", "editor")
def submit_for_review(content_id: int):
    item = ContentItem.query.get_or_404(content_id)
    if item.status not in EDITABLE_STATUSES:
        return jsonify({"error": "Hanya draft/rejected yang bisa diajukan review"}), 400
    if not (item.body or item.media_url):
        return jsonify({"error": "Isi konten atau media_url wajib sebelum review"}), 400

    item.status = "in_review"
    user = get_current_user()
    from app.services.alerts import notify_review_pending
    from app.services.role_notify import notify_pimpinan_review

    if item.issue:
        notify_review_pending(item.issue, item)
    try:
        notify_pimpinan_review(item, user)
    except Exception:
        from flask import current_app

        current_app.logger.exception("Gagal mengirim notifikasi review ke pimpinan")
    db.session.add(
        AuditLog(
            user_id=user.id if user else None,
            action="submit_content_review",
            entity_type="content_item",
            entity_id=item.id,
            ip_address=request.remote_addr,
        )
    )
    db.session.commit()
    return jsonify({"data": _content_payload(item, include_issue=True)})


@bp.post("/<int:content_id>/approve")
@jwt_required()
@role_required("super_admin", "pimpinan")
def approve_content(content_id: int):
    """Review & approve / reject konten (pimpinan / super admin)."""
    item = ContentItem.query.get_or_404(content_id)
    if item.status != "in_review":
        return jsonify({"error": "Konten harus berstatus in_review"}), 400

    data = request.get_json(silent=True) or {}
    decision = data.get("decision")
    if decision not in {"approved", "rejected"}:
        return jsonify({"error": "decision harus approved atau rejected"}), 400

    user = get_current_user()
    item.status = decision
    db.session.add(
        ContentApproval(
            content_id=item.id,
            reviewer_id=user.id if user else None,
            decision=decision,
            notes=data.get("notes"),
        )
    )

    if decision == "approved" and item.issue and item.issue.status == "producing":
        item.issue.status = "approved"

    db.session.add(
        AuditLog(
            user_id=user.id if user else None,
            action="approve_content",
            entity_type="content_item",
            entity_id=item.id,
            details={"decision": decision},
            ip_address=request.remote_addr,
        )
    )
    db.session.commit()
    return jsonify({"data": _content_payload(item, include_approvals=True, include_issue=True)})
