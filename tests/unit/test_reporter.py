import pytest
from src.testing.reporter import ConsoleReporter
from src.testing.types import TestRunResult, Configuration
from src.testing.constants import MODE_COUNT

def create_mock_result(expected: int, successful: int, failed: int, error_rate: float = 0.1) -> TestRunResult:
    config = Configuration(mode=MODE_COUNT, sampling_frequency_hz=1.0, timeout_seconds=1.0, measurements_count=expected, acceptable_error_rate=error_rate)
    return TestRunResult(
        test_id="123", timestamp="2026", ammeter_type="greenlee", status="PENDING",
        configuration=config, expected_samples=expected, attempted_samples=successful+failed,
        successful_samples=successful, failed_samples=failed,
        measurements=[], statistics={}, errors=[]
    )

def test_calculate_status_pass():
    res = create_mock_result(10, 10, 0)
    assert ConsoleReporter.calculate_status(res) == "PASS"
    
def test_calculate_status_fail():
    res = create_mock_result(10, 5, 5, 0.1) # 50% failure rate > 10%
    assert ConsoleReporter.calculate_status(res) == "FAIL"

def test_calculate_status_error_no_data():
    res = create_mock_result(10, 0, 10, 0.5) # 100% failure rate, 0 successes
    assert ConsoleReporter.calculate_status(res) == "ERROR"

def test_calculate_status_error_zero_expected():
    res = create_mock_result(0, 0, 0)
    assert ConsoleReporter.calculate_status(res) == "ERROR"
