"""Hotel entity."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from .validators import req_pos_int, req_str


@dataclass(frozen=True, slots=True)
class Hotel:
    hotel_id: str
    name: str
    city: str
    rooms_total: int

    def __post_init__(self) -> None:
        req_str(self.hotel_id, "hotel_id")
        req_str(self.name, "name")
        req_str(self.city, "city")
        req_pos_int(self.rooms_total, "rooms_total")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hotel_id": self.hotel_id,
            "name": self.name,
            "city": self.city,
            "rooms_total": self.rooms_total,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Hotel":
        return Hotel(
            hotel_id=d["hotel_id"],
            name=d["name"],
            city=d["city"],
            rooms_total=d["rooms_total"],
        )
