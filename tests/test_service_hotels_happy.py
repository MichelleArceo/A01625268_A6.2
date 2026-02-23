import os
import tempfile
import unittest

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


class TestHotelsHappy(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.svc = make_service(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_create_and_get_hotel(self) -> None:
        h = Hotel("H1", “Michelle Inn", "Nagoya", 3)
        self.svc.create_hotel(h)
        loaded = self.svc.get_hotel("H1")
        self.assertEqual(loaded.name, “Michelle Inn")

    def test_update_hotel(self) -> None:
        self.svc.create_hotel(Hotel("H1", "A", "B", 2))
        updated = self.svc.update_hotel("H1", name="A2", rooms_total=4)
        self.assertEqual(updated.name, "A2")
        self.assertEqual(updated.rooms_total, 4)

    def test_delete_hotel(self) -> None:
        self.svc.create_hotel(Hotel("H1", "A", "B", 1))
        self.svc.delete_hotel("H1")
        with self.assertRaises(Exception):
            self.svc.get_hotel("H1")
