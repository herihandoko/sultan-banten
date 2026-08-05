"""F.09 Agenda Setting Planner API."""

from datetime import date, datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models import AuditLog, EditorialAgenda
from app.utils.auth import get_current_user, role_required
from app.utils.pagination import paginate

bp = Blueprint("agenda", __name__)

STATUSES = {"planned", "in_production", "ready", "published", "cancelled"}
THEMES = {"pembangunan", "penghargaan", "sosial", "ekonomi", "lainnya"}
CHANNELS = {"media", "sosial", "both"}


def _parse_date(value):
    if not value:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


@bp.get("")
@jwt_required()
@role_required("super_admin", "editor", "media_kol_admin", "pimpinan")
def list_agenda():
    status = request.args.get("status")
    theme = request.args.get("theme")
    channel = request.args.get("channel")
    q = (request.args.get("q") or "").strip()
    date_from = _parse_date(request.args.get("date_from"))
    date_to = _parse_date(request.args.get("date_to"))
    month = request.args.get("month")  # YYYY-MM

    query = EditorialAgenda.query
    if status:
        query = query.filter_by(status=status)
    if theme:
        query = query.filter_by(theme=theme)
    if channel:
        query = query.filter_by(channel=channel)
    if q:
        like = f"%{q}%"
        query = query.filter(
            db.or_(
                EditorialAgenda.title.ilike(like),
                EditorialAgenda.description.ilike(like),
                EditorialAgenda.target_media.ilike(like),
            )
        )
    if month:
        try:
            year, mon = map(int, month.split("-"))
            start = date(year, mon, 1)
            if mon == 12:
                end = date(year + 1, 1, 1)
            else:
                end = date(year, mon + 1, 1)
            query = query.filter(
                EditorialAgenda.planned_date >= start,
                EditorialAgenda.planned_date < end,
            )
        except ValueError:
            return jsonify({"error": "Format month harus YYYY-MM"}), 400
    if date_from:
        query = query.filter(EditorialAgenda.planned_date >= date_from)
    if date_to:
        query = query.filter(EditorialAgenda.planned_date <= date_to)

    query = query.order_by(EditorialAgenda.planned_date.asc(), EditorialAgenda.id.asc())
    return jsonify(paginate(query, lambda i: i.to_dict()))


@bp.post("")
@jwt_required()
@role_required("super_admin", "editor", "media_kol_admin")
def create_agenda():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    planned_date = _parse_date(data.get("planned_date"))
    if not title:
        return jsonify({"error": "Judul wajib diisi"}), 400
    if not planned_date:
        return jsonify({"error": "planned_date wajib (YYYY-MM-DD)"}), 400

    theme = data.get("theme") or "lainnya"
    if theme not in THEMES:
        return jsonify({"error": f"theme: {', '.join(sorted(THEMES))}"}), 400
    channel = data.get("channel") or "media"
    if channel not in CHANNELS:
        return jsonify({"error": "channel tidak valid"}), 400
    status = data.get("status") or "planned"
    if status not in STATUSES:
        return jsonify({"error": "status tidak valid"}), 400

    user = get_current_user()
    item = EditorialAgenda(
        title=title,
        description=data.get("description"),
        theme=theme,
        planned_date=planned_date,
        channel=channel,
        status=status,
        target_media=data.get("target_media"),
        content_id=data.get("content_id"),
        notes=data.get("notes"),
        created_by=user.id if user else None,
    )
    db.session.add(item)
    db.session.flush()
    db.session.add(
        AuditLog(
            user_id=user.id if user else None,
            action="create_agenda",
            entity_type="editorial_agenda",
            entity_id=item.id,
            ip_address=request.remote_addr,
        )
    )
    db.session.commit()
    return jsonify({"data": item.to_dict()}), 201


@bp.patch("/<int:agenda_id>")
@jwt_required()
@role_required("super_admin", "editor", "media_kol_admin")
def update_agenda(agenda_id: int):
    item = EditorialAgenda.query.get_or_404(agenda_id)
    data = request.get_json(silent=True) or {}

    if "title" in data:
        title = (data.get("title") or "").strip()
        if not title:
            return jsonify({"error": "Judul tidak boleh kosong"}), 400
        item.title = title
    if "description" in data:
        item.description = data.get("description")
    if "theme" in data:
        if data["theme"] not in THEMES:
            return jsonify({"error": "theme tidak valid"}), 400
        item.theme = data["theme"]
    if "planned_date" in data:
        planned = _parse_date(data["planned_date"])
        if not planned:
            return jsonify({"error": "planned_date tidak valid"}), 400
        item.planned_date = planned
    if "channel" in data:
        if data["channel"] not in CHANNELS:
            return jsonify({"error": "channel tidak valid"}), 400
        item.channel = data["channel"]
    if "status" in data:
        if data["status"] not in STATUSES:
            return jsonify({"error": "status tidak valid"}), 400
        item.status = data["status"]
    if "target_media" in data:
        item.target_media = data.get("target_media")
    if "content_id" in data:
        item.content_id = data.get("content_id")
    if "notes" in data:
        item.notes = data.get("notes")

    db.session.commit()
    return jsonify({"data": item.to_dict()})


@bp.delete("/<int:agenda_id>")
@jwt_required()
@role_required("super_admin", "editor", "media_kol_admin")
def cancel_agenda(agenda_id: int):
    item = EditorialAgenda.query.get_or_404(agenda_id)
    item.status = "cancelled"
    db.session.commit()
    return jsonify({"data": item.to_dict()})
