import pytest
import os
import json
from src.testing.consistency_analyzer import ConsistencyAnalyzer

def test_analyze_history(tmp_path):
    # Create mock JSON files
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    
    file1 = data_dir / "run_1.json"
    file1.write_text(json.dumps({"ammeter_type": "greenlee", "statistics": {"mean": 5.0}}))
    
    file2 = data_dir / "run_2.json"
    file2.write_text(json.dumps({"ammeter_type": "greenlee", "statistics": {"mean": 7.0}}))
    
    file3 = data_dir / "run_3.json"
    file3.write_text(json.dumps({"ammeter_type": "entes", "statistics": {"mean": 10.0}}))
    
    # Missing mean
    file4 = data_dir / "run_4.json"
    file4.write_text(json.dumps({"ammeter_type": "entes", "statistics": {}}))
    
    report = ConsistencyAnalyzer.analyze_history(str(data_dir))
    
    assert "greenlee" in report
    assert report["greenlee"]["historical_runs"] == 2
    assert report["greenlee"]["mean_of_means"] == 6.0
    assert report["greenlee"]["std_dev_of_means"] > 0
    
    assert "entes" in report
    assert report["entes"]["historical_runs"] == 1
    assert report["entes"]["mean_of_means"] == 10.0
    assert report["entes"]["std_dev_of_means"] == 0.0
