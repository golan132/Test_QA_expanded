import pytest
from unittest.mock import patch, MagicMock
from src.testing.test_framework import AmmeterTestFramework
from src.testing.types import MeasurementResult

@pytest.fixture
def mock_config(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text("""
testing:
  sampling:
    mode: "count"
    measurements_count: 3
    sampling_frequency_hz: 10
    timeout_seconds: 1.0
    acceptable_error_rate: 0.1

ammeters:
  greenlee:
    port: 5000
    command: "MOCK_CMD"
  circutor:
    port: 5002
    command: "MOCK_CMD"
""")
    return str(config_file)

@patch("src.testing.test_framework.AmmeterFactory.get_client")
def test_framework_runs_deterministically(mock_get_client, mock_config):
    # Setup mock client
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    
    # Return deterministic results
    mock_client.measure.side_effect = [
        MeasurementResult("t1", 5.0, True),
        MeasurementResult("t2", 6.0, True),
        MeasurementResult("t3", None, False, "TimeoutError", "Socket timeout")
    ]
    
    framework = AmmeterTestFramework(config_path=mock_config)
    result = framework.run_test("greenlee")
    
    assert result.attempted_samples == 3
    assert result.successful_samples == 2
    assert result.failed_samples == 1
    
    # Error rate is 1/3 (33%) > 10% acceptable, so it should FAIL
    assert result.status == "FAIL"
    
    # Check stats
    assert result.statistics["mean"] == 5.5
    assert result.statistics["min"] == 5.0
    assert result.statistics["max"] == 6.0
    
    assert len(result.errors) == 1
    assert result.errors[0]["error_type"] == "TimeoutError"

@patch("src.testing.test_framework.AmmeterFactory.get_client")
def test_framework_catches_fatal_error(mock_get_client, mock_config):
    # Setup mock client to throw an unhandled exception
    mock_get_client.side_effect = Exception("Simulated fatal factory failure")
    
    framework = AmmeterTestFramework(config_path=mock_config)
    result = framework.run_test("circutor")
    
    # Assert that instead of crashing, it gracefully returns an ERROR result
    assert result.status == "ERROR"
    assert result.expected_samples == 0
    assert len(result.errors) == 1
    assert result.errors[0]["error_type"] == "FatalFrameworkError"
    assert "Simulated fatal factory failure" in result.errors[0]["error_message"]
