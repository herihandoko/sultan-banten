"""Pull SIPANTAU crisis candidates into SIAGAPIM Crisis Room."""

from __future__ import annotations

import logging
from typing import Any

import requests
from flask import current_app, request

logger = logging.getLogger(__name__)


def _headers() -> dict[str, str]:
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    key = current_app.config.get("SIPANTAU_INTERNAL_KEY") or ""
    if key:
        headers["X-Internal-Key"] = key
    auth = request.headers.get("Authorization") if request else None
    if auth:
        headers["Authorization"] = auth
    return headers


def sync_sipantau_crises(project_id: str | None = None) -> dict[str, Any]:
    """
    Ask SIPANTAU to evaluate negative spikes and push them via webhook.
    Returns {candidates, pushed} or {error}.
    """
    base = (current_app.config.get("SIPANTAU_INTERNAL_URL") or "").rstrip("/")
    if not base:
        return {"error": "SIPANTAU_INTERNAL_URL kosong", "candidates": 0, "pushed": 0}

    body: dict[str, Any] = {}
    if project_id:
        body["keyword_id"] = project_id

    try:
        res = requests.post(
            f"{base}/api/export/crisis-check",
            headers=_headers(),
            json=body,
            timeout=current_app.config.get("SIPANTAU_TIMEOUT", 8),
        )
        if not res.ok:
            logger.warning("SIPANTAU crisis-check HTTP %s: %s", res.status_code, res.text[:200])
            return {
                "error": f"HTTP {res.status_code}",
                "candidates": 0,
                "pushed": 0,
            }
        data = (res.json() or {}).get("data") or {}
        return {
            "candidates": int(data.get("candidates") or 0),
            "pushed": int(data.get("pushed") or 0),
        }
    except requests.RequestException as exc:
        logger.warning("SIPANTAU crisis-check failed: %s", exc)
        return {"error": str(exc), "candidates": 0, "pushed": 0}
