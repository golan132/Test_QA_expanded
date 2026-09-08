import pytest
import os
from src.testing.test_framework import AmmeterTestFramework
from src.testing.analysis_engine import AnalysisEngine
from src.testing.types import MeasurementResult

def test_framework_initialization():
    framework = AmmeterTestFramework()
    assert framework.config is not None
    assert framework.config.measurements_count is not None or framework.config.duration_seconds is not None

def test_analysis_engine_stats():
    # Test advanced statistical calculations
    samples = [
        MeasurementResult.create_success("2026-01-01T00:00:00", 1.0),
        MeasurementResult.create_success("2026-01-01T00:00:01", 3.0),
        MeasurementResult.create_success("2026-01-01T00:00:02", 5.0)
    ]
    metrics = ["mean", "median", "variance", "std_dev"]
    stats = AnalysisEngine.analyze(samples, metrics)
    
    assert stats["mean"] == 3.0
    assert stats["median"] == 3.0
    assert stats["variance"] == 4.0
    assert stats["std_dev"] == 2.0
