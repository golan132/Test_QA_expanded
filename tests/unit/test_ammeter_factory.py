import pytest
from src.testing.ammeter_factory import AmmeterFactory
from src.testing.types import Configuration


def test_missing_port():
    config = Configuration(
        sampling_frequency_hz=1,
        timeout_seconds=2,
        measurements_count=1,
        ammeters_config={"bad": {"command": "MEASURE"}},  # Missing port
    )
    with pytest.raises(ValueError, match="Missing port or command"):
        AmmeterFactory.get_client("bad", config)
