import os
import tempfile
import unittest

from reservation_system.customer import Customer
from reservation_system.service import ReservationService
from reservation_system.storage import JsonStore, StorePaths


def make_service(tmpdir: str) -> ReservationService:
    paths = StorePaths(
        hotels=os.path.join(tmpdir, "hotels.json"),
        customers=os.path.join(tmpdir, "customers.json"),
        reservations=os.path.join(tmpdir, "reservations.json"),
    )
    return ReservationService(store=JsonStore(paths))


class TestCustomersHappy(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.svc = make_service(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_create_and_get_customer(self) -> None:
        c = Customer("C1", "Michelle", "michelle@example.com")
        self.svc.create_customer(c)
        loaded = self.svc.get_customer("C1")
        self.assertEqual(loaded.email, "michelle@example.com")

    def test_update_customer(self) -> None:
        self.svc.create_customer(Customer("C1", "A", "a@x.com"))
        updated = self.svc.update_customer("C1", name_full="A2", email="a2@x.com")
        self.assertEqual(updated.name_full, "A2")
        self.assertEqual(updated.email, "a2@x.com")

    def test_delete_customer(self) -> None:
        self.svc.create_customer(Customer("C1", "A", "a@x.com"))
        self.svc.delete_customer("C1")
        with self.assertRaises(Exception):
            self.svc.get_customer("C1")
