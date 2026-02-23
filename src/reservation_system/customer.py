"""Customer entity."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from .exceptions import ValidationError
from .validators import req_str


@dataclass(frozen=True, slots=True)
class Customer:
    customer_id: str
    name_full: str
    email: str

    def __post_init__(self) -> None:
        req_str(self.customer_id, "customer_id")
        req_str(self.name_full, "name_full")
        req_str(self.email, "email")
        if "@" not in self.email or self.email.startswith("@") or self.email.endswith("@"):
            raise ValidationError("email must look like a valid email address.")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "customer_id": self.customer_id,
            "name_full": self.name_full,
            "email": self.email,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Customer":
        return Customer(
            customer_id=d["customer_id"],
            name_full=d["name_full"],
            email=d["email"],
        )
