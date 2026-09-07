import pytest
import threading
import time
from src.testing.ammeter_factory import AmmeterFactory
from Ammeters.Greenlee_Ammeter import GreenleeAmmeter
from Ammeters.Entes_Ammeter import EntesAmmeter
from Ammeters.Circutor_Ammeter import CircutorAmmeter

@pytest.fixture(scope="module", autouse=True)
def start_emulators():
    # Start emulators on default ports
    threading.Thread(target=lambda: GreenleeAmmeter(5000).start_server(), daemon=True).start()
    threading.Thread(target=lambda: EntesAmmeter(5001).start_server(), daemon=True).start()
    threading.Thread(target=lambda: CircutorAmmeter(5002).start_server(), daemon=True).start()
    time.sleep(1) # wait for servers to start
    yield

from src.testing.types import Configuration

# Dummy config for integration tests
dummy_config = Configuration(
    mode="count",
    sampling_frequency_hz=1.0,
    timeout_seconds=2.0,
    measurements_count=1,
    ammeters_config={
        "greenlee": {"port": 5000, "command": "MEASURE_GREENLEE -get_measurement"},
        "entes": {"port": 5001, "command": "MEASURE_ENTES -get_data"},
        "circutor": {"port": 5002, "command": "MEASURE_CIRCUTOR -get_measurement"}
    }
)

def test_greenlee_client():
    client = AmmeterFactory.get_client("greenlee", dummy_config)
    result = client.measure()
    assert result.success is True
    assert isinstance(result.value, float)

def test_entes_client():
    client = AmmeterFactory.get_client("entes", dummy_config)
    result = client.measure()
    assert result.success is True
    assert isinstance(result.value, float)

def test_circutor_client():
    client = AmmeterFactory.get_client("circutor", dummy_config)
    result = client.measure()
    assert result.success is True
    assert isinstance(result.value, float)

def test_invalid_ammeter():
    with pytest.raises(ValueError):
        AmmeterFactory.get_client("invalid_type", dummy_config)
