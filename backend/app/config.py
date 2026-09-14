"""Application configuration."""

import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_DIR = BASE_DIR / "instance"
INSTANCE_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv(BASE_DIR / ".env")


def _database_url() -> str:
    configured = os.getenv("DATABASE_URL", "").strip()
    if not configured:
        return f"sqlite:///{INSTANCE_DIR / 'sultan_banten.db'}"
    # Normalize relative sqlite paths to absolute under backend/
    if configured.startswith("sqlite:///"):
        raw = configured.removeprefix("sqlite:///")
        path = Path(raw)
        if not path.is_absolute():
            path = BASE_DIR / path
        path.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{path}"
    # Allow plain postgresql:// — SQLAlchemy accepts it with psycopg2 installed
    if configured.startswith("postgres://"):
        configured = configured.replace("postgres://", "postgresql+psycopg2://", 1)
    elif configured.startswith("postgresql://") and "+psycopg2" not in configured:
        configured = configured.replace("postgresql://", "postgresql+psycopg2://", 1)
    return configured


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret-change-me")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)

    SQLALCHEMY_DATABASE_URI = _database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    CORS_ORIGINS = [
        o.strip()
        for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
        if o.strip()
    ]

    # Mata Bathin / SIPANTAU integration
    MATA_BATHIN_BASE_URL = os.getenv("MATA_BATHIN_BASE_URL", "")
    MATA_BATHIN_API_KEY = os.getenv("MATA_BATHIN_API_KEY", "")
    MATA_BATHIN_ENABLED = os.getenv("MATA_BATHIN_ENABLED", "false").lower() == "true"
    MATA_BATHIN_TIMEOUT = int(os.getenv("MATA_BATHIN_TIMEOUT", "10"))
    MATA_BATHIN_MAX_RETRIES = int(os.getenv("MATA_BATHIN_MAX_RETRIES", "3"))

    # SIPANTAU listening engine (source of mention KPIs)
    SIPANTAU_INTERNAL_URL = os.getenv("SIPANTAU_INTERNAL_URL", "http://panten:3000")
    SIPANTAU_INTERNAL_KEY = os.getenv("SIPANTAU_INTERNAL_KEY", "")
    SIPANTAU_TIMEOUT = int(os.getenv("SIPANTAU_TIMEOUT", "8"))
