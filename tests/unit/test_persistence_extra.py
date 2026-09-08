import os
import json
import tempfile
from src.testing.persistence import PersistenceLayer


def test_get_all_runs_no_dir():
    assert PersistenceLayer.get_all_runs("non_existent_123") == []


def test_get_run_by_id_no_dir():
    assert PersistenceLayer.get_run_by_id("123", "non_existent_123") is None


def test_persistence_corrupt_files():
    with tempfile.TemporaryDirectory() as tmp:
        d = os.path.join(tmp, "run1")
        os.makedirs(d)
        with open(os.path.join(d, "data.json"), "w") as f:
            f.write("INVALID")

        assert PersistenceLayer.get_all_runs(tmp) == []
        assert PersistenceLayer.get_run_by_id("123", tmp) is None


def test_persistence_missing_fields():
    with tempfile.TemporaryDirectory() as tmp:
        d = os.path.join(tmp, "run1")
        os.makedirs(d)
        with open(os.path.join(d, "data.json"), "w") as f:
            # missing ammeter_type and status
            json.dump(
                {"test_id": "123", "timestamp": "2026", "successful_samples": 5}, f
            )

        runs = PersistenceLayer.get_all_runs(tmp)
        assert len(runs) == 1
        assert runs[0]["ammeter_type"] == "UNKNOWN"
        assert runs[0]["status"] == "UNKNOWN"
