"""Centralized API endpoint definitions for target applications."""


class BookingEndpoints:
    """Endpoint paths for the Restful-Booker API."""

    AUTH = "/auth"
    BOOKING = "/booking"
    PING = "/ping"

    @staticmethod
    def booking_detail(booking_id: int) -> str:
        """Return the endpoint path for a specific booking ID."""
        return f"{BookingEndpoints.BOOKING}/{booking_id}"
