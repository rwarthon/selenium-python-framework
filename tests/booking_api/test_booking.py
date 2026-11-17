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
        # Arrange: Provided via parametrize (case_id and payload)
        # Act: Attempt authentication with invalid string credentials
        response = booking_service.authenticate(payload)
        # Assert: Audit note - Restful-Booker returns 200 OK instead of 401
        # (HTTP 401 standard compliance is audited in test_auth_invalid_credentials_returns_401)
        assert response.status_code == 200, (
            f"[{case_id}] Expected 200, but got {response.status_code}"
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
        # Arrange: Provided via parametrize (case_id and payload)
        # Act: Send authentication request with malformed or incomplete data
        response = booking_service.authenticate(payload)
        # Assert: Audit note - Restful-Booker returns 200 OK instead of 400
        # (HTTP 400 standard compliance is audited in test_auth_malformed_payload_returns_400)
        assert response.status_code == 200, (
            f"[{case_id}] Expected 200, but got {response.status_code}"
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
        response = booking_service.authenticate(payload)
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
        response = booking_service.authenticate(payload)
        # Assert: Expect standard 400 Bad Request status code
        assert response.status_code == 400, (
            f"Expected 400 Bad Request, but got {response.status_code}"
        )


@pytest.mark.api
class TestCreateBooking:
    """Test suite for the /booking creation endpoint."""

    @pytest.mark.smoke
    def test_create_and_verify_booking(self, booking_service: BookingService) -> None:
        """Verify booking creation via POST and data persistence via GET."""
        # Arrange: Generate dynamic booking payload
        payload = BookingData.valid_booking_payload()
        # Act: Create the booking via POST /booking
        create_response = booking_service.create_booking(payload)
        # Assert: Audit note - Restful-Booker returns 200 OK instead of 201 Created
        # (RFC 9110 standard compliance is audited in test_create_booking_returns_201_created)
        assert create_response.status_code == 200, (
            f"Expected 200, but got {create_response.status_code}"
        )
        create_body = create_response.json()
        assert "bookingid" in create_body, "Expected 'bookingid' key in create response"
        booking_id = create_body["bookingid"]
        assert isinstance(booking_id, int), (
            f"Expected 'bookingid' to be int, but got {type(booking_id)}"
        )
        assert create_body.get("booking") == payload, (
            f"Expected booking {payload}, but got {create_body.get('booking')}"
        )
        # Act: Retrieve the created booking via GET /booking/{id} to confirm backend persistence
        get_response = booking_service.get_booking(booking_id)
        # Assert: Verify persisted record matches the original payload exactly
        assert get_response.status_code == 200, (
            f"Expected 200 on GET, but got {get_response.status_code}"
        )
        get_body = get_response.json()
        assert get_body == payload, (
            f"Expected persisted booking {payload}, but got {get_body}"
        )

    @pytest.mark.parametrize(
        ("case_id", "payload"),
        BookingData.valid_booking_variations(),
    )
    def test_create_booking_valid_variations(
        self,
        booking_service: BookingService,
        case_id: str,
        payload: dict[str, Any],
    ) -> None:
        """Verify that valid schema variations and boundary values succeed."""
        # Arrange: Provided via parametrize (case_id and payload)
        # Act: Create the booking via POST /booking
        response = booking_service.create_booking(payload)
        # Assert: Audit note - 'additionalneeds' is undocumented as optional in API spec,
        # and endpoint returns 200 OK instead of 201 Created
        assert response.status_code == 200, (
            f"[{case_id}] Expected 200, but got {response.status_code}"
        )
        body = response.json()
        assert "bookingid" in body, (
            f"[{case_id}] Expected 'bookingid' key in create response"
        )
        booking_id = body["bookingid"]
        assert isinstance(booking_id, int), (
            f"[{case_id}] Expected 'bookingid' to be int, but got {type(booking_id)}"
        )
        assert body.get("booking") == payload, (
            f"[{case_id}] Expected booking {payload}, but got {body.get('booking')}"
        )

    @pytest.mark.parametrize(
        ("case_id", "payload"),
        BookingData.missing_required_booking_fields(),
    )
    def test_create_booking_missing_required_fields(
        self,
        booking_service: BookingService,
        case_id: str,
        payload: dict[str, Any],
    ) -> None:
        """Verify that omitting any required schema field rejects booking creation."""
        # Arrange: Provided via parametrize (case_id and payload)
        # Act: Create the booking via POST /booking
        response = booking_service.create_booking(payload)
        # Assert: Audit note - Restful-Booker returns 500 Internal Server Error instead of 400
        # (HTTP 400 standard compliance is audited in test_create_booking_invalid_schema_returns_400)
        assert response.status_code == 500, (
            f"[{case_id}] Expected 500, but got {response.status_code}"
        )
        assert response.text == "Internal Server Error", (
            f"[{case_id}] Expected 'Internal Server Error' response body, but got {response.text}"
        )

    @pytest.mark.parametrize(
        ("case_id", "payload"),
        BookingData.unhandled_booking_field_types(),
    )
    def test_create_booking_unhandled_field_type_exceptions(
        self,
        booking_service: BookingService,
        case_id: str,
        payload: dict[str, Any],
    ) -> None:
        """Verify that incompatible field types breaking the backend parser reject creation."""
        # Arrange: Provided via parametrize (case_id and payload)
        # Act: Create the booking via POST /booking
        response = booking_service.create_booking(payload)
        # Assert: Audit note - Restful-Booker returns 500 Internal Server Error instead of 400
        # (HTTP 400 standard compliance is audited in test_create_booking_invalid_schema_returns_400)
        assert response.status_code == 500, (
            f"[{case_id}] Expected 500, but got {response.status_code}"
        )
        assert response.text == "Internal Server Error", (
            f"[{case_id}] Expected 'Internal Server Error' response body, but got {response.text}"
        )

    @pytest.mark.xfail(
        reason=(
            "Audit defect: Restful-Booker silently coerces incompatible field types "
            "and returns 200 OK instead of 400 Bad Request"
        ),
        strict=True,
    )
    @pytest.mark.parametrize(
        ("case_id", "payload"),
        BookingData.coerced_booking_field_types(),
    )
    def test_create_booking_coerced_field_types(
        self,
        booking_service: BookingService,
        case_id: str,
        payload: dict[str, Any],
    ) -> None:
        """Audit that incompatible field types should return HTTP 400 instead of coercing."""
        # Arrange: Provided via parametrize (case_id and payload)
        # Act: Create the booking via POST /booking
        response = booking_service.create_booking(payload)
        # Assert: Expect standard 400 Bad Request when field types violate schema contract
        assert response.status_code == 400, (
            f"[{case_id}] Expected 400 Bad Request, but got {response.status_code}"
        )

    @pytest.mark.xfail(
        reason=(
            "Audit defect: Restful-Booker accepts domain-invalid business values "
            "and returns 200 OK instead of 400 Bad Request"
        ),
        strict=True,
    )
    @pytest.mark.parametrize(
        ("case_id", "payload"),
        BookingData.invalid_booking_business_rules(),
    )
    def test_create_booking_invalid_business_rules(
        self,
        booking_service: BookingService,
        case_id: str,
        payload: dict[str, Any],
    ) -> None:
        """Audit that domain-invalid booking values should return HTTP 400 Bad Request."""
        # Arrange: Provided via parametrize (case_id and payload)
        # Act: Create the booking via POST /booking
        response = booking_service.create_booking(payload)
        # Assert: Expect standard 400 Bad Request when business domain rules are violated
        assert response.status_code == 400, (
            f"[{case_id}] Expected 400 Bad Request, but got {response.status_code}"
        )

    @pytest.mark.xfail(
        reason=(
            "Audit defect: Restful-Booker silently truncates decimal totalprice "
            "values to integers, losing fractional cents"
        ),
        strict=True,
    )
    def test_create_booking_preserves_decimal_price(
        self, booking_service: BookingService
    ) -> None:
        """Audit that a valid decimal totalprice is preserved without truncation."""
        # Arrange: Request a booking payload with a decimal price from data layer
        payload = BookingData.decimal_price_booking_payload()
        # Act: Create the booking via POST /booking
        response = booking_service.create_booking(payload)
        # Assert: Expect HTTP 200 and exact decimal price preservation in response
        assert response.status_code == 200, (
            f"Expected 200, but got {response.status_code}"
        )
        body = response.json()
        assert body.get("booking") == payload, (
            f"Expected booking {payload}, but got {body.get('booking')}"
        )

    @pytest.mark.xfail(
        reason=(
            "Audit defect: Restful-Booker returns 500 Internal Server Error "
            "instead of 400 Bad Request on invalid or incomplete booking schema"
        ),
        strict=True,
    )
    def test_create_booking_invalid_schema_returns_400(
        self, booking_service: BookingService
    ) -> None:
        """Audit that an incomplete booking schema should return HTTP 400 Bad Request."""
        # Arrange: Request an empty JSON payload from data layer
        payload = BookingData.empty_payload()
        # Act: Create the booking via POST /booking
        response = booking_service.create_booking(payload)
        # Assert: Expect standard 400 Bad Request status code
        assert response.status_code == 400, (
            f"Expected 400 Bad Request, but got {response.status_code}"
        )

    @pytest.mark.xfail(
        reason=(
            "Audit defect: Restful-Booker returns 200 OK instead of "
            "201 Created when creating a new booking resource per RFC 9110"
        ),
        strict=True,
    )
    def test_create_booking_returns_201_created(
        self, booking_service: BookingService
    ) -> None:
        """Audit that POST /booking should return HTTP 201 Created per REST standards."""
        # Arrange: Generate dynamic booking payload
        payload = BookingData.valid_booking_payload()
        # Act: Create the booking via POST /booking
        response = booking_service.create_booking(payload)
        # Assert: Expect standard 201 Created status code
        assert response.status_code == 201, (
            f"Expected 201 Created, but got {response.status_code}"
        )


@pytest.mark.api
class TestGetBooking:
    """Test suite for the /booking/{id} retrieval endpoint."""

    @pytest.mark.smoke
    def test_get_existing_booking(
        self, booking_service: BookingService, created_booking: dict[str, Any]
    ) -> None:
        """Verify that an existing booking can be retrieved by its ID."""
        # Arrange: Extract booking ID and expected payload from precondition fixture
        booking_id = created_booking["bookingid"]
        expected_booking = created_booking["booking"]
        # Act: Retrieve the booking via GET /booking/{id}
        response = booking_service.get_booking(booking_id)
        # Assert: Verify HTTP 200 OK and exact match with persisted booking data
        assert response.status_code == 200, (
            f"Expected 200, but got {response.status_code}"
        )
        body = response.json()
        assert body == expected_booking, (
            f"Expected booking {expected_booking}, but got {body}"
        )

    @pytest.mark.parametrize(
        ("case_id", "booking_id"),
        BookingData.invalid_booking_ids(),
    )
    def test_get_booking_not_found(
        self,
        booking_service: BookingService,
        case_id: str,
        booking_id: Any,
    ) -> None:
        """Verify that non-existent or invalid booking IDs return HTTP 404 Not Found."""
        # Arrange: Provided via parametrize (case_id and booking_id)
        # Act: Retrieve the booking via GET /booking/{id}
        response = booking_service.get_booking(booking_id)
        # Assert: Verify HTTP 404 Not Found status and plain text error per RFC 9110
        assert response.status_code == 404, (
            f"[{case_id}] Expected 404, but got {response.status_code}"
        )
        assert response.text == "Not Found", (
            f"[{case_id}] Expected 'Not Found' response body, but got {response.text}"
        )


@pytest.mark.api
class TestGetBookingIds:
    """Test suite for the /booking search and collection endpoint."""

    @pytest.mark.smoke
    def test_get_booking_ids_unfiltered(
        self, booking_service: BookingService, created_booking: dict[str, Any]
    ) -> None:
        """Verify that an unfiltered search returns a list containing the created booking ID."""
        # Arrange: Build the expected booking ID entry from the precondition fixture
        booking_id = created_booking["bookingid"]
        expected_item = {"bookingid": booking_id}
        # Act: Retrieve the full collection of booking IDs without query filters
        response = booking_service.get_booking_ids()
        # Assert: Verify HTTP 200 OK, list structure, and presence of the created booking ID
        assert response.status_code == 200, (
            f"Expected 200, but got {response.status_code}"
        )
        body = response.json()
        assert isinstance(body, list), f"Expected list response, but got {type(body)}"
        assert expected_item in body, f"Expected {expected_item} in booking ID list"

    @pytest.mark.parametrize(
        ("case_id", "field"),
        BookingData.valid_name_filter_keys(),
    )
    def test_get_booking_ids_by_valid_name(
        self,
        booking_service: BookingService,
        created_booking: dict[str, Any],
        case_id: str,
        field: str,
    ) -> None:
        """Verify that filtering by a valid guest name returns the created booking ID."""
        # Arrange: Extract single-field filter and expected ID from precondition fixture
        params = {field: created_booking["booking"][field]}
        booking_id = created_booking["bookingid"]
        expected_item = {"bookingid": booking_id}
        # Act: Search booking IDs using the single name query parameter
        response = booking_service.get_booking_ids(params=params)
        # Assert: Verify HTTP 200 OK and presence of the created booking ID in results
        assert response.status_code == 200, (
            f"[{case_id}] Expected 200, but got {response.status_code}"
        )
        body = response.json()
        assert expected_item in body, (
            f"[{case_id}] Expected {expected_item} in filtered results for {params}"
        )
