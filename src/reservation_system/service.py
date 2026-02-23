"""Application service for managing hotels, customers, and reservations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .customer import Customer
from .exceptions import ConflictError, NotFoundError, ValidationError
from .hotel import Hotel
from .reservation import Reservation
from .storage import JsonStore


def _idx(items: List[dict], key: str) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for it in items:
        val = it.get(key)
        if isinstance(val, str) and val.strip():
            out[val.strip()] = it
        else:
            msg = "[ERROR] Skipping record with invalid {}: {}".format(key, it)
            print(msg)
    return out


def _overlap(a: Tuple[str, str], b: Tuple[str, str]) -> bool:
    a_s, a_e = a
    b_s, b_e = b
    return a_s < b_e and b_s < a_e


@dataclass(slots=True)
class ReservationService:
    store: JsonStore

    # -------- Hotels --------
    def create_hotel(self, hotel: Hotel) -> None:
        hotels = self.store.load_hotels()
        by_id = _idx(hotels, "hotel_id")
        if hotel.hotel_id in by_id:
            raise ConflictError("Hotel already exists.")
        hotels.append(hotel.to_dict())
        self.store.save_hotels(hotels)

    def get_hotel(self, hotel_id: str) -> Hotel:
        if not isinstance(hotel_id, str) or not hotel_id.strip():
            raise ValidationError("hotel_id must be a non-empty string.")
        hotels = self.store.load_hotels()
        by_id = _idx(hotels, "hotel_id")
        if hotel_id not in by_id:
            raise NotFoundError("Hotel not found.")
        return Hotel.from_dict(by_id[hotel_id])

    def delete_hotel(self, hotel_id: str) -> None:
        if not isinstance(hotel_id, str) or not hotel_id.strip():
            raise ValidationError("hotel_id must be a non-empty string.")
        hotels = self.store.load_hotels()
        before = len(hotels)
        hotels = [h for h in hotels if h.get("hotel_id") != hotel_id]
        if len(hotels) == before:
            raise NotFoundError("Hotel not found.")
        # Remove linked reservations
        res = self.store.load_reservations()
        res = [r for r in res if r.get("hotel_id") != hotel_id]
        self.store.save_hotels(hotels)
        self.store.save_reservations(res)

    def update_hotel(
        self,
        hotel_id: str,
        *,
        name: Optional[str] = None,
        city: Optional[str] = None,
        rooms_total: Optional[int] = None,
    ) -> Hotel:
        hotels = self.store.load_hotels()
        updated: List[dict] = []
        found = False

        for it in hotels:
            if it.get("hotel_id") != hotel_id:
                updated.append(it)
                continue

            found = True
            patched = dict(it)
            if name is not None:
                patched["name"] = name
            if city is not None:
                patched["city"] = city
            if rooms_total is not None:
                patched["rooms_total"] = rooms_total

            h = Hotel.from_dict(patched)  # validates
            updated.append(h.to_dict())

        if not found:
            raise NotFoundError("Hotel not found.")
        self.store.save_hotels(updated)
        return self.get_hotel(hotel_id)


    # ---------------- Customers ----------------
    def create_customer(self, cust: Customer) -> None:
        customers = self.store.load_customers()
        by_id = _idx(customers, "customer_id")
        if cust.customer_id in by_id:
            raise ConflictError("Customer already exists.")
        customers.append(cust.to_dict())
        self.store.save_customers(customers)

    def get_customer(self, customer_id: str) -> Customer:
        if not isinstance(customer_id, str) or not customer_id.strip():
            raise ValidationError("customer_id must be a non-empty string.")
        customers = self.store.load_customers()
        by_id = _idx(customers, "customer_id")
        if customer_id not in by_id:
            raise NotFoundError("Customer not found.")
        return Customer.from_dict(by_id[customer_id])

    def delete_customer(self, customer_id: str) -> None:
        if not isinstance(customer_id, str) or not customer_id.strip():
            raise ValidationError("customer_id must be a non-empty string.")
        customers = self.store.load_customers()
        before = len(customers)
        customers = [c for c in customers if c.get("customer_id") != customer_id]
        if len(customers) == before:
            raise NotFoundError("Customer not found.")

        # Remove linked reservations to keep storage consistent
        res = self.store.load_reservations()
        res = [r for r in res if r.get("customer_id") != customer_id]

        self.store.save_customers(customers)
        self.store.save_reservations(res)

    def update_customer(
        self,
        customer_id: str,
        *,
        name_full: Optional[str] = None,
        email: Optional[str] = None,
    ) -> Customer:
        customers = self.store.load_customers()
        updated: List[dict] = []
        found = False

        for it in customers:
            if it.get("customer_id") != customer_id:
                updated.append(it)
                continue

            found = True
            patched = dict(it)
            if name_full is not None:
                patched["name_full"] = name_full
            if email is not None:
                patched["email"] = email

            c = Customer.from_dict(patched)  # validates
            updated.append(c.to_dict())

        if not found:
            raise NotFoundError("Customer not found.")
        self.store.save_customers(updated)
        return self.get_customer(customer_id)

    # ---------------- Reservations ----------------
    def create_reservation(self, resv: Reservation) -> Reservation:
        # Ensure hotel and customer exist
        _ = self.get_hotel(resv.hotel_id)
        _ = self.get_customer(resv.customer_id)

        res_list = self.store.load_reservations()
        by_id = _idx(res_list, "resv_id")
        if resv.resv_id in by_id:
            raise ConflictError("Reservation already exists.")

        room_no = resv.room_no
        if room_no is None:
            room_no = self._find_room(resv.hotel_id, resv.check_in, resv.check_out)

        hotel = self.get_hotel(resv.hotel_id)
        if room_no < 1 or room_no > hotel.rooms_total:
            raise ValidationError("room_no is out of hotel room range.")

        if self._room_busy(resv.hotel_id, room_no, resv.check_in, resv.check_out):
            raise ConflictError("Room is not available for those dates.")

        created = Reservation(
            resv_id=resv.resv_id,
            hotel_id=resv.hotel_id,
            customer_id=resv.customer_id,
            check_in=resv.check_in,
            check_out=resv.check_out,
            room_no=room_no,
        )
        res_list.append(created.to_dict())
        self.store.save_reservations(res_list)
        return created

    def cancel_reservation(self, resv_id: str) -> None:
        if not isinstance(resv_id, str) or not resv_id.strip():
            raise ValidationError("resv_id must be a non-empty string.")
        res_list = self.store.load_reservations()
        before = len(res_list)
        res_list = [r for r in res_list if r.get("resv_id") != resv_id]
        if len(res_list) == before:
            raise NotFoundError("Reservation not found.")
        self.store.save_reservations(res_list)

    def reserve_room(
        self,
        resv_id: str,
        hotel_id: str,
        customer_id: str,
        check_in: str,
        check_out: str,
        room_no: Optional[int] = None,
    ) -> Reservation:
        """Convenience wrapper to match 'Reserve a Room' requirement."""
        resv = Reservation(
            resv_id=resv_id,
            hotel_id=hotel_id,
            customer_id=customer_id,
            check_in=check_in,
            check_out=check_out,
            room_no=room_no,
        )
        return self.create_reservation(resv)

    def _room_busy(
        self,
        hotel_id: str,
        room_no: int,
        check_in: str,
        check_out: str,
    ) -> bool:
        raw = self.store.load_reservations()
        existing: List[Reservation] = []
        for it in raw:
            if it.get("hotel_id") == hotel_id and it.get("room_no") == room_no:
                try:
                    existing.append(Reservation.from_dict(it))
                except Exception as exc:
                    print(f"[ERROR] Skipping invalid reservation record: {it} ({exc})")

        new_range = (check_in, check_out)
        for r in existing:
            if _overlap(new_range, (r.check_in, r.check_out)):
                return True
        return False

    def _find_room(self, hotel_id: str, check_in: str, check_out: str) -> int:
        hotel = self.get_hotel(hotel_id)
        for rn in range(1, hotel.rooms_total + 1):
            if not self._room_busy(hotel_id, rn, check_in, check_out):
                return rn
        raise ConflictError("No rooms available for those dates.")
