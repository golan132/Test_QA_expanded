import yaml
from src.testing.types import Configuration
from src.testing.constants import (
    MODE_COUNT, MODE_DURATION, DEFAULT_TIMEOUT_SECONDS, 
    DEFAULT_ACCEPTABLE_ERROR_RATE, DEFAULT_SAMPLING_FREQUENCY_HZ,
    DEFAULT_MEASUREMENTS_COUNT
)

def load_config(config_path: str) -> Configuration:
    """
    Loads and strictly validates the testing configuration from a YAML file.
    Enforces that either count OR duration is provided, not both.
    Supports 'null' or missing values by falling back to robust defaults.
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}
    
    sampling = data.get("testing", {}).get("sampling", {})
    if sampling is None:
        sampling = {}
    
    freq = sampling.get("sampling_frequency_hz")
    if freq == "NULL" or freq is None:
        freq = DEFAULT_SAMPLING_FREQUENCY_HZ
    freq = float(freq)
    if freq <= 0:
        raise ValueError("sampling_frequency_hz must be > 0")

    count = sampling.get("measurements_count")
    if count == "NULL":
        count = None
    elif count is not None:
        count = int(count)
        
    duration = sampling.get("total_duration_seconds")
    if duration == "NULL":
        duration = None
    elif duration is not None:
        duration = float(duration)

    if count is not None and duration is not None:
        raise ValueError("Strict validation failed: Cannot define both measurements_count and total_duration_seconds. Choose one mode.")
    
    if count is not None:
        if count <= 0:
            raise ValueError("measurements_count must be > 0")
        mode = MODE_COUNT
    elif duration is not None:
        if duration <= 0:
            raise ValueError("total_duration_seconds must be > 0")
        mode = MODE_DURATION
    else:
        # Default fallback when both are null
        mode = MODE_COUNT
        count = DEFAULT_MEASUREMENTS_COUNT
        
    timeout = sampling.get("timeout_seconds")
    if timeout == "NULL" or timeout is None:
        timeout = DEFAULT_TIMEOUT_SECONDS
        
    error_rate = sampling.get("acceptable_error_rate")
    if error_rate == "NULL" or error_rate is None:
        error_rate = DEFAULT_ACCEPTABLE_ERROR_RATE

    return Configuration(
        mode=mode,
        sampling_frequency_hz=freq,
        timeout_seconds=float(timeout),
        measurements_count=count,
        duration_seconds=duration,
        acceptable_error_rate=float(error_rate)
    )
