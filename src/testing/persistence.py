import json
import os
import dataclasses
from datetime import datetime
from src.testing.types import TestRunResult

class PersistenceLayer:
    @staticmethod
    def save_result(result: TestRunResult, base_dir: str = "results/runs") -> str:
        # Parse timestamp to get YYYY-MM-DD
        dt = datetime.strptime(result.timestamp, "%Y-%m-%dT%H:%M:%SZ")
        date_str = dt.strftime("%Y-%m-%d")
        
        # Structure: results/runs/YYYY-MM-DD/{ammeter}_{short_id}/
        short_id = result.test_id[:8]
        ammeter_name = result.ammeter_type.lower()
        run_folder_name = f"{ammeter_name}_{short_id}"
        
        target_dir = os.path.join(base_dir, date_str, run_folder_name)
        os.makedirs(target_dir, exist_ok=True)
        
        filename = os.path.join(target_dir, "data.json")
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(dataclasses.asdict(result), f, indent=2)
            
        return target_dir
