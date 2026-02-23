import os
import tempfile
import unittest

from reservation_system.storage import JsonStore, StorePaths


class TestInvalidJson(unittest.TestCase):
    def test_invalid_json_returns_empty_list(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            hotels = os.path.join(tmp, "hotels.json")
            customers = os.path.join(tmp, "customers.json")
            reservations = os.path.join(tmp, "reservations.json")

            with open(hotels, "w", encoding="utf-8") as f:
                f.write("{ not valid json }")

            store = JsonStore(StorePaths(hotels=hotels, customers=customers, reservations=reservations))
            items = store.load_hotels()
            self.assertEqual(items, [])

    def test_wrong_type_json_returns_empty_list(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            hotels = os.path.join(tmp, "hotels.json")
            customers = os.path.join(tmp, "customers.json")
            reservations = os.path.join(tmp, "reservations.json")

            with open(customers, "w", encoding="utf-8") as f:
                f.write('{"oops": true}')

            store = JsonStore(StorePaths(hotels=hotels, customers=customers, reservations=reservations))
            items = store.load_customers()
            self.assertEqual(items, [])

    def test_missing_file_returns_empty_list(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            hotels = os.path.join(tmp, "hotels.json")
            customers = os.path.join(tmp, "customers.json")
            reservations = os.path.join(tmp, "reservations.json")

            store = JsonStore(StorePaths(hotels=hotels, customers=customers, reservations=reservations))
            self.assertEqual(store.load_reservations(), [])
