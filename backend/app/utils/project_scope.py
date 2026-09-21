"""Scope SIAGAPIM operational data to a SIPANTAU project (keyword id)."""

from __future__ import annotations

from flask import request
from sqlalchemy import or_, text

from app.extensions import db
from app.models import Issue


def request_project_id() -> str | None:
    """Read project_id from query string (preferred) or JSON body."""
    pid = (request.args.get("project_id") or request.args.get("keyword_id") or "").strip()
    if pid:
        return pid
    if request.method in {"POST", "PUT", "PATCH"}:
        data = request.get_json(silent=True) or {}
        pid = str(data.get("project_id") or data.get("keyword_id") or "").strip()
        if pid:
            return pid
    return None


def issue_ids_for_project(project_id: str | None) -> list[int] | None:
    """
    Return matching issue IDs for project_id.
    None means no filter (no project selected — should be rare).
    Empty list means no matches.
    """
    if not project_id:
        return None

    ids: set[int] = set()
    # Primary: dedicated column
    for row in Issue.query.filter(Issue.project_id == project_id).with_entities(Issue.id).all():
        ids.add(row[0])

    # Legacy: JSON risk_assessment.sipantau_keyword_id
    try:
        rows = db.session.execute(
            text(
                """
                SELECT id FROM issues
                WHERE project_id IS NULL
                  AND risk_assessment IS NOT NULL
                  AND risk_assessment->>'sipantau_keyword_id' = :pid
                """
            ),
            {"pid": project_id},
        ).fetchall()
        for r in rows:
            ids.add(r[0])
    except Exception:
        # SQLite / non-JSON dialect fallback — scan in Python
        for issue in Issue.query.filter(Issue.project_id.is_(None)).all():
            assessment = issue.risk_assessment if isinstance(issue.risk_assessment, dict) else {}
            if str(assessment.get("sipantau_keyword_id") or "") == project_id:
                ids.add(issue.id)

    return list(ids) if ids else []


def filter_query_by_issue_ids(query, issue_id_column, project_id: str | None):
    """Apply issue_id IN (...) when project is selected. Empty match → no rows."""
    ids = issue_ids_for_project(project_id)
    if ids is None:
        return query
    if not ids:
        return query.filter(issue_id_column.in_([-1]))
    return query.filter(issue_id_column.in_(ids))


def filter_issues_query(query, project_id: str | None):
    """Filter Issue.query by project."""
    ids = issue_ids_for_project(project_id)
    if ids is None:
        return query
    if not ids:
        return query.filter(Issue.id.in_([-1]))
    return query.filter(Issue.id.in_(ids))


def ensure_issue_project_id_column() -> None:
    """Idempotent ALTER for existing Postgres volumes (create_all won't add columns)."""
    try:
        db.session.execute(
            text("ALTER TABLE issues ADD COLUMN IF NOT EXISTS project_id VARCHAR(100)")
        )
        db.session.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_issues_project_id ON issues (project_id)"
            )
        )
        # Google News RSS URLs exceed VARCHAR(500)
        db.session.execute(
            text("ALTER TABLE issue_evidence ALTER COLUMN url TYPE TEXT")
        )
        db.session.commit()
    except Exception:
        db.session.rollback()
