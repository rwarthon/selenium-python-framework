"""Configuration module for the automation framework."""
import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def _get_required_env(key: str) -> str:
    """Retrieve a required string environment variable or raise an error if missing."""
    value = os.getenv(key)
    if not value:
        raise ValueError(f"Missing required environment variable: '{key}' in .env file.")
    return value

def _get_int_env(key: str) -> int:
    """Retrieve and validate an integer environment variable."""
    raw_value = _get_required_env(key)
    try:
        return int(raw_value)
    except ValueError as e:
        raise ValueError(
            f"Invalid integer value for '{key}' in .env file. Got: '{raw_value}'."
        ) from e

class Config:
    """Centralized framework configuration loaded from environment variables."""
    BOOKING_API_URL: str = _get_required_env("BOOKING_API_URL")
    BOOKING_USERNAME: str = _get_required_env("BOOKING_USERNAME")
    BOOKING_PASSWORD: str = _get_required_env("BOOKING_PASSWORD")
    API_TIMEOUT: int = _get_int_env("API_TIMEOUT")
