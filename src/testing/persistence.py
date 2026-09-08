import json
import os
import csv
import dataclasses
import matplotlib
import matplotlib.pyplot as plt
from src.testing.types import TestRunResult

# Use Agg backend so matplotlib doesn't try to open windows
matplotlib.use('Agg')


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

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(dataclasses.asdict(result), f, indent=2)

        return target_dir

    @staticmethod
    def export_csv(run_data: dict, target_dir: str):
        csv_filename = os.path.join(target_dir, "data.csv")
        with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            
            writer.writerow(["=== Ammeter Test Run Metadata ==="])
            writer.writerow(["Test ID", "Timestamp", "Ammeter Type", "Status", "Expected Samples", "Successful Samples", "Failed Samples"])
            writer.writerow([
                run_data.get("test_id", ""),
                run_data.get("timestamp", ""),
                run_data.get("ammeter_type", "").upper(),
                run_data.get("status", ""),
                run_data.get("expected_samples", 0),
                run_data.get("successful_samples", 0),
                run_data.get("failed_samples", 0)
            ])
            writer.writerow([])
            
            stats = run_data.get("statistics", {})
            if stats:
                writer.writerow(["=== Statistics ==="])
                stat_keys = list(stats.keys())
                writer.writerow([k.replace("_", " ").title() for k in stat_keys])
                writer.writerow([stats[k] for k in stat_keys])
                writer.writerow([])
            
            writer.writerow(["=== Raw Measurements ==="])
            writer.writerow(["Sample Index", "Timestamp", "Success", "Current (A)", "Error Type", "Error Message"])
            for idx, m in enumerate(run_data.get("measurements", []), start=1):
                writer.writerow([
                    idx,
                    m.get("timestamp", ""),
                    "PASS" if m.get("success") else "FAIL",
                    m.get("value") if m.get("value") is not None else "N/A",
                    m.get("error_type") if m.get("error_type") else "-",
                    m.get("error_message") if m.get("error_message") else "-"
                ])
        return csv_filename

    @staticmethod
    def export_graphs(run_data: dict, target_dir: str):
        valid_measurements = [
            m.get("value") for m in run_data.get("measurements", [])
            if m.get("success") and m.get("value") is not None
        ]
        
        if not valid_measurements:
            return None, None

        ammeter_type = run_data.get("ammeter_type", "Unknown")
        plt.figure(figsize=(10, 5))
        plt.plot(valid_measurements, marker='o', linestyle='-', color='b')
        plt.title(f"Time Series: {ammeter_type.capitalize()} Current (A)")
        plt.xlabel("Sample Index (Valid)")
        plt.ylabel("Current (A)")
        plt.grid(True)
        plt.tight_layout()
        ts_path = os.path.join(target_dir, "time_series.png")
        plt.savefig(ts_path)
        plt.close()

        plt.figure(figsize=(8, 5))
        plt.hist(valid_measurements, bins='auto', color='g', alpha=0.7, rwidth=0.85)
        plt.title(f"Histogram: {ammeter_type.capitalize()} Current (A)")
        plt.xlabel("Current (A)")
        plt.ylabel("Frequency")
        plt.grid(axis='y', alpha=0.75)
        plt.tight_layout()
        hist_path = os.path.join(target_dir, "histogram.png")
        plt.savefig(hist_path)
        plt.close()
        
        return ts_path, hist_path

    @staticmethod
    def get_all_runs(results_dir: str = "results/runs") -> list:
        runs = []
        if not os.path.exists(results_dir):
            return runs

        for root, _, files in os.walk(results_dir):
            if "data.json" in files:
                try:
                    with open(
                        os.path.join(root, "data.json"), "r", encoding="utf-8"
                    ) as f:
                        data = json.load(f)
                        runs.append(
                            {
                                "timestamp": data.get("timestamp"),
                                "test_id": data.get("test_id"),
                                "ammeter_type": data.get(
                                    "ammeter_type", "unknown"
                                ).upper(),
                                "status": data.get("status", "UNKNOWN"),
                                "pass_rate": f"{(data.get('successful_samples', 0) / max(data.get('expected_samples', 1), 1) * 100):.1f}%",
                            }
                        )
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
                    with open(
                        os.path.join(root, "data.json"), "r", encoding="utf-8"
                    ) as f:
                        data = json.load(f)
                        if data.get("test_id") == test_id:
                            data["_source_dir"] = root
                            return data
                except Exception:
                    pass
        return None
