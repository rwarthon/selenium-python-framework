"""Global Pytest fixtures for test orchestration and dependency injection."""

from collections.abc import Iterator
from typing import Any

import pytest

from data.booking_data import BookingData
from services.booking_service import BookingService


@pytest.fixture(scope="function")
def booking_service() -> Iterator[BookingService]:
    """Provide a clean BookingService instance for Restful-Booker per test function."""
    # Setup: Initialize client with Restful-Booker
    service = BookingService()
    # Deliver the service instance to the test
    yield service
    # Teardown: Close the underlying TCP session after the test finishes
    service.close()


@pytest.fixture(scope="session")
def auth_token() -> str:
    """Fetch and return a valid authentication token once per test session."""
    service = BookingService()
    payload = BookingData.valid_auth_payload()
    response = service.authenticate(payload)
    # Close session immediately after receiving response to prevent connection leaks
    service.close()
    # Precondition check: Abort session setup if authentication fails
    if response.status_code != 200 or "token" not in response.json():
        pytest.fail(
            f"Precondition failed: Could not obtain auth token. "
            f"Status: {response.status_code}, Response: {response.text}"
        )
    return response.json()["token"]


@pytest.fixture(scope="function")
def created_booking(booking_service: BookingService) -> dict[str, Any]:
    """Create a fresh booking per test function and return its ID and payload."""
    payload = BookingData.valid_booking_payload()
    response = booking_service.create_booking(payload)
    # Precondition check: Abort test setup if booking creation fails
    if response.status_code != 200 or "bookingid" not in response.json():
        pytest.fail(
            f"Precondition failed: Could not create booking. "
            f"Status: {response.status_code}, Response: {response.text}"
        )
    return response.json()
