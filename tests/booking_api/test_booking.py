"""Test suite for Restful-Booker API operations."""
import pytest

from data.booking_data import BookingData
from services.booking_service import BookingService


@pytest.mark.api
@pytest.mark.smoke
def test_health_check(booking_service: BookingService) -> None:
    """Verify that the Booking API server is up and responding to ping."""
    # Arrange: Handled implicitly via the booking_service fixture
    # Act: Send health check request
    response = booking_service.ping()
    # Assert: Restful-Booker returns 201 Created for /ping health check
    assert response.status_code == 201, f"Expected 201, but got {response.status_code}"

@pytest.mark.api
@pytest.mark.smoke
def test_create_and_verify_booking(booking_service: BookingService) -> None:
    """Verify booking creation via POST and data persistence via GET."""
    # Arrange: Generate dynamic booking payload
    payload = BookingData.valid_booking_payload()
    # Act 1: Create the booking
    post_response = booking_service.create_booking(payload)
    # Assert 1: Verify creation status, ID generation, and returned booking object
    assert post_response.status_code == 200
    post_data = post_response.json()
    assert "bookingid" in post_data
    assert isinstance(post_data["bookingid"], int)
    assert post_data["booking"] == payload
    # Act 2: Retrieve the created booking by ID to confirm backend persistence
    booking_id = post_data["bookingid"]
    get_response = booking_service.get_booking(booking_id)
    # Assert 2: Verify persisted record matches the original payload exactly
    assert get_response.status_code == 200
    assert get_response.json() == payload
