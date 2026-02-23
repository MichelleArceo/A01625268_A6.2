import os
import tempfile
import unittest

from reservation_system.customer import Customer
from reservation_system.exceptions import ConflictError, NotFoundError
from reservation_system.hotel import Hotel
from reservation_system.service import ReservationService
from reservation_system.storage import JsonStore, StorePaths


def make_service(tmpdir: str) -> ReservationService:
    paths = StorePaths(
        hotels=os.path.join(tmpdir, "hotels.json"),
        customers=os.path.join(tmpdir, "customers.json"),
        reservations=os.path.join(tmpdir, "reservations.json"),
    )
    return ReservationService(store=JsonStore(paths))


class TestReservationsOverlapNegative(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.svc = make_service(self.tmp.name)
        self.svc.create_hotel(Hotel("H1", "Michelle Inn", "Nagoya", 2))
        self.svc.create_customer(Customer("C1", "Michelle", "michelle@example.com"))

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_overlap_same_room_raises_conflict(self) -> None:
        self.svc.reserve_room("R1", "H1", "C1", "2026-02-25", "2026-02-28", room_no=1)
        with self.assertRaises(ConflictError):
            self.svc.reserve_room("R2", "H1", "C1", "2026-02-26", "2026-02-27", room_no=1)

    def test_duplicate_reservation_id_raises_conflict(self) -> None:
        self.svc.reserve_room("R1", "H1", "C1", "2026-03-01", "2026-03-03", room_no=1)
        with self.assertRaises(ConflictError):
            self.svc.reserve_room("R1", "H1", "C1", "2026-04-01", "2026-04-03", room_no=2)

    def test_cancel_missing_reservation_raises_notfound(self) -> None:
        with self.assertRaises(NotFoundError):
            self.svc.cancel_reservation("NOPE")
