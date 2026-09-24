"""Application settings helpers."""

from __future__ import annotations

from app.extensions import db
from app.models.setting import AppSetting

NEWS_SOURCE_KEY = "news_source"
NEWS_SOURCES = ("sipantau", "mata_bathin")
DEFAULT_NEWS_SOURCE = "mata_bathin"


def get_setting(key: str, default: str = "") -> str:
    row = AppSetting.query.filter_by(key=key).first()
    if not row or row.value is None:
        return default
    return str(row.value)


def get_setting_raw(key: str) -> str | None:
    """None when the key has never been saved."""
    row = AppSetting.query.filter_by(key=key).first()
    if not row:
        return None
    return "" if row.value is None else str(row.value)


def set_setting(key: str, value: str) -> AppSetting:
    row = AppSetting.query.filter_by(key=key).first()
    if row:
        row.value = value
    else:
        row = AppSetting(key=key, value=value)
        db.session.add(row)
    db.session.commit()
    return row


def get_news_source() -> str:
    raw = (get_setting(NEWS_SOURCE_KEY, DEFAULT_NEWS_SOURCE) or DEFAULT_NEWS_SOURCE).strip().lower()
    if raw not in NEWS_SOURCES:
        return DEFAULT_NEWS_SOURCE
    return raw


def set_news_source(source: str) -> str:
    value = (source or "").strip().lower()
    if value not in NEWS_SOURCES:
        raise ValueError(f"news_source harus salah satu dari: {', '.join(NEWS_SOURCES)}")
    set_setting(NEWS_SOURCE_KEY, value)
    return value


def news_source_public() -> dict:
    source = get_news_source()
    return {
        "news_source": source,
        "allowed": list(NEWS_SOURCES),
        "show_sipantau_ui": source == "sipantau",
        "label": "SIPANTAU" if source == "sipantau" else "Mata Bathin",
    }


def _env_fallback(key: str, default: str = "") -> str:
    import os

    try:
        from flask import current_app, has_app_context

        if has_app_context():
            val = current_app.config.get(key)
            if isinstance(val, bool):
                return "true" if val else "false"
            if val is not None and str(val) != "":
                return str(val)
    except Exception:
        pass
    return os.getenv(key, default)


def messaging_value(key: str, default: str = "") -> str:
    """DB setting wins when saved; otherwise fall back to env / Flask config."""
    stored = get_setting_raw(f"msg.{key}")
    if stored is not None:
        return stored
    return _env_fallback(key, default)


def _flag(value: str) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def messaging_public() -> dict:
    token = messaging_value("FONNTE_TOKEN", "")
    password = messaging_value("MAIL_PASSWORD", "")
    mail_enabled = _flag(messaging_value("MAIL_ENABLED", "false"))
    return {
        "whatsapp": {
            "token_set": bool(token.strip()),
            "country_code": messaging_value("FONNTE_COUNTRY_CODE", "62") or "62",
            "crisis_number": messaging_value("CRISIS_WA_NUMBER", ""),
        },
        "email": {
            "enabled": mail_enabled,
            "host": messaging_value("MAIL_HOST", ""),
            "port": int(messaging_value("MAIL_PORT", "587") or 587),
            "username": messaging_value("MAIL_USERNAME", ""),
            "password_set": bool(password),
            "encryption": (messaging_value("MAIL_ENCRYPTION", "tls") or "tls").lower(),
            "from_address": messaging_value("MAIL_FROM_ADDRESS", ""),
            "from_name": messaging_value("MAIL_FROM_NAME", "SIAGAPIM Banten") or "SIAGAPIM Banten",
        },
    }


def save_messaging(payload: dict) -> dict:
    whatsapp = payload.get("whatsapp") if isinstance(payload.get("whatsapp"), dict) else {}
    email = payload.get("email") if isinstance(payload.get("email"), dict) else {}

    if "country_code" in whatsapp:
        code = "".join(c for c in str(whatsapp.get("country_code") or "") if c.isdigit()) or "62"
        set_setting("msg.FONNTE_COUNTRY_CODE", code[:4])
    if "crisis_number" in whatsapp:
        number = "".join(c for c in str(whatsapp.get("crisis_number") or "") if c.isdigit())
        set_setting("msg.CRISIS_WA_NUMBER", number[:20])
    token = whatsapp.get("token")
    if isinstance(token, str) and token.strip():
        set_setting("msg.FONNTE_TOKEN", token.strip())

    if "enabled" in email:
        set_setting("msg.MAIL_ENABLED", "true" if _flag(str(email.get("enabled"))) or email.get("enabled") is True else "false")
    if "host" in email:
        set_setting("msg.MAIL_HOST", str(email.get("host") or "").strip()[:200])
    if "port" in email:
        try:
            port = int(email.get("port") or 587)
        except (TypeError, ValueError):
            raise ValueError("Port SMTP harus angka")
        if port < 1 or port > 65535:
            raise ValueError("Port SMTP tidak valid")
        set_setting("msg.MAIL_PORT", str(port))
    if "username" in email:
        set_setting("msg.MAIL_USERNAME", str(email.get("username") or "").strip()[:200])
    if "encryption" in email:
        encryption = str(email.get("encryption") or "tls").strip().lower()
        if encryption not in {"tls", "ssl", "none"}:
            raise ValueError("Enkripsi email harus tls, ssl, atau none")
        set_setting("msg.MAIL_ENCRYPTION", encryption)
    if "from_address" in email:
        set_setting("msg.MAIL_FROM_ADDRESS", str(email.get("from_address") or "").strip()[:200])
    if "from_name" in email:
        set_setting("msg.MAIL_FROM_NAME", str(email.get("from_name") or "").strip()[:120] or "SIAGAPIM Banten")
    password = email.get("password")
    if isinstance(password, str) and password.strip():
        set_setting("msg.MAIL_PASSWORD", password)

    return messaging_public()
