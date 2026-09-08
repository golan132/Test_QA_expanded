import os
import tempfile
from src.testing.consistency_analyzer import ConsistencyAnalyzer


def test_analyze_history_no_dir():
    assert ConsistencyAnalyzer.analyze_history("non_existent_dir_123") == {}


def test_analyze_history_json_error():
    with tempfile.TemporaryDirectory() as tmp:
        run_dir = os.path.join(tmp, "run1")
        os.makedirs(run_dir)
        with open(os.path.join(run_dir, "data.json"), "w") as f:
            f.write("INVALID JSON")

        assert ConsistencyAnalyzer.analyze_history(tmp) == {}


def test_get_most_reliable_ammeter_insufficient_data():
    report = {
        "ammeter1": {
            "historical_runs": 1,
            "mean_of_means": 5.0,
            "std_dev_of_means": None,  # None std_dev
        }
    }
    verdict = ConsistencyAnalyzer.get_most_reliable_ammeter(report)
    assert verdict == "Insufficient data to determine reliability."
