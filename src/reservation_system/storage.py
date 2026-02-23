"""Persistence layer using JSON files.

Goal: if JSON is invalid or has wrong type, print an error and continue.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List

from .exceptions import StorageError


def _read_json_safe(path: str) -> Any:
    """Read JSON. If missing/empty/invalid, return []."""
    if not os.path.exists(path):
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read().strip()
            if not raw:
                return []
            return json.loads(raw)
    except json.JSONDecodeError as exc:
        msg = "[ERROR] Invalid JSON in {}: {}".format(path, exc)
        print(msg)
        return []
    except OSError as exc:
        msg = "Failed reading {}: {}".format(path, exc)
        raise StorageError(msg) from exc


def _write_json_safe(path: str, data: Any) -> None:
    """Write JSON to disk."""
    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except OSError as exc:
        msg = "Failed writing {}: {}".format(path, exc)
        raise StorageError(msg) from exc


@dataclass(frozen=True, slots=True)
class StorePaths:
    """Paths for JSON storage files."""
    hotels: str
    customers: str
    reservations: str


class JsonStore:
    """Simple JSON store: each file is a list of dict records."""

    def __init__(self, paths: StorePaths) -> None:
        self._p = paths

    def load_hotels(self) -> List[Dict[str, Any]]:
        data = _read_json_safe(self._p.hotels)
        if isinstance(data, list):
            return [x for x in data if isinstance(x, dict)]
        msg = "[ERROR] Hotels file must be a JSON array. Got: {}".format(
            type(data).__name__
        )
        print(msg)
        return []

    def save_hotels(self, items: List[Dict[str, Any]]) -> None:
        _write_json_safe(self._p.hotels, items)

    def load_customers(self) -> List[Dict[str, Any]]:
        data = _read_json_safe(self._p.customers)
        if isinstance(data, list):
            return [x for x in data if isinstance(x, dict)]
        msg = "[ERROR] Customers file must be a JSON array. Got: {}".format(
            type(data).__name__
        )
        print(msg)
        return []

    def save_customers(self, items: List[Dict[str, Any]]) -> None:
        _write_json_safe(self._p.customers, items)

    def load_reservations(self) -> List[Dict[str, Any]]:
        data = _read_json_safe(self._p.reservations)
        if isinstance(data, list):
            return [x for x in data if isinstance(x, dict)]
        msg = "[ERROR] Reservations file must be a JSON array. Got: {}".format(
            type(data).__name__
        )
        print(msg)
        return []

    def save_reservations(self, items: List[Dict[str, Any]]) -> None:
        _write_json_safe(self._p.reservations, items)
