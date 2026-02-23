import os
import tempfile
import unittest

from reservation_system.customer import Customer
from reservation_system.exceptions import ValidationError
from reservation_system.hotel import Hotel
from reservation_system.reservation import Reservation
from reservation_system.service import ReservationService
from reservation_system.storage import JsonStore, StorePaths


def make_service(tmpdir: str) -> ReservationService:
    paths = StorePaths(
        hotels=os.path.join(tmpdir, "hotels.json"),
        customers=os.path.join(tmpdir, "customers.json"),
        reservations=os.path.join(tmpdir, "reservations.json"),
    )
    return ReservationService(store=JsonStore(paths))


class TestReservationsInvalidDateNegative(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.svc = make_service(self.tmp.name)
        self.svc.create_hotel(Hotel("H1", "Michelle Inn", "Nagoya", 2))
        self.svc.create_customer(
            Customer("C1",
            "Michelle",
            "michelle@example.com"),
        )

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_check_out_before_check_in_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            Reservation("R1", "H1", "C1", "2026-02-28", "2026-02-25")

    def test_invalid_date_format_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            Reservation("R2", "H1", "C1", "2026/02/25", "2026-02-28")

    def test_room_out_of_range_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            self.svc.reserve_room("R3", "H1", "C1", "2026-05-01", "2026-05-03", room_no=99)
