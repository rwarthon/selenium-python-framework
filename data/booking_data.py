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
        payload: dict[str, Any] = {
            "firstname": fake.first_name(),
            "lastname": fake.last_name(),
            "totalprice": fake.random_int(min=50, max=2000),
            "depositpaid": fake.boolean(),
            "bookingdates": BookingData.booking_dates(
                checkin_offset_days=fake.random_int(min=1, max=30),
                stay_nights=fake.random_int(min=1, max=14),
            ),
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
                BookingData.valid_booking_payload(
                    bookingdates=BookingData.booking_dates(
                        checkin_offset_days=fake.random_int(min=1, max=30),
                        stay_nights=1,
                    )
                ),
            ),
        ]

    @staticmethod
    def remove_key(payload: dict[str, Any], *keys: str) -> dict[str, Any]:
        """Remove a root or nested key path from a dictionary payload."""
        # Point target reference to the root payload dictionary in memory
        target = payload
        # Traverse parent dictionaries up to the penultimate key (keys[:-1])
        for key in keys[:-1]:
            target = target[key]
        # Remove the final target key (keys[-1]); mutates payload in place
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

    @staticmethod
    def replace_key(payload: dict[str, Any], value: Any, *keys: str) -> dict[str, Any]:
        """Replace an existing root or nested key value in a dictionary payload."""
        # Point target reference to the root payload dictionary in memory
        target = payload
        # Traverse parent dictionaries up to the penultimate key (keys[:-1])
        for key in keys[:-1]:
            target = target[key]
        # Fail-fast guard: prevent typos from silently creating a new key
        if keys[-1] not in target:
            raise KeyError(keys[-1])
        # Overwrite the final target key (keys[-1]); mutates payload in place
        target[keys[-1]] = value
        return payload

    @staticmethod
    def coerced_booking_field_types() -> list[tuple[str, dict[str, Any]]]:
        """Generate incompatible field types silently coerced by the backend."""
        return [
            # Alphabetic string in integer field: backend coerces to null
            (
                "non_numeric_totalprice",
                BookingData.valid_booking_payload(totalprice=fake.word()),
            ),
            # Non-empty string in boolean field: backend evaluates as truthy (true)
            (
                "non_boolean_depositpaid",
                BookingData.valid_booking_payload(depositpaid=fake.word()),
            ),
            # Boolean in string date field: backend coerces True to Unix Epoch 1970-01-01
            (
                "non_string_checkin",
                BookingData.replace_key(
                    BookingData.valid_booking_payload(),
                    True,
                    "bookingdates",
                    "checkin",
                ),
            ),
            # Boolean in string date field: backend coerces True to Unix Epoch 1970-01-01
            (
                "non_string_checkout",
                BookingData.replace_key(
                    BookingData.valid_booking_payload(),
                    True,
                    "bookingdates",
                    "checkout",
                ),
            ),
        ]

    @staticmethod
    def booking_dates(checkin_offset_days: int, stay_nights: int) -> dict[str, str]:
        """Generate a bookingdates dictionary from relative day offsets."""
        # checkin_offset_days: days from today (+ future, 0 today, - past)
        checkin_date = date.today() + timedelta(days=checkin_offset_days)
        # stay_nights: days relative to checkin (+ valid stay, 0 same day, - inverted)
        checkout_date = checkin_date + timedelta(days=stay_nights)
        return {
            "checkin": checkin_date.isoformat(),
            "checkout": checkout_date.isoformat(),
        }

    @staticmethod
    def invalid_booking_business_rules() -> list[tuple[str, dict[str, Any]]]:
        """Generate domain-invalid booking payloads accepted by the backend without validation."""
        return [
            # Identity rule: guest firstname cannot be an empty string
            (
                "empty_firstname",
                BookingData.valid_booking_payload(firstname=""),
            ),
            # Identity rule: guest lastname cannot be an empty string
            (
                "empty_lastname",
                BookingData.valid_booking_payload(lastname=""),
            ),
            # Pricing BVA (0): booking price cannot be $0 without a discount contract
            (
                "zero_totalprice",
                BookingData.valid_booking_payload(totalprice=0),
            ),
            # Pricing EP (< 0): booking price cannot be a negative amount
            (
                "negative_totalprice",
                BookingData.valid_booking_payload(
                    totalprice=fake.random_int(min=-1000, max=-1)
                ),
            ),
            # Stay duration BVA (0 nights): checkout cannot be on the same day as checkin
            (
                "same_day_checkin_checkout",
                BookingData.valid_booking_payload(
                    bookingdates=BookingData.booking_dates(
                        checkin_offset_days=fake.random_int(min=1, max=30),
                        stay_nights=0,
                    )
                ),
            ),
            # Chronological rule (< 0 nights): checkout cannot precede checkin date
            (
                "checkout_before_checkin",
                BookingData.valid_booking_payload(
                    bookingdates=BookingData.booking_dates(
                        checkin_offset_days=fake.random_int(min=1, max=30),
                        stay_nights=fake.random_int(min=-14, max=-1),
                    )
                ),
            ),
            # Past date rule: new bookings cannot be scheduled in the past
            (
                "past_booking_dates",
                BookingData.valid_booking_payload(
                    bookingdates=BookingData.booking_dates(
                        checkin_offset_days=fake.random_int(min=-45, max=-15),
                        stay_nights=fake.random_int(min=1, max=14),
                    )
                ),
            ),
            # Date format rule: non-ISO string in checkin is stored as '0NaN-aN-aN'
            (
                "malformed_checkin_date",
                BookingData.replace_key(
                    BookingData.valid_booking_payload(),
                    "invalid-date",
                    "bookingdates",
                    "checkin",
                ),
            ),
            # Date calendar rule: impossible month/day in checkout is stored as '0NaN-aN-aN'
            (
                "malformed_checkout_date",
                BookingData.replace_key(
                    BookingData.valid_booking_payload(),
                    "2026-13-45",
                    "bookingdates",
                    "checkout",
                ),
            ),
        ]

    @staticmethod
    def decimal_price_booking_payload() -> dict[str, Any]:
        """Generate a valid booking payload with a non-zero decimal totalprice."""
        # Generate a random float price across the full valid domain [50, 2000]
        price = fake.pyfloat(min_value=50, max_value=2000, right_digits=2)
        # Re-sample if pyfloat lands on an exact .00 integer value
        while price.is_integer():
            price = fake.pyfloat(min_value=50, max_value=2000, right_digits=2)
        return BookingData.valid_booking_payload(totalprice=price)

    @staticmethod
    def invalid_booking_ids() -> list[tuple[str, Any]]:
        """Generate non-existent and invalid booking IDs for negative lookup tests."""
        return [
            # Valid 32-bit int in high range [100M, 999M] to avoid colliding with active DB IDs
            (
                "non_existent_booking_id",
                fake.random_int(min=100_000_000, max=999_999_999),
            ),
            # ID BVA (0): lower invalid boundary since auto-increment IDs start at 1
            (
                "zero_booking_id",
                0,
            ),
            # ID EP (< 0): negative integer is invalid for a primary key identifier
            (
                "negative_booking_id",
                fake.random_int(min=-1000, max=-1),
            ),
            # Incompatible type: alphabetic string in numeric URI path parameter
            (
                "non_numeric_booking_id",
                fake.word(),
            ),
        ]

    @staticmethod
    def valid_name_filter_keys() -> list[tuple[str, str]]:
        """Return single-fault name filter keys for positive search tests."""
        return [
            # Partition: Exact match by guest first name
            ("filter_by_firstname", "firstname"),
            # Partition: Exact match by guest last name
            ("filter_by_lastname", "lastname"),
        ]

    @staticmethod
    def non_existent_name_filters() -> list[tuple[str, dict[str, str]]]:
        """Generate collision-free alphabetic name filters for negative search tests."""
        return [
            # Partition: Valid alphabetic first name not present in database
            (
                "non_existent_firstname",
                {"firstname": fake.first_name() + fake.lexify(text="????????")},
            ),
            # Partition: Valid alphabetic last name not present in database
            (
                "non_existent_lastname",
                {"lastname": fake.last_name() + fake.lexify(text="????????")},
            ),
        ]

    @staticmethod
    def date_filter_params(
        booking: dict[str, Any], field: str, day_offset: int
    ) -> dict[str, str]:
        """Build a date query filter shifted by a boundary day offset."""
        # booking: inner booking payload; field: 'checkin' or 'checkout'
        base_date = date.fromisoformat(booking["bookingdates"][field])
        # day_offset: days relative to base_date (-1 before, 0 same day, +1 after)
        target_date = (base_date + timedelta(days=day_offset)).isoformat()
        return {field: target_date}
