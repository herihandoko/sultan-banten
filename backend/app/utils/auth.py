"""Auth helpers and RBAC decorators."""

from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request

from app.models import User


ROLE_CODES = {
    "super_admin": "Super Admin",
    "editor": "Tim Editor/Kreatif",
    "opd_admin": "Admin OPD Teknis",
    "pimpinan": "Pimpinan",
    "media_kol_admin": "Admin Media & KOL",
    "asn": "User ASN Banten",
}


def role_required(*allowed_roles):
    """Require JWT and one of the allowed role codes. Super admin always allowed."""

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            role = claims.get("role")
            if role == "super_admin" or role in allowed_roles:
                return fn(*args, **kwargs)
            return jsonify({"error": "Forbidden"}), 403

        return wrapper

    return decorator


def get_current_user() -> User | None:
    from flask_jwt_extended import get_jwt_identity

    user_id = get_jwt_identity()
    if user_id is None:
        return None
    return db_get_user(int(user_id))


def db_get_user(user_id: int) -> User | None:
    return User.query.get(user_id)
