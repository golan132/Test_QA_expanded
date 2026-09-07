import threading
import time
import argparse
import sys
import os
import yaml

from Ammeters.Circutor_Ammeter import CircutorAmmeter
from Ammeters.Entes_Ammeter import EntesAmmeter
from Ammeters.Greenlee_Ammeter import GreenleeAmmeter
from src.testing.test_framework import AmmeterTestFramework


def get_ammeter_ports():
    ports = {"greenlee": 5000, "entes": 5001, "circutor": 5002}
    try:
        if os.path.exists("config/config.yaml"):
            with open("config/config.yaml", "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                ammeters = data.get("ammeters", {})
                for name in ports:
                    ports[name] = ammeters.get(name, {}).get("port", ports[name])
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
    parser = argparse.ArgumentParser(description="Ammeter Emulator & Testing Framework")
    parser.add_argument("--ammeter", type=str, choices=["greenlee", "entes", "circutor", "all"], 
                        help="Run test framework against specified ammeter")
    args = parser.parse_args()

    ports = get_ammeter_ports()
    
    # Start each ammeter in a separate thread
    threading.Thread(target=run_greenlee_emulator, args=(ports["greenlee"],), daemon=True).start()
    threading.Thread(target=run_entes_emulator, args=(ports["entes"],), daemon=True).start()
    threading.Thread(target=run_circutor_emulator, args=(ports["circutor"],), daemon=True).start()

    # Wait for the servers to start
    time.sleep(1)
    
    if args.ammeter:
        framework = AmmeterTestFramework()
        ammeters_to_test = ["greenlee", "entes", "circutor"] if args.ammeter == "all" else [args.ammeter]
        
        for ammeter in ammeters_to_test:
            print(f"\nStarting test for {ammeter}...")
            framework.run_test(ammeter)
            time.sleep(1)
    else:
        print("\nEmulators are running. Use --ammeter to run tests.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Exiting...")

