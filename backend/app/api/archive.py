"""F.05 Arsip Isu & Konten — searchable history."""

from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import or_

from app.models import ContentItem, Issue, MediaBlastLog, OpdValidation
from app.utils.auth import role_required
from app.utils.pagination import paginate, pagination_args
from app.utils.project_scope import filter_issues_query, filter_query_by_issue_ids, request_project_id

bp = Blueprint("archive", __name__)


def _page_arg(*keys, default=1):
    for key in keys:
        raw = request.args.get(key)
        if raw is not None:
            try:
                return max(1, int(raw))
            except (TypeError, ValueError):
                return default
    return default


def _parse_date(value, end_of_day: bool = False):
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if end_of_day and "T" not in str(value):
            dt = dt.replace(hour=23, minute=59, second=59)
        return dt
    except ValueError:
        try:
            dt = datetime.strptime(value, "%Y-%m-%d")
            if end_of_day:
                dt = dt.replace(hour=23, minute=59, second=59)
            return dt
        except ValueError:
            return None


def _issue_archive_card(issue: Issue) -> dict:
    validations = issue.validations or []
    contents = issue.content_items or []
    blasts = MediaBlastLog.query.filter_by(issue_id=issue.id).count()
    return {
        **issue.to_dict(),
        "archive": {
            "evidence_count": len(issue.evidence or []),
            "validation_count": len(validations),
            "validated_count": sum(1 for v in validations if v.status == "validated"),
            "content_count": len(contents),
            "content_approved": sum(
                1 for c in contents if c.status in {"approved", "published"}
            ),
            "blast_count": blasts,
            "timeline": _build_timeline(issue),
        },
    }


def _build_timeline(issue: Issue) -> list[dict]:
    events = [
        {
            "at": issue.created_at.isoformat() if issue.created_at else None,
            "event": "issue_created",
            "label": f"Isu dibuat ({issue.source})",
        }
    ]
    for v in sorted(issue.validations or [], key=lambda x: x.requested_at or datetime.min):
        events.append(
            {
                "at": v.requested_at.isoformat() if v.requested_at else None,
                "event": "validation_requested",
                "label": f"Validasi ke {v.opd_name}",
            }
        )
        if v.responded_at:
            events.append(
                {
                    "at": v.responded_at.isoformat(),
                    "event": "validation_responded",
                    "label": f"OPD {v.status}: {v.opd_name}",
                }
            )
    for c in sorted(issue.content_items or [], key=lambda x: x.created_at or datetime.min):
        events.append(
            {
                "at": c.created_at.isoformat() if c.created_at else None,
                "event": "content_created",
                "label": f"Konten: {c.title} ({c.status})",
            }
        )
    for b in (
        MediaBlastLog.query.filter_by(issue_id=issue.id)
        .order_by(MediaBlastLog.sent_at.asc())
        .all()
    ):
        events.append(
            {
                "at": b.sent_at.isoformat() if b.sent_at else None,
                "event": "media_blast",
                "label": f"Media blast #{b.id} ({b.status})",
            }
        )
    if issue.closed_at:
        events.append(
            {
                "at": issue.closed_at.isoformat(),
                "event": "issue_closed",
                "label": "Isu ditutup",
            }
        )
    events = [e for e in events if e.get("at")]
    events.sort(key=lambda x: x["at"])
    return events


@bp.get("")
@jwt_required()
@role_required("super_admin", "editor", "pimpinan", "media_kol_admin")
def search_archive():
    """
    Cari arsip isu (dan ringkasan konten terkait).
    Query: q, status, risk_level, source, date_from, date_to, type=issues|content|all
    """
    q = (request.args.get("q") or "").strip()
    status = request.args.get("status")
    risk_level = request.args.get("risk_level")
    source = request.args.get("source")
    archive_type = request.args.get("type", "all")
    date_from = _parse_date(request.args.get("date_from"))
    date_to = _parse_date(request.args.get("date_to"), end_of_day=True)

    issues_data = []
    content_data = []
    issues_meta = None
    content_meta = None

    if archive_type in {"all", "issues"}:
        query = Issue.query
        query = filter_issues_query(query, request_project_id())
        if q:
            like = f"%{q}%"
            query = query.filter(
                or_(
                    Issue.title.ilike(like),
                    Issue.summary.ilike(like),
                    Issue.why_now.ilike(like),
                    Issue.mb_alert_id.ilike(like),
                )
            )
        if status:
            query = query.filter_by(status=status)
        if risk_level:
            query = query.filter_by(risk_level=risk_level)
        if source:
            query = query.filter_by(source=source)
        if date_from:
            query = query.filter(Issue.created_at >= date_from)
        if date_to:
            query = query.filter(Issue.created_at <= date_to)
        issues_page = _page_arg("issues_page", "page")
        _, per_page = pagination_args(default_per_page=10)
        result = paginate(
            query.order_by(Issue.created_at.desc()),
            _issue_archive_card,
            page=issues_page,
            per_page=per_page,
        )
        issues_data = result["data"]
        issues_meta = result["meta"]

    if archive_type in {"all", "content"}:
        cquery = ContentItem.query
        cquery = filter_query_by_issue_ids(cquery, ContentItem.issue_id, request_project_id())
        if q:
            like = f"%{q}%"
            cquery = cquery.filter(
                or_(ContentItem.title.ilike(like), ContentItem.body.ilike(like))
            )
        if status and archive_type == "content":
            cquery = cquery.filter_by(status=status)
        if date_from:
            cquery = cquery.filter(ContentItem.created_at >= date_from)
        if date_to:
            cquery = cquery.filter(ContentItem.created_at <= date_to)

        def _content_card(c):
            return {
                **c.to_dict(),
                "issue_title": c.issue.title if c.issue else None,
                "issue_risk_level": c.issue.risk_level if c.issue else None,
            }

        contents_page = _page_arg("contents_page", "page")
        _, per_page = pagination_args(default_per_page=10)
        result = paginate(
            cquery.order_by(ContentItem.created_at.desc()),
            _content_card,
            page=contents_page,
            per_page=per_page,
        )
        content_data = result["data"]
        content_meta = result["meta"]

    return jsonify(
        {
            "data": {
                "issues": issues_data,
                "contents": content_data,
            },
            "meta": {
                "q": q,
                "issues": issues_meta,
                "contents": content_meta,
                "issues_count": (issues_meta or {}).get("total", len(issues_data)),
                "contents_count": (content_meta or {}).get("total", len(content_data)),
            },
        }
    )


@bp.get("/issues/<int:issue_id>")
@jwt_required()
@role_required("super_admin", "editor", "pimpinan", "media_kol_admin", "opd_admin")
def archive_issue_detail(issue_id: int):
    issue = Issue.query.get_or_404(issue_id)
    card = _issue_archive_card(issue)
    card["evidence"] = [e.to_dict() for e in issue.evidence]
    card["validations"] = [v.to_dict() for v in issue.validations]
    card["content_items"] = [c.to_dict() for c in issue.content_items]
    return jsonify({"data": card})
