"""Master OPD — referensi organisasi perangkat daerah."""

from datetime import datetime, timezone

from app.extensions import db


class Opd(db.Model):
    __tablename__ = "opds"

    id = db.Column(db.Integer, primary_key=True)
    # Preserve source id from ct_opd when seeded
    source_id = db.Column(db.Integer, unique=True, index=True)
    name = db.Column(db.String(255), nullable=False, unique=True, index=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    users = db.relationship("User", back_populates="opd")

    def to_dict(self):
        return {
            "id": self.id,
            "source_id": self.source_id,
            "name": self.name,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
