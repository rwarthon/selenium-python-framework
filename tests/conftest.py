"""Global Pytest fixtures for test orchestration and dependency injection."""

from collections.abc import Iterator

import pytest

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
    response = service.authenticate()
    # Close session immediately after receiving response to prevent connection leaks
    service.close()
    # Precondition check: Abort session setup if authentication fails
    if response.status_code != 200 or "token" not in response.json():
        pytest.fail(
            f"Precondition failed: Could not obtain auth token. "
            f"Status: {response.status_code}, Response: {response.text}"
        )
    return response.json()["token"]
