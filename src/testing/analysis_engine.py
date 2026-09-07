import statistics
from typing import List, Dict, Optional
from src.testing.types import MeasurementResult

class AnalysisEngine:
    @staticmethod
    def analyze(results: List[MeasurementResult], metrics: Optional[List[str]] = None) -> Dict[str, Optional[float]]:
        if metrics is None:
            metrics = ["mean", "median", "std_dev", "min", "max"]
            
        # Filter only successful measurements
        valid_values = [r.value for r in results if r.success and r.value is not None]
        
        stats = {m: None for m in metrics}
        
        if not valid_values:
            return stats
            
        if "mean" in metrics:
            stats["mean"] = statistics.mean(valid_values)
        if "median" in metrics:
            stats["median"] = statistics.median(valid_values)
        if "min" in metrics:
            stats["min"] = min(valid_values)
        if "max" in metrics:
            stats["max"] = max(valid_values)
            
        if "std_dev" in metrics:
            if len(valid_values) > 1:
                stats["std_dev"] = statistics.stdev(valid_values)
            else:
                stats["std_dev"] = None
                
        return stats
