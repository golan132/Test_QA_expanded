import statistics
import math
from typing import List, Dict, Optional
from src.testing.types import MeasurementResult


class AnalysisEngine:
    @staticmethod
    def analyze(
        results: List[MeasurementResult], metrics: Optional[List[str]] = None
    ) -> Dict[str, Optional[float]]:
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

        if "variance" in metrics:
            if len(valid_values) > 1:
                stats["variance"] = statistics.variance(valid_values)
            else:
                stats["variance"] = None

        if "rms" in metrics:
            stats["rms"] = math.sqrt(sum(v**2 for v in valid_values) / len(valid_values))

        # CV and SNR require Mean and StdDev. If they weren't explicitly requested, compute them here.
        if "cv" in metrics or "snr" in metrics:
            mean_val = stats.get("mean")
            std_dev_val = stats.get("std_dev")
            if mean_val is None:
                mean_val = statistics.mean(valid_values)
            if std_dev_val is None and len(valid_values) > 1:
                std_dev_val = statistics.stdev(valid_values)

            if "cv" in metrics:
                if mean_val is not None and std_dev_val is not None and mean_val != 0:
                    stats["cv"] = std_dev_val / mean_val
                else:
                    stats["cv"] = None

            if "snr" in metrics:
                if mean_val is not None and std_dev_val:
                    stats["snr"] = mean_val / std_dev_val
                elif mean_val is not None and not std_dev_val:
                    stats["snr"] = float('inf') # Zero noise
                else:
                    stats["snr"] = None

        return stats
