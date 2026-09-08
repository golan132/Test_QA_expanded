from src.testing.reporter import ConsoleReporter
from src.testing.types import TestRunResult, Configuration


def create_mock_result(
    expected: int, successful: int, failed: int, error_rate: float = 0.1
) -> TestRunResult:
    config = Configuration(
        sampling_frequency_hz=1.0,
        timeout_seconds=1.0,
        measurements_count=expected,
        acceptable_error_rate=error_rate,
    )
    return TestRunResult(
        test_id="123",
        timestamp="2026",
        ammeter_type="greenlee",
        status="PENDING",
        configuration=config,
        expected_samples=expected,
        attempted_samples=successful + failed,
        successful_samples=successful,
        failed_samples=failed,
        measurements=[],
        statistics={},
        errors=[],
    )


def test_calculate_status_pass():
    res = create_mock_result(10, 10, 0)
    assert ConsoleReporter.calculate_status(res) == "PASS"


def test_calculate_status_fail():
    res = create_mock_result(10, 5, 5, 0.1)  # 50% failure rate > 10%
    assert ConsoleReporter.calculate_status(res) == "FAIL"


def test_calculate_status_error_no_data():
    res = create_mock_result(10, 0, 10, 0.5)  # 100% failure rate, 0 successes
    assert ConsoleReporter.calculate_status(res) == "ERROR"


def test_calculate_status_error_zero_expected():
    res = create_mock_result(0, 0, 0)
    assert ConsoleReporter.calculate_status(res) == "ERROR"


def test_generate_report_from_dict():
    mock_dict = {
        "ammeter_type": "greenlee",
        "test_id": "1234",
        "timestamp": "now",
        "status": "PASS",
        "attempted_samples": 10,
        "expected_samples": 10,
        "successful_samples": 10,
        "failed_samples": 0,
        "statistics": {
            "mean": 5.0,
            "median": 4.0,
            "std_dev": 0.5,
            "min": 1.0,
            "max": 10.0,
        },
        "errors": [
            {"timestamp": "now", "error_type": "Timeout", "error_message": "test"}
        ],
    }
    report = ConsoleReporter.generate_report_from_dict(mock_dict)
    assert "GREENLEE" in report
    assert "1234" in report
    assert "Mean: 5.0" in report
    assert "Timeout: test" in report
