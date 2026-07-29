#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."
python - <<'PY'
import os, sys, time
from urllib.parse import urlparse, unquote

url = os.environ.get("DATABASE_URL", "")
if not url.startswith("postgresql"):
    print("DATABASE_URL is not PostgreSQL — skip wait")
    sys.exit(0)

# postgresql+psycopg2://user:pass@host:port/db
raw = url.replace("postgresql+psycopg2://", "postgresql://", 1)
parsed = urlparse(raw)
host = parsed.hostname or "localhost"
port = parsed.port or 5432
user = unquote(parsed.username or "postgres")
password = unquote(parsed.password or "")
dbname = (parsed.path or "/postgres").lstrip("/") or "postgres"

import psycopg2
for i in range(60):
    try:
        conn = psycopg2.connect(
            host=host, port=port, user=user, password=password, dbname=dbname,
            connect_timeout=3,
        )
        conn.close()
        print(f"PostgreSQL ready at {host}:{port}/{dbname}")
        sys.exit(0)
    except Exception as e:
        print(f"  attempt {i+1}/60: {e}")
        time.sleep(2)
print("PostgreSQL not reachable", file=sys.stderr)
sys.exit(1)
PY

if [ "${RUN_SEED:-true}" = "true" ]; then
  echo "Initializing schema + seed (idempotent)..."
  python - <<'PY'
from app import create_app
from app import models  # noqa: F401
from app.extensions import db
from seed import seed_all

app = create_app()
with app.app_context():
    db.create_all()
    seed_all()
    print("Schema + seed OK")
PY
fi

exec "$@"
