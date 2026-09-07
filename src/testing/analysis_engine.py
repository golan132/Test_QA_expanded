import statistics
from typing import List, Dict, Optional
from src.testing.types import MeasurementResult

class AnalysisEngine:
    @staticmethod
    def analyze(results: List[MeasurementResult]) -> Dict[str, Optional[float]]:
        # Filter only successful measurements
        valid_values = [r.value for r in results if r.success and r.value is not None]
        
        if not valid_values:
            return {
                "mean": None,
                "median": None,
                "std_dev": None,
                "min": None,
                "max": None
            }
            
        stats = {
            "mean": statistics.mean(valid_values),
            "median": statistics.median(valid_values),
            "min": min(valid_values),
            "max": max(valid_values)
        }
        
        if len(valid_values) > 1:
            stats["std_dev"] = statistics.stdev(valid_values)
        else:
            stats["std_dev"] = None
            
        return stats
