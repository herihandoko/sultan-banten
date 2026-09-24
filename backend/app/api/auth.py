"""Authentication endpoints."""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

from app.extensions import db
from app.models import AuditLog, User
from app.utils.auth import get_current_user

bp = Blueprint("auth", __name__)


@bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return jsonify({"error": "Username dan password wajib diisi"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password) or not user.is_active:
        return jsonify({"error": "Kredensial tidak valid"}), 401

    token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role.code if user.role else None},
    )

    db.session.add(
        AuditLog(
            user_id=user.id,
            action="login",
            entity_type="user",
            entity_id=user.id,
            ip_address=request.remote_addr,
        )
    )
    db.session.commit()

    return jsonify({"access_token": token, "user": user.to_dict(include_avatar=True)})


@bp.get("/me")
@jwt_required()
def me():
    user = get_current_user()
    if not user:
        return jsonify({"error": "User tidak ditemukan"}), 404
    return jsonify({"user": user.to_dict(include_avatar=True)})


def _valid_avatar(value) -> str | None:
    """Accept a small JPEG/PNG data URL, or None to clear."""
    if value in (None, ""):
        return None
    if not isinstance(value, str):
        raise ValueError("Foto profil tidak valid")
    if not value.startswith(("data:image/jpeg;base64,", "data:image/png;base64,")):
        raise ValueError("Foto profil harus JPEG atau PNG")
    if len(value) > 180_000:
        raise ValueError("Foto profil terlalu besar")
    return value


@bp.patch("/profile")
@jwt_required()
def update_profile():
    user = get_current_user()
    if not user:
        return jsonify({"error": "User tidak ditemukan"}), 404

    data = request.get_json(silent=True) or {}
    changed = []

    if "avatar" in data:
        try:
            user.avatar = _valid_avatar(data.get("avatar"))
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        changed.append("avatar")

    new_password = (data.get("new_password") or "").strip()
    if new_password or data.get("current_password"):
        current = data.get("current_password") or ""
        if not user.check_password(current):
            return jsonify({"error": "Password saat ini salah"}), 400
        if len(new_password) < 8:
            return jsonify({"error": "Password baru minimal 8 karakter"}), 400
        user.set_password(new_password)
        changed.append("password")

    if not changed:
        return jsonify({"error": "Tidak ada perubahan"}), 400

    db.session.add(
        AuditLog(
            user_id=user.id,
            action="update_profile",
            entity_type="user",
            entity_id=user.id,
            details={"fields": changed},
            ip_address=request.remote_addr,
        )
    )
    db.session.commit()
    return jsonify({"user": user.to_dict(include_avatar=True)})


@bp.post("/logout")
@jwt_required()
def logout():
    user_id = get_jwt_identity()
    db.session.add(
        AuditLog(
            user_id=int(user_id),
            action="logout",
            entity_type="user",
            entity_id=int(user_id),
            ip_address=request.remote_addr,
        )
    )
    db.session.commit()
    return jsonify({"message": "Logged out"})
