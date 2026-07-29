"""Pagination helpers for list endpoints."""

from flask import request


def pagination_args(default_per_page: int = 10, max_per_page: int = 100):
    try:
        page = int(request.args.get("page", 1))
    except (TypeError, ValueError):
        page = 1
    try:
        per_page = int(request.args.get("per_page", default_per_page))
    except (TypeError, ValueError):
        per_page = default_per_page
    page = max(1, page)
    per_page = min(max_per_page, max(1, per_page))
    return page, per_page


def paginate(
    query,
    serializer,
    default_per_page: int = 10,
    max_per_page: int = 100,
    page: int | None = None,
    per_page: int | None = None,
):
    """
    Paginate a SQLAlchemy query.
    serializer: callable(item) -> dict  OR  None to return model as-is (caller maps).
    Optional page/per_page override request args (e.g. archive dual lists).
    """
    args_page, args_per_page = pagination_args(default_per_page, max_per_page)
    page = max(1, page) if page is not None else args_page
    if per_page is not None:
        per_page = min(max_per_page, max(1, per_page))
    else:
        per_page = args_per_page
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    items = pagination.items
    if serializer:
        data = [serializer(i) for i in items]
    else:
        data = items
    return {
        "data": data,
        "meta": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": max(1, pagination.pages or 1) if pagination.total else 0,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
        },
    }
