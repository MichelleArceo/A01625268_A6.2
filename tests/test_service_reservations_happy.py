import os
import tempfile
import unittest

from reservation_system.customer import Customer
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


class TestReservationsHappy(unittest.TestCase):
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

    def test_reserve_room_auto_assigns_room(self) -> None:
        r = self.svc.reserve_room(
            resv_id="R1",
            hotel_id="H1",
            customer_id="C1",
            check_in="2026-02-25",
            check_out="2026-02-28",
        )
        self.assertIsNotNone(r.room_no)
        self.assertIn(r.room_no, (1, 2))

    def test_reserve_room_with_specific_room(self) -> None:
        r = self.svc.reserve_room(
            resv_id="R2",
            hotel_id="H1",
            customer_id="C1",
            check_in="2026-03-01",
            check_out="2026-03-03",
            room_no=1,
        )
        self.assertEqual(r.room_no, 1)

    def test_cancel_reservation(self) -> None:
        self.svc.reserve_room(
            resv_id="R3",
            hotel_id="H1",
            customer_id="C1",
            check_in="2026-04-01",
            check_out="2026-04-03",
            room_no=2,
        )
        self.svc.cancel_reservation("R3")
        # Cancel again should raise NotFoundError (tested in negative tests later)
