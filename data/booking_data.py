"""Test data factory for generating dynamic Restful-Booker payloads."""

import string
from datetime import date, timedelta
from typing import Any

from faker import Faker

from config.config import Config

# Initialize Faker instance once at module level to avoid reloading dictionaries
fake = Faker()


class BookingData:
    """Generate structured and dynamic payloads for booking API tests."""

    @staticmethod
    def valid_auth_payload(**overrides: Any) -> dict[str, Any]:
        """Generate a valid authentication payload, allowing specific field overrides."""
        payload: dict[str, Any] = {
            "username": Config.BOOKING_USERNAME,
            "password": Config.BOOKING_PASSWORD,
        }
        # Override default credentials if specific values are passed
        payload.update(overrides)
        return payload

    @staticmethod
    def invalid_auth_credentials() -> list[tuple[str, dict[str, Any]]]:
        """Generate single-fault string credential mutations for negative auth tests."""
        return [
            # Partition A: Incorrect values via Faker
            (
                "incorrect_username",
                BookingData.valid_auth_payload(username=fake.user_name()),
            ),
            (
                "incorrect_password",
                BookingData.valid_auth_payload(password=fake.password()),
            ),
            # Partition B: Case sensitivity (.upper())
            (
                "uppercase_username",
                BookingData.valid_auth_payload(
                    username=Config.BOOKING_USERNAME.upper()
                ),
            ),
            (
                "uppercase_password",
                BookingData.valid_auth_payload(
                    password=Config.BOOKING_PASSWORD.upper()
                ),
            ),
            # Partition C: Leading and trailing whitespace
            (
                "whitespace_username",
                BookingData.valid_auth_payload(username=f" {Config.BOOKING_USERNAME} "),
            ),
            (
                "whitespace_password",
                BookingData.valid_auth_payload(password=f" {Config.BOOKING_PASSWORD} "),
            ),
            # Partition D: Special characters / punctuation strings
            (
                "special_chars_username",
                BookingData.valid_auth_payload(
                    username=f"{Config.BOOKING_USERNAME}{string.punctuation}"
                ),
            ),
            (
                "special_chars_password",
                BookingData.valid_auth_payload(
                    password=f"{Config.BOOKING_PASSWORD}{string.punctuation}"
                ),
            ),
        ]

    @staticmethod
    def malformed_auth_payloads() -> list[tuple[str, dict[str, Any]]]:
        """Generate empty, missing-key, and non-string payloads for negative auth tests."""
        return [
            # Partition E: Empty strings (Single-Fault - 2 sides)
            (
                "empty_username",
                BookingData.valid_auth_payload(username=""),
            ),
            (
                "empty_password",
                BookingData.valid_auth_payload(password=""),
            ),
            # Partition F: Missing keys / Structural schema (3 sides)
            (
                "missing_username_key",
                BookingData.remove_key(BookingData.valid_auth_payload(), "username"),
            ),
            (
                "missing_password_key",
                BookingData.remove_key(BookingData.valid_auth_payload(), "password"),
            ),
            (
                "empty_json_object",
                BookingData.empty_payload(),
            ),
            # Partition G: Integer data type (Single-Fault - 2 sides)
            (
                "int_username",
                BookingData.valid_auth_payload(username=fake.random_int()),
            ),
            (
                "int_password",
                BookingData.valid_auth_payload(password=fake.random_int()),
            ),
            # Partition H: Boolean data type (Single-Fault - 2 sides)
            (
                "bool_username",
                BookingData.valid_auth_payload(username=True),
            ),
            (
                "bool_password",
                BookingData.valid_auth_payload(password=True),
            ),
            # Partition I: Null / None data type (Single-Fault - 2 sides)
            (
                "null_username",
                BookingData.valid_auth_payload(username=None),
            ),
            (
                "null_password",
                BookingData.valid_auth_payload(password=None),
            ),
            # Partition J: List / Array data type (Single-Fault - 2 sides)
            (
                "list_username",
                BookingData.valid_auth_payload(username=[Config.BOOKING_USERNAME]),
            ),
            (
                "list_password",
                BookingData.valid_auth_payload(password=[Config.BOOKING_PASSWORD]),
            ),
        ]

    @staticmethod
    def invalid_auth_payload() -> dict[str, Any]:
        """Generate a representative invalid authentication payload via Faker."""
        return {
            "username": fake.user_name(),
            "password": fake.password(),
        }

    @staticmethod
    def empty_payload() -> dict[str, Any]:
        """Generate an empty JSON object payload lacking all required schema keys."""
        return {}

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
                "checkin": checkin_date.isoformat(),
                "checkout": checkout_date.isoformat(),
            },
            "additionalneeds": fake.random_element(
                elements=("Breakfast", "Late Checkout", "Airport Shuttle", "Extra Bed")
            ),
        }
        # Mutate default random values if specific fields are passed via kwargs
        payload.update(overrides)
        return payload

    @staticmethod
    def valid_booking_variations() -> list[tuple[str, dict[str, Any]]]:
        """Generate valid contract variations and boundary payloads for create booking."""
        checkin_date = date.today() + timedelta(days=fake.random_int(min=1, max=30))
        checkout_date = checkin_date + timedelta(days=1)
        one_night_dates = {
            "checkin": checkin_date.isoformat(),
            "checkout": checkout_date.isoformat(),
        }
        return [
            # Contract variation: Omit implicit optional field 'additionalneeds'
            (
                "without_additionalneeds",
                BookingData.remove_key(
                    BookingData.valid_booking_payload(), "additionalneeds"
                ),
            ),
            # Boundary Value Analysis (BVA): Minimum positive integer price ($1)
            (
                "minimum_valid_totalprice",
                BookingData.valid_booking_payload(totalprice=1),
            ),
            # Boundary Value Analysis (BVA): Minimum valid hotel stay (1 night)
            (
                "one_night_minimum_stay",
                BookingData.valid_booking_payload(bookingdates=one_night_dates),
            ),
        ]

    @staticmethod
    def remove_key(payload: dict[str, Any], *keys: str) -> dict[str, Any]:
        """Remove a root or nested key path from a dictionary payload."""
        target = payload
        for key in keys[:-1]:
            target = target[key]
        target.pop(keys[-1])
        return payload

    @staticmethod
    def missing_required_booking_fields() -> list[tuple[str, dict[str, Any]]]:
        """Generate single-fault payloads missing one required key at a time."""
        return [
            # Root-level required schema keys (5 sides)
            (
                "missing_firstname",
                BookingData.remove_key(
                    BookingData.valid_booking_payload(), "firstname"
                ),
            ),
            (
                "missing_lastname",
                BookingData.remove_key(BookingData.valid_booking_payload(), "lastname"),
            ),
            (
                "missing_totalprice",
                BookingData.remove_key(
                    BookingData.valid_booking_payload(), "totalprice"
                ),
            ),
            (
                "missing_depositpaid",
                BookingData.remove_key(
                    BookingData.valid_booking_payload(), "depositpaid"
                ),
            ),
            (
                "missing_bookingdates",
                BookingData.remove_key(
                    BookingData.valid_booking_payload(), "bookingdates"
                ),
            ),
            # Nested required schema keys inside 'bookingdates' (2 sides)
            (
                "missing_checkin",
                BookingData.remove_key(
                    BookingData.valid_booking_payload(), "bookingdates", "checkin"
                ),
            ),
            (
                "missing_checkout",
                BookingData.remove_key(
                    BookingData.valid_booking_payload(), "bookingdates", "checkout"
                ),
            ),
            # Structural edge case: Empty JSON object (1 side)
            (
                "empty_json_object",
                BookingData.empty_payload(),
            ),
        ]

    @staticmethod
    def unhandled_booking_field_types() -> list[tuple[str, dict[str, Any]]]:
        """Generate incompatible field types that trigger unhandled 500 server exceptions."""
        return [
            # Integer in string field: breaks backend string operations on firstname
            (
                "non_string_firstname",
                BookingData.valid_booking_payload(firstname=fake.random_int()),
            ),
            # Integer in string field: breaks backend string operations on lastname
            (
                "non_string_lastname",
                BookingData.valid_booking_payload(lastname=fake.random_int()),
            ),
            # Scalar string in dict field: breaks backend property access on bookingdates
            (
                "non_dict_bookingdates",
                BookingData.valid_booking_payload(bookingdates=fake.word()),
            ),
        ]
