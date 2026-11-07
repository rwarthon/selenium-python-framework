"""Test suite for Restful-Booker API operations."""

from typing import Any

import pytest

from data.booking_data import BookingData
from services.booking_service import BookingService


@pytest.mark.api
class TestPing:
    """Test suite for the /ping health check endpoint."""

    @pytest.mark.smoke
    def test_health_check(self, booking_service: BookingService) -> None:
        """Verify that the Booking API server is up and responding to ping."""
        # Arrange: Handled implicitly via the booking_service fixture
        # Act: Send health check request
        response = booking_service.ping()
        # Assert: Audit note - Restful-Booker returns 201 instead of 200
        # (RFC 9110 standard compliance is audited in test_health_check_returns_200_ok)
        assert response.status_code == 201, (
            f"Expected 201, but got {response.status_code}"
        )
        assert response.text == "Created", (
            f"Expected 'Created' response body, but got {response.text}"
        )

    @pytest.mark.xfail(
        reason=(
            "Audit defect: Restful-Booker returns 201 Created instead of "
            "200 OK on an idempotent GET health check per RFC 9110"
        ),
        strict=True,
    )
    def test_health_check_returns_200_ok(self, booking_service: BookingService) -> None:
        """Audit that GET /ping should return HTTP 200 OK per REST standards."""
        # Arrange: Handled implicitly via the booking_service fixture
        # Act: Send health check request
        response = booking_service.ping()
        # Assert: Expect standard 200 OK status code for a read-only GET request
        assert response.status_code == 200, (
            f"Expected 200 OK, but got {response.status_code}"
        )


@pytest.mark.api
class TestAuth:
    """Test suite for the /auth authentication endpoint."""

    @pytest.mark.smoke
    def test_auth_valid_credentials(self, booking_service: BookingService) -> None:
        """Verify that valid credentials return a 200 status and a non-empty token."""
        # Arrange: Generate valid authentication payload from environment config
        payload = BookingData.valid_auth_payload()
        # Act: Request authentication token
        response = booking_service.authenticate(payload)
        # Assert: Verify HTTP 200 and non-empty string token in response JSON
        assert response.status_code == 200, (
            f"Expected 200, but got {response.status_code}"
        )
        body = response.json()
        assert "token" in body, "Expected 'token' key in authentication response"
        assert isinstance(body["token"], str), (
            f"Expected token to be str, but got {type(body['token'])}"
        )
        assert len(body["token"]) > 0, "Expected non-empty authentication token"

    @pytest.mark.parametrize(
        ("case_id", "payload"),
        BookingData.invalid_auth_credentials(),
    )
    def test_auth_invalid_credentials(
        self,
        booking_service: BookingService,
        case_id: str,
        payload: dict[str, Any],
    ) -> None:
        """Verify that invalid string credentials never return a token."""
        # Arrange: Provided via parametrize (case_id and mutated payload)
        # Act: Attempt authentication with invalid string credentials
        response = booking_service.authenticate(payload)
        # Assert: Audit note - Restful-Booker returns 200 OK instead of 401
        # (HTTP 401 standard compliance is audited in test_auth_invalid_credentials_returns_401)
        assert response.status_code == 200, (
            f"[{case_id}]Expected 200, but got {response.status_code}"
        )
        body = response.json()
        assert "token" not in body, (
            f"[{case_id}] Security breach: 'token' returned for invalid credentials"
        )
        assert body.get("reason") == "Bad credentials", (
            f"[{case_id}] Expected 'Bad credentials', but got '{body.get('reason')}'"
        )

    @pytest.mark.parametrize(
        ("case_id", "payload"),
        BookingData.malformed_auth_payloads(),
    )
    def test_auth_empty_or_malformed_payloads(
        self,
        booking_service: BookingService,
        case_id: str,
        payload: dict[str, Any],
    ) -> None:
        """Verify that empty or malformed payloads are rejected without leaking a token."""
        # Arrange: Provided via parametrize (case_id and malformed payload)
        # Act: Send authentication request with malformed or incomplete data
        response = booking_service.authenticate(payload)
        # Assert: Audit note - Restful-Booker returns 200 OK instead of 400
        # (HTTP 400 standard compliance is audited in test_auth_malformed_payload_returns_400)
        assert response.status_code == 200, (
            f"[{case_id}]Expected 200, but got {response.status_code}"
        )
        body = response.json()
        assert "token" not in body, (
            f"[{case_id}] Security breach: 'token' returned for malformed payload"
        )

    @pytest.mark.xfail(
        reason="Audit defect: Restful-Booker returns 200 OK instead of 401 Unauthorized",
        strict=True,
    )
    def test_auth_invalid_credentials_returns_401(
        self, booking_service: BookingService
    ) -> None:
        """Audit that invalid credentials should return HTTP 401 per REST standards."""
        # Arrange: Request a representative invalid credential payload from data layer
        payload = BookingData.invalid_auth_payload()
        # Act: Attempt authentication with invalid credentials
        response = BookingService.authenticate(payload)
        # Assert: Expect standard 401 Unauthorized status code
        assert response.status_code == 401, (
            f"Expected 401 Unauthorized, but got {response.status_code}"
        )

    @pytest.mark.xfail(
        reason=(
            "Audit defect: Restful-Booker returns 200 OK with 'Bad credentials' "
            "instead of 400 Bad Request on empty JSON schema"
        ),
        strict=True,
    )
    def test_auth_malformed_payload_returns_400(
        self, booking_service: BookingService
    ) -> None:
        """Audit that an empty payload should return HTTP 400 Bad Request."""
        # Arrange: Request an empty JSON payload from data layer
        payload = BookingData.empty_payload()
        # Act: Send empty payload to authentication endpoint
        response = BookingService.authenticate(payload)
        # Assert: Expect standard 400 Bad Request status code
        assert response.status_code == 400, (
            f"Expected 400 Bad Request, but got {response.status_code}"
        )


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
