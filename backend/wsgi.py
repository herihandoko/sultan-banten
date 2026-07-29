"""WSGI / CLI entrypoint."""

from app import create_app
from app import models  # noqa: F401 — register all models
from app.extensions import db

app = create_app()


@app.cli.command("init-db")
def init_db():
    """Create tables and seed roles + demo admin."""
    from seed import seed_all

    with app.app_context():
        db.create_all()
        seed_all()
        print("Database initialized.")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
