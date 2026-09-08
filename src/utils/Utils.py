import random
from datetime import datetime, timezone


def generate_random_float(min_value: float, max_value: float) -> float:
    """Generate a random float between min_value and max_value."""
    return random.uniform(min_value, max_value)


def get_current_timestamp() -> str:
    """Return the current UTC timestamp in standard ISO 8601 format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_timestamp(timestamp: str) -> datetime:
    """Parse the standard ISO 8601 timestamp string into a datetime object."""
    return datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
