import json
import os
import dataclasses
from src.testing.types import TestRunResult

class PersistenceLayer:
    @staticmethod
    def save_result(result: TestRunResult, session_dir: str) -> str:
        """
        Saves a test result into the given session directory.
        Creates an ammeter-specific subfolder: session_dir/{ammeter_type}/
        """
        ammeter_name = result.ammeter_type.lower()
        target_dir = os.path.join(session_dir, ammeter_name)
        os.makedirs(target_dir, exist_ok=True)
        
        filename = os.path.join(target_dir, "data.json")
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(dataclasses.asdict(result), f, indent=2)
            
        return target_dir
