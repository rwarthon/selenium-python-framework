"""API Client wrapper module for handling HTTP requests."""

from typing import Any

import requests
from requests import Response

from config.config import Config


class APIClient:
    """Generic wrapper around requests.Session to centralize HTTP calls."""

    def __init__(
        self, base_url: str, default_headers: dict[str, str] | None = None
    ) -> None:
        """Initialize the API client with a persistent session and target base URL."""
        self.base_url = base_url
        self.timeout = Config.API_TIMEOUT
        # Use a persistent Session to reuse TCP connections (Keep-Alive) and retain cookies/headers
        self.session = requests.Session()
        # Apply initial headers only if explicitly provided to keep the client API-agnostic
        if default_headers:
            self.session.headers.update(default_headers)

    def get(
        self, endpoint: str, params: dict[str, Any] | None = None, **kwargs: Any
    ) -> Response:
        """Send a GET request to the specified endpoint."""
        # Concatenate base URL and target endpoint dynamically
        url = f"{self.base_url}{endpoint}"
        return self.session.get(url, params=params, timeout=self.timeout, **kwargs)

    def post(
        self, endpoint: str, payload: dict[str, Any] | None = None, **kwargs: Any
    ) -> Response:
        """Send a POST request with a JSON payload."""
        url = f"{self.base_url}{endpoint}"
        # Pass payload via 'json' parameter to auto-serialize dict and set Content-Type header
        return self.session.post(url, json=payload, timeout=self.timeout, **kwargs)

    def put(
        self, endpoint: str, payload: dict[str, Any] | None = None, **kwargs: Any
    ) -> Response:
        """Send a PUT request with a JSON payload."""
        url = f"{self.base_url}{endpoint}"
        return self.session.put(url, json=payload, timeout=self.timeout, **kwargs)

    def patch(
        self, endpoint: str, payload: dict[str, Any] | None = None, **kwargs: Any
    ) -> Response:
        """Send a PATCH request with a JSON payload."""
        url = f"{self.base_url}{endpoint}"
        return self.session.patch(url, json=payload, timeout=self.timeout, **kwargs)

    def delete(self, endpoint: str, **kwargs: Any) -> Response:
        """Send a DELETE request to the specified endpoint."""
        url = f"{self.base_url}{endpoint}"
        return self.session.delete(url, timeout=self.timeout, **kwargs)

    def set_headers(self, headers: dict[str, str]) -> None:
        """Update session headers dynamically (e.g., for Authorization tokens or Cookies)."""
        # Merge new headers into the active session for subsequent requests
        self.session.headers.update(headers)
