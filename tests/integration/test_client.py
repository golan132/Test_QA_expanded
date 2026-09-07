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

def test_greenlee_client():
    client = AmmeterFactory.get_client("greenlee")
    result = client.measure()
    assert result.success is True
    assert isinstance(result.value, float)

def test_entes_client():
    client = AmmeterFactory.get_client("entes")
    result = client.measure()
    assert result.success is True
    assert isinstance(result.value, float)

def test_circutor_client():
    client = AmmeterFactory.get_client("circutor")
    result = client.measure()
    assert result.success is True
    assert isinstance(result.value, float)

def test_invalid_ammeter():
    with pytest.raises(ValueError):
        AmmeterFactory.get_client("invalid_type")
