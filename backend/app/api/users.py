"""User management endpoints."""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models import Opd, Role, User
from app.utils.auth import role_required
from app.utils.pagination import paginate

bp = Blueprint("users", __name__)


def _resolve_opd(data: dict) -> tuple[int | None, str | None, str | None]:
    """Return (opd_id, opd_name, error)."""
    opd_id = data.get("opd_id")
    opd_name = (data.get("opd_name") or "").strip() or None

    if opd_id:
        opd = Opd.query.get(opd_id)
        if not opd or not opd.is_active:
            return None, None, "OPD tidak ditemukan / nonaktif"
        return opd.id, opd.name, None

    if opd_name:
        opd = Opd.query.filter_by(name=opd_name, is_active=True).first()
        if not opd:
            return None, None, "OPD harus dipilih dari master OPD"
        return opd.id, opd.name, None

    return None, None, None


@bp.get("")
@jwt_required()
@role_required("super_admin")
def list_users():
    q = (request.args.get("q") or "").strip()
    role_code = (request.args.get("role_code") or "").strip()
    active = request.args.get("active")  # 1 | 0 | omit
    query = User.query
    if role_code:
        role = Role.query.filter_by(code=role_code).first()
        if role:
            query = query.filter_by(role_id=role.id)
        else:
            query = query.filter_by(role_id=-1)
    if active == "1":
        query = query.filter_by(is_active=True)
    elif active == "0":
        query = query.filter_by(is_active=False)
    if q:
        like = f"%{q}%"
        query = query.filter(
            db.or_(
                User.username.ilike(like),
                User.full_name.ilike(like),
                User.email.ilike(like),
                User.opd_name.ilike(like),
            )
        )
    query = query.order_by(User.created_at.desc())
    return jsonify(paginate(query, lambda u: u.to_dict()))


@bp.get("/roles")
@jwt_required()
@role_required("super_admin")
def list_roles():
    roles = Role.query.order_by(Role.id).all()
    return jsonify({"data": [r.to_dict() for r in roles]})


@bp.post("")
@jwt_required()
@role_required("super_admin")
def create_user():
    data = request.get_json(silent=True) or {}
    required = ["username", "email", "password", "full_name", "role_code"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Field wajib: {', '.join(missing)}"}), 400

    role = Role.query.filter_by(code=data["role_code"]).first()
    if not role:
        return jsonify({"error": "Role tidak ditemukan"}), 400

    if role.code in {"opd_admin", "asn"} and not data.get("opd_id") and not data.get("opd_name"):
        return jsonify({"error": "OPD wajib dipilih untuk role OPD Admin / ASN"}), 400

    opd_id, opd_name, opd_err = _resolve_opd(data)
    if opd_err:
        return jsonify({"error": opd_err}), 400

    if User.query.filter(
        (User.username == data["username"]) | (User.email == data["email"])
    ).first():
        return jsonify({"error": "Username atau email sudah digunakan"}), 409

    user = User(
        username=data["username"].strip(),
        email=data["email"].strip().lower(),
        full_name=data["full_name"].strip(),
        role_id=role.id,
        opd_id=opd_id,
        opd_name=opd_name,
    )
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()
    return jsonify({"data": user.to_dict()}), 201


@bp.patch("/<int:user_id>")
@jwt_required()
@role_required("super_admin")
def update_user(user_id: int):
    user = User.query.get_or_404(user_id)
    data = request.get_json(silent=True) or {}

    if "full_name" in data:
        name = (data.get("full_name") or "").strip()
        if not name:
            return jsonify({"error": "full_name tidak boleh kosong"}), 400
        user.full_name = name

    if "email" in data:
        email = (data.get("email") or "").strip().lower()
        if not email:
            return jsonify({"error": "email tidak boleh kosong"}), 400
        conflict = User.query.filter(User.email == email, User.id != user.id).first()
        if conflict:
            return jsonify({"error": "Email sudah digunakan"}), 409
        user.email = email

    if "role_code" in data:
        role = Role.query.filter_by(code=data["role_code"]).first()
        if not role:
            return jsonify({"error": "Role tidak ditemukan"}), 400
        user.role_id = role.id

    if "opd_id" in data or "opd_name" in data:
        opd_id, opd_name, opd_err = _resolve_opd(data)
        if opd_err:
            return jsonify({"error": opd_err}), 400
        # Explicit clear
        if data.get("opd_id") in (None, "", 0) and not data.get("opd_name"):
            user.opd_id = None
            user.opd_name = None
        else:
            user.opd_id = opd_id
            user.opd_name = opd_name

    if "is_active" in data:
        user.is_active = bool(data["is_active"])

    if data.get("password"):
        user.set_password(data["password"])

    db.session.commit()
    return jsonify({"data": user.to_dict()})
