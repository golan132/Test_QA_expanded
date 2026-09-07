import json
import os
import dataclasses
from src.testing.types import TestRunResult

class PersistenceLayer:
    @staticmethod
    def save_result(result: TestRunResult, base_dir: str = "results/data") -> str:
        os.makedirs(base_dir, exist_ok=True)
        filename = os.path.join(base_dir, f"run_{result.test_id}.json")
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(dataclasses.asdict(result), f, indent=2)
            
        return filename
