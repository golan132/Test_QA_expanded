import pytest
import os
import json
from src.testing.consistency_analyzer import ConsistencyAnalyzer

def test_analyze_history(tmp_path):
    # Create mock JSON files
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    
    dir1 = data_dir / "test1"
    dir1.mkdir()
    file1 = dir1 / "data.json"
    file1.write_text(json.dumps({"ammeter_type": "greenlee", "statistics": {"mean": 5.0}}))
    
    dir2 = data_dir / "test2"
    dir2.mkdir()
    file2 = dir2 / "data.json"
    file2.write_text(json.dumps({"ammeter_type": "greenlee", "statistics": {"mean": 7.0}}))
    
    dir3 = data_dir / "test3"
    dir3.mkdir()
    file3 = dir3 / "data.json"
    file3.write_text(json.dumps({"ammeter_type": "entes", "statistics": {"mean": 10.0}}))
    
    # Missing mean
    dir4 = data_dir / "test4"
    dir4.mkdir()
    file4 = dir4 / "data.json"
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

def test_get_most_reliable_ammeter():
    report = {
        "greenlee": {"std_dev_of_means": 0.08},
        "entes": {"std_dev_of_means": 15.0},
        "circutor": {"std_dev_of_means": 0.01}
    }
    best = ConsistencyAnalyzer.get_most_reliable_ammeter(report)
    assert "CIRCUTOR" in best
    
    empty = ConsistencyAnalyzer.get_most_reliable_ammeter({})
    assert "No historical data" in empty
