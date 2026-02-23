"""Validation helpers for domain models."""

from __future__ import annotations

from datetime import date

from .exceptions import ValidationError


def req_str(val: str, field: str) -> str:
    """Require a non-empty string."""
    if not isinstance(val, str) or not val.strip():
        raise ValidationError(f"{field} must be a non-empty string.")
    return val.strip()


def req_pos_int(val: int, field: str) -> int:
    """Require a positive integer."""
    if not isinstance(val, int) or val <= 0:
        raise ValidationError(f"{field} must be a positive integer.")
    return val


def req_iso_date(val: str, field: str) -> str:
    """Require an ISO date string (YYYY-MM-DD)."""
    if not isinstance(val, str):
        raise ValidationError(f"{field} must be an ISO date string.")
    try:
        date.fromisoformat(val)
    except ValueError as exc:
        raise ValidationError(f"{field} must be ISO format YYYY-MM-DD.") from exc
    return val
