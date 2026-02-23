"""Reservation entity."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, Optional

from .exceptions import ValidationError
from .validators import req_iso_date, req_str


@dataclass(frozen=True, slots=True)
class Reservation:
    resv_id: str
    hotel_id: str
    customer_id: str
    check_in: str
    check_out: str
    room_no: Optional[int] = None

    def __post_init__(self) -> None:
        req_str(self.resv_id, "resv_id")
        req_str(self.hotel_id, "hotel_id")
        req_str(self.customer_id, "customer_id")

        cin = req_iso_date(self.check_in, "check_in")
        cout = req_iso_date(self.check_out, "check_out")

        d_in = date.fromisoformat(cin)
        d_out = date.fromisoformat(cout)
        if d_out <= d_in:
            raise ValidationError("check_out must be after check_in.")

        if self.room_no is not None and (
            (not isinstance(self.room_no, int))
            or (self.room_no <= 0)
        ):
            raise ValidationError(
                "room_no must be a positive integer if provided.")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "resv_id": self.resv_id,
            "hotel_id": self.hotel_id,
            "customer_id": self.customer_id,
            "check_in": self.check_in,
            "check_out": self.check_out,
            "room_no": self.room_no,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Reservation":
        return Reservation(
            resv_id=d["resv_id"],
            hotel_id=d["hotel_id"],
            customer_id=d["customer_id"],
            check_in=d["check_in"],
            check_out=d["check_out"],
            room_no=d.get("room_no"),
        )
