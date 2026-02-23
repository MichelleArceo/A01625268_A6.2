"""Minimal CLI for execution evidence.

Usage:
  python -m reservation_system.cli seed
  python -m reservation_system.cli demo
"""

from __future__ import annotations

import sys

from .customer import Customer
from .hotel import Hotel
from .service import ReservationService
from .storage import JsonStore, StorePaths


def _service() -> ReservationService:
    paths = StorePaths(
        hotels="data/hotels.json",
        customers="data/customers.json",
        reservations="data/reservations.json",
    )
    return ReservationService(store=JsonStore(paths))


def seed() -> None:
    svc = _service()
    # Create base data if not exists
    try:
        svc.create_hotel(Hotel("H1", “Michelle Inn", "Nagoya", 2))
    except Exception:
        pass
    try:
        svc.create_customer(Customer("C1", "Michelle", "michelle@example.com"))
    except Exception:
        pass
    print("Seed completed.")


def demo() -> None:
    svc = _service()
    seed()

    r = svc.reserve_room("RDEMO1", "H1", "C1", "2026-07-01", "2026-07-03")
    print(f"Reserved: {r}")

    svc.cancel_reservation("RDEMO1")
    print("Cancelled reservation RDEMO1")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2

    cmd = argv[1].strip().lower()
    if cmd == "seed":
        seed()
        return 0
    if cmd == "demo":
        demo()
        return 0

    print(f"Unknown command: {cmd}")
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
