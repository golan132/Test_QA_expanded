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
    
    saved_file = PersistenceLayer.save_result(result, base_dir=str(tmp_path))
    assert os.path.exists(saved_file)
    
    with open(saved_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        assert data["test_id"] == "test-1234"
        assert data["status"] == "PASS"
        assert data["configuration"]["mode"] == MODE_COUNT
