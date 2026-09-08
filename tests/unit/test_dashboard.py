from unittest.mock import patch, MagicMock
from src.testing.dashboard_generator import DashboardGenerator
from src.testing.types import TestRunResult


@patch("src.testing.dashboard_generator.DashboardGenerator.generate_global_dashboard")
def test_dashboard_generator_handles_ioerror(mock_generate):
    # Mock to raise an OSError
    mock_generate.side_effect = OSError("Simulated error")

    # Create a dummy result
    dummy_result = MagicMock(spec=TestRunResult)
    dummy_result.test_id = "123"
    dummy_result.measurements = []

    # Run the generator
    # It should catch the exception internally and return an empty string, rather than crashing
    result_path = DashboardGenerator.generate_dashboard(dummy_result, "dummy/path")

    assert result_path == ""


@patch("src.testing.dashboard_generator.open")
def test_global_dashboard_handles_ioerror(mock_open):
    mock_open.side_effect = OSError("Simulated permission denied")

    # Should not crash
    try:
        DashboardGenerator.generate_global_dashboard()
        crashed = False
    except Exception:
        crashed = True

    assert not crashed
