"""Service layer encapsulating Restful-Booker domain operations (SOM)."""

from typing import Any, ClassVar

from requests import Response

from config.config import Config
from config.endpoints import BookingEndpoints
from core.api_client import APIClient


class BookingService:
    """Provide business-level methods to interact with the Booking API."""

    # Standard headers required by the Restful-Booker API contract
    DEFAULT_HEADERS: ClassVar[dict[str, str]] = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    def __init__(self) -> None:
        """Initialize the Booking service with its dedicated APIClient instance."""
        self.client = APIClient(
            base_url=Config.BOOKING_API_URL, default_headers=self.DEFAULT_HEADERS
        )

    def ping(self) -> Response:
        """Perform a health check on the API server."""
        return self.client.get(BookingEndpoints.PING)

    def authenticate(
        self,
        username: str = Config.BOOKING_USERNAME,
        password: str = Config.BOOKING_PASSWORD,
    ) -> Response:
        """Request an authentication token using user credentials."""
        payload = {"username": username, "password": password}
        return self.client.post(BookingEndpoints.AUTH, payload=payload)

    def get_all_bookings(self, params: dict[str, Any] | None = None) -> Response:
        """Retrieve a list of booking IDs, optionally filtered by query parameters."""
        return self.client.get(BookingEndpoints.BOOKING, params=params)

    def get_booking(self, booking_id: int) -> Response:
        """Retrieve details of a specific booking by its ID."""
        endpoint = BookingEndpoints.booking_detail(booking_id)
        return self.client.get(endpoint)

    def create_booking(self, payload: dict[str, Any]) -> Response:
        """Create a new booking record."""
        return self.client.post(BookingEndpoints.BOOKING, payload=payload)

    def update_booking(
        self, booking_id: int, payload: dict[str, Any], token: str
    ) -> Response:
        """Fully update an existing booking (PUT) using token authentication."""
        endpoint = BookingEndpoints.booking_detail(booking_id)
        # Inject auth token via Cookie header as required by Restful-Booker
        auth_headers = {"Cookie": f"token={token}"}
        return self.client.put(endpoint, payload=payload, headers=auth_headers)

    def partial_update_booking(
        self, booking_id: int, payload: dict[str, Any], token: str
    ) -> Response:
        """Partially update an existing booking (PATCH) using token authentication."""
        endpoint = BookingEndpoints.booking_detail(booking_id)
        auth_headers = {"Cookie": f"token={token}"}
        return self.client.patch(endpoint, payload=payload, headers=auth_headers)

    def delete_booking(self, booking_id: int, token: str) -> Response:
        """Delete an existing booking by its ID using token authentication."""
        endpoint = BookingEndpoints.booking_detail(booking_id)
        auth_headers = {"Cookie": f"token={token}"}
        return self.client.delete(endpoint, headers=auth_headers)

    def close(self) -> None:
        """Close the underlying HTTP session to release network resources."""
        self.client.session.close()
