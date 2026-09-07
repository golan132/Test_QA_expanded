import pytest
from src.testing.analysis_engine import AnalysisEngine
from src.testing.types import MeasurementResult

def create_result(value: float, success: bool = True) -> MeasurementResult:
    return MeasurementResult(timestamp="2026-09-07T12:00:00Z", value=value, success=success)

def test_analyze_zero_values():
    results = [create_result(0, success=False)]
    stats = AnalysisEngine.analyze(results)
    assert stats["mean"] is None
    assert stats["std_dev"] is None
    assert stats["min"] is None
    assert stats["max"] is None

def test_analyze_one_value():
    results = [create_result(5.0)]
    stats = AnalysisEngine.analyze(results)
    assert stats["mean"] == 5.0
    assert stats["std_dev"] is None
    assert stats["min"] == 5.0
    assert stats["max"] == 5.0

def test_analyze_multiple_values():
    results = [create_result(2.0), create_result(4.0), create_result(4.0), create_result(4.5)]
    stats = AnalysisEngine.analyze(results)
    assert stats["mean"] == 3.625
    assert stats["min"] == 2.0
    assert stats["max"] == 4.5
    assert stats["std_dev"] is not None
    assert round(stats["std_dev"], 2) == 1.11

def test_ignores_failed_measurements():
    results = [create_result(2.0), create_result(100.0, success=False), create_result(4.0)]
    stats = AnalysisEngine.analyze(results)
    assert stats["mean"] == 3.0
    assert stats["min"] == 2.0
    assert stats["max"] == 4.0
    assert stats["std_dev"] is not None

def test_analyze_selective_metrics():
    results = [create_result(2.0), create_result(4.0), create_result(6.0)]
    stats = AnalysisEngine.analyze(results, metrics=["mean", "max"])
    assert "mean" in stats
    assert "max" in stats
    assert "std_dev" not in stats
    assert "min" not in stats
    assert stats["mean"] == 4.0
    assert stats["max"] == 6.0

def test_analyze_single_metric():
    results = [create_result(10.0), create_result(20.0)]
    stats = AnalysisEngine.analyze(results, metrics=["median"])
    assert "median" in stats
    assert stats["median"] == 15.0
    assert "mean" not in stats

