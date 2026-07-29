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

    return jsonify({"access_token": token, "user": user.to_dict()})


@bp.get("/me")
@jwt_required()
def me():
    user = get_current_user()
    if not user:
        return jsonify({"error": "User tidak ditemukan"}), 404
    return jsonify({"user": user.to_dict()})


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
