import threading
import time
from typing import Dict, Type

from Ammeters.base_ammeter import AmmeterEmulatorBase
from Ammeters.Greenlee_Ammeter import GreenleeAmmeter
from Ammeters.Entes_Ammeter import EntesAmmeter
from Ammeters.Circutor_Ammeter import CircutorAmmeter
from src.utils.config import load_config
from src.utils.logger import TestLogger


class EmulatorManager:
    """
    Manages the lifecycle and execution of the hardware emulators.
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = load_config(config_path)
        self.logger = TestLogger("emulator_manager")
        
        # Default ports if missing in config
        self.ports: Dict[str, int] = {
            "greenlee": self.config.ammeters_config.get("greenlee", {}).get("port", 5000),
            "entes": self.config.ammeters_config.get("entes", {}).get("port", 5001),
            "circutor": self.config.ammeters_config.get("circutor", {}).get("port", 5002)
        }

    def start_emulator(self, emulator_class: Type[AmmeterEmulatorBase], port: int) -> None:
        """Starts a specific emulator on the given port."""
        try:
            emulator_instance = emulator_class(port)
            emulator_instance.start_server()
        except OSError as e:
            self.logger.warning(f"Emulator on port {port} failed to start or is already running: {e}")

    def start_all_emulators_in_background(self) -> None:
        """Starts all defined emulators in background daemon threads."""
        self.logger.info("Starting hardware emulators in the background...")
        
        threading.Thread(
            target=self.start_emulator, 
            args=(GreenleeAmmeter, self.ports["greenlee"]), 
            daemon=True
        ).start()
        
        threading.Thread(
            target=self.start_emulator, 
            args=(EntesAmmeter, self.ports["entes"]), 
            daemon=True
        ).start()
        
        threading.Thread(
            target=self.start_emulator, 
            args=(CircutorAmmeter, self.ports["circutor"]), 
            daemon=True
        ).start()
        
        # Allow time for socket binding
        time.sleep(1)
