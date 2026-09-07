import threading
import time
import yaml
import os

from Ammeters.Circutor_Ammeter import CircutorAmmeter
from Ammeters.Entes_Ammeter import EntesAmmeter
from Ammeters.Greenlee_Ammeter import GreenleeAmmeter
from Ammeters.client import request_current_from_ammeter


def get_ammeter_ports():
    ports = {"greenlee": 5000, "entes": 5001, "circutor": 5002}
    try:
        if os.path.exists("config/config.yaml"):
            with open("config/config.yaml", "r", encoding="utf-8") as f:
                ammeters = (yaml.safe_load(f) or {}).get("ammeters") or {}
                for key, val in ammeters.items():
                    if isinstance(val, dict) and val.get("port"):
                        ports[key] = val["port"]
    except Exception as e:
        print(f"Failed to load ports from config, using defaults: {e}")
    return ports


def run_greenlee_emulator(port):
    greenlee = GreenleeAmmeter(port)
    greenlee.start_server()

def run_entes_emulator(port):
    entes = EntesAmmeter(port)
    entes.start_server()

def run_circutor_emulator(port):
    circutor = CircutorAmmeter(port)
    circutor.start_server()

if __name__ == "__main__":
    ports = get_ammeter_ports()
    
    # Start each ammeter in a separate thread
    threading.Thread(target=run_greenlee_emulator, args=(ports["greenlee"],), daemon=True).start()
    threading.Thread(target=run_entes_emulator, args=(ports["entes"],), daemon=True).start()
    threading.Thread(target=run_circutor_emulator, args=(ports["circutor"],), daemon=True).start()

    # Wait for the servers to start
    time.sleep(5)
    
    # Request from Greenlee Ammeter
    request_current_from_ammeter(ports["greenlee"], b'MEASURE_GREENLEE -get_measurement')
    
    # Request from ENTES Ammeter
    request_current_from_ammeter(ports["entes"], b'MEASURE_ENTES -get_data')
    
    # Request from CIRCUTOR Ammeter
    request_current_from_ammeter(ports["circutor"], b'MEASURE_CIRCUTOR -get_measurement')
