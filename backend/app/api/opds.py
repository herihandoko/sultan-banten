"""Master OPD API."""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models import Opd
from app.utils.auth import role_required
from app.utils.pagination import paginate

bp = Blueprint("opds", __name__)


@bp.get("")
@jwt_required()
@role_required(
    "super_admin",
    "editor",
    "pimpinan",
    "media_kol_admin",
    "opd_admin",
    "asn",
)
def list_opds():
    """Daftar OPD — untuk master & dropdown."""
    active_only = request.args.get("active", "1") != "0"
    q = (request.args.get("q") or "").strip()
    query = Opd.query
    if active_only:
        query = query.filter_by(is_active=True)
    if q:
        query = query.filter(Opd.name.ilike(f"%{q}%"))
    query = query.order_by(Opd.name.asc())
    return jsonify(paginate(query, lambda i: i.to_dict(), default_per_page=15, max_per_page=200))


@bp.post("")
@jwt_required()
@role_required("super_admin")
def create_opd():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "Nama OPD wajib diisi"}), 400
    if Opd.query.filter_by(name=name).first():
        return jsonify({"error": "Nama OPD sudah ada"}), 409
    item = Opd(name=name, is_active=bool(data.get("is_active", True)))
    db.session.add(item)
    db.session.commit()
    return jsonify({"data": item.to_dict()}), 201


@bp.patch("/<int:opd_id>")
@jwt_required()
@role_required("super_admin")
def update_opd(opd_id: int):
    item = Opd.query.get_or_404(opd_id)
    data = request.get_json(silent=True) or {}
    if "name" in data:
        name = (data.get("name") or "").strip()
        if not name:
            return jsonify({"error": "Nama OPD tidak boleh kosong"}), 400
        conflict = Opd.query.filter(Opd.name == name, Opd.id != item.id).first()
        if conflict:
            return jsonify({"error": "Nama OPD sudah dipakai"}), 409
        old_name = item.name
        item.name = name
        # Sync user.opd_name & open validations that used old name
        from app.models import OpdValidation, User

        User.query.filter_by(opd_id=item.id).update({"opd_name": name})
        OpdValidation.query.filter_by(opd_name=old_name).update({"opd_name": name})
    if "is_active" in data:
        item.is_active = bool(data["is_active"])
    db.session.commit()
    return jsonify({"data": item.to_dict()})


@bp.delete("/<int:opd_id>")
@jwt_required()
@role_required("super_admin")
def deactivate_opd(opd_id: int):
    item = Opd.query.get_or_404(opd_id)
    item.is_active = False
    db.session.commit()
    return jsonify({"data": item.to_dict()})
