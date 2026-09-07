import os
import json
import statistics
from typing import Dict

class ConsistencyAnalyzer:
    @staticmethod
    def analyze_history(results_dir: str = "results/runs") -> Dict[str, dict]:
        if not os.path.exists(results_dir):
            return {}
            
        history = {}
        for root, _, files in os.walk(results_dir):
            for filename in files:
                if filename == "data.json":
                    path = os.path.join(root, filename)
                    with open(path, 'r', encoding='utf-8') as f:
                        try:
                            data = json.load(f)
                        except json.JSONDecodeError:
                            continue
                        
                        ammeter = data.get("ammeter_type")
                        stats = data.get("statistics", {})
                        mean = stats.get("mean") if stats else None
                        
                        if ammeter and mean is not None:
                            if ammeter not in history:
                                history[ammeter] = []
                            history[ammeter].append(mean)
                    
        consistency_report = {}
        for ammeter, means in history.items():
            if len(means) > 1:
                consistency_report[ammeter] = {
                    "historical_runs": len(means),
                    "mean_of_means": statistics.mean(means),
                    "std_dev_of_means": statistics.stdev(means)
                }
            elif len(means) == 1:
                consistency_report[ammeter] = {
                    "historical_runs": 1,
                    "mean_of_means": means[0],
                    "std_dev_of_means": 0.0
                }
                
        return consistency_report
