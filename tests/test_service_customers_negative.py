import os
import tempfile
import unittest

from reservation_system.customer import Customer
from reservation_system.exceptions import ConflictError, NotFoundError, ValidationError
from reservation_system.service import ReservationService
from reservation_system.storage import JsonStore, StorePaths


def make_service(tmpdir: str) -> ReservationService:
    paths = StorePaths(
        hotels=os.path.join(tmpdir, "hotels.json"),
        customers=os.path.join(tmpdir, "customers.json"),
        reservations=os.path.join(tmpdir, "reservations.json"),
    )
    return ReservationService(store=JsonStore(paths))


class TestCustomersNegative(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.svc = make_service(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_duplicate_customer(self) -> None:
        self.svc.create_customer(Customer("C1", "A", "a@x.com"))
        with self.assertRaises(ConflictError):
            self.svc.create_customer(Customer("C1", "B", "b@x.com"))

    def test_get_missing_customer(self) -> None:
        with self.assertRaises(NotFoundError):
            self.svc.get_customer("NOPE")

    def test_delete_missing_customer(self) -> None:
        with self.assertRaises(NotFoundError):
            self.svc.delete_customer("NOPE")

    def test_invalid_customer_id(self) -> None:
        with self.assertRaises(ValidationError):
            self.svc.get_customer("")

    def test_update_missing_customer(self) -> None:
        with self.assertRaises(NotFoundError):
            self.svc.update_customer("NOPE", name_full="X")

    def test_invalid_email_rejected(self) -> None:
        self.svc.create_customer(Customer("C1", "A", "a@x.com"))
        with self.assertRaises(ValidationError):
            self.svc.update_customer("C1", email="not-an-email")
