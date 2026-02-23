import os
import tempfile
import unittest

from reservation_system.exceptions import (
    ConflictError,
    NotFoundError,
    ValidationError,
)
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


class TestHotelsNegative(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.svc = make_service(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_create_duplicate_hotel(self) -> None:
        self.svc.create_hotel(Hotel("H1", "A", "B", 1))
        with self.assertRaises(ConflictError):
            self.svc.create_hotel(Hotel("H1", "A2", "B2", 2))

    def test_get_missing_hotel(self) -> None:
        with self.assertRaises(NotFoundError):
            self.svc.get_hotel("NOPE")

    def test_delete_missing_hotel(self) -> None:
        with self.assertRaises(NotFoundError):
            self.svc.delete_hotel("NOPE")

    def test_get_invalid_id(self) -> None:
        with self.assertRaises(ValidationError):
            self.svc.get_hotel("")

    def test_update_invalid_rooms(self) -> None:
        self.svc.create_hotel(Hotel("H1", "A", "B", 2))
        with self.assertRaises(ValidationError):
            self.svc.update_hotel("H1", rooms_total=0)
