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

    @staticmethod
    def get_all_runs(results_dir: str = "results/runs") -> list:
        runs = []
        if not os.path.exists(results_dir):
            return runs
            
        for root, _, files in os.walk(results_dir):
            if "data.json" in files:
                try:
                    with open(os.path.join(root, "data.json"), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        runs.append({
                            "timestamp": data.get("timestamp"),
                            "test_id": data.get("test_id"),
                            "ammeter_type": data.get("ammeter_type", "unknown").upper(),
                            "status": data.get("status", "UNKNOWN"),
                            "pass_rate": f"{(data.get('successful_samples', 0) / max(data.get('expected_samples', 1), 1) * 100):.1f}%"
                        })
                except Exception:
                    pass
        # Sort by timestamp descending
        runs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return runs

    @staticmethod
    def get_run_by_id(test_id: str, results_dir: str = "results/runs") -> dict:
        if not os.path.exists(results_dir):
            return None
            
        for root, _, files in os.walk(results_dir):
            if "data.json" in files:
                try:
                    with open(os.path.join(root, "data.json"), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if data.get("test_id") == test_id:
                            return data
                except Exception:
                    pass
        return None
