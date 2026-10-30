"""Test data factory for generating dynamic Restful-Booker payloads."""
from datetime import date, timedelta
from typing import Any

from faker import Faker

# Initialize Faker instance once at module level to avoid reloading dictionaries
fake = Faker()

class BookingData:
    """Generate structured and dynamic payloads for booking API tests."""
    @staticmethod
    def valid_booking_payload(**overrides: Any) -> dict[str, Any]:
        """Generate a valid booking payload, allowing specific field overrides."""
        # Calculate dynamic future dates so tests never expire over time
        checkin_date = date.today() + timedelta(days=fake.random_int(min=1, max=30))
        checkout_date = checkin_date + timedelta(days=fake.random_int(min=1, max=14))
        payload: dict[str, Any] = {
            "firstname": fake.first_name(),
            "lastname": fake.last_name(),
            "totalprice": fake.random_int(min=50, max=2000),
            "depositpaid": fake.boolean(),
            "bookingdates": {
                # Format dates as YYYY-MM-DD strings required by the API contract
                "checkin": checkin_date.strftime("%Y-%m-%d"),
                "checkout": checkout_date.strftime("%Y-%m-%d")
            },
            "additionalneeds": fake.random_element(
                elements=("Breakfast", "Late Checkout", "Airport Shuttle", "Extra Bed")
            )
        }
        # Mutate default random values if specific fields are passed via kwargs
        payload.update(overrides)
        return payload
