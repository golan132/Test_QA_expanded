import pytest
import json
import os
from src.testing.persistence import PersistenceLayer
from src.testing.types import TestRunResult, Configuration
from src.testing.constants import MODE_COUNT

def test_persistence_saves_json(tmp_path):
    config = Configuration(mode=MODE_COUNT, sampling_frequency_hz=1.0, timeout_seconds=1.0, measurements_count=10)
    result = TestRunResult(
        test_id="test-1234",
        timestamp="2026-09-07T12:00:00Z",
        ammeter_type="greenlee",
        status="PASS",
        configuration=config,
        expected_samples=10,
        attempted_samples=10,
        successful_samples=10,
        failed_samples=0,
        measurements=[],
        statistics={},
        errors=[]
    )
    
    session_dir = str(tmp_path / "session_test")
    saved_dir = PersistenceLayer.save_result(result, session_dir=session_dir)
    assert os.path.exists(saved_dir)
    assert os.path.isdir(saved_dir)
    # Verify ammeter subfolder was created inside session dir
    assert saved_dir == os.path.join(session_dir, "greenlee")
    
    saved_file = os.path.join(saved_dir, "data.json")
    with open(saved_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        assert data["test_id"] == "test-1234"
        assert data["status"] == "PASS"
        assert data["configuration"]["mode"] == MODE_COUNT

def test_persistence_get_history(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    
    dir1 = data_dir / "test1"
    dir1.mkdir()
    file1 = dir1 / "data.json"
    file1.write_text(json.dumps({"test_id": "abc", "ammeter_type": "greenlee", "timestamp": "2026-09-07T12:00:00Z"}))
    
    runs = PersistenceLayer.get_all_runs(str(data_dir))
    assert len(runs) == 1
    assert runs[0]["test_id"] == "abc"
    assert runs[0]["ammeter_type"] == "GREENLEE"
    
    run_data = PersistenceLayer.get_run_by_id("abc", str(data_dir))
    assert run_data["test_id"] == "abc"
    assert run_data["ammeter_type"] == "greenlee"
    
    assert PersistenceLayer.get_run_by_id("nonexistent", str(data_dir)) is None
