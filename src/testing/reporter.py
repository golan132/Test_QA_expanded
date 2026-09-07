from src.testing.types import TestRunResult

class ConsoleReporter:
    @staticmethod
    def calculate_status(result: TestRunResult) -> str:
        if result.expected_samples == 0 or result.attempted_samples == 0:
            return "ERROR"
            
        error_rate = result.failed_samples / result.expected_samples
        if result.successful_samples == 0:
            return "ERROR"
        elif error_rate <= result.configuration.acceptable_error_rate:
            return "PASS"
        else:
            return "FAIL"

    @staticmethod
    def generate_report(result: TestRunResult) -> str:
        report = []
        report.append(f"=== Test Report: {result.ammeter_type.upper()} ===")
        report.append(f"Test ID: {result.test_id}")
        report.append(f"Timestamp: {result.timestamp}")
        report.append(f"Overall Status: {result.status}")
        report.append("-" * 30)
        report.append(f"Total Attempts: {result.attempted_samples} (Expected: {result.expected_samples})")
        report.append(f"Successes: {result.successful_samples}")
        report.append(f"Failures: {result.failed_samples}")
        
        stats = result.statistics
        if stats:
            report.append("-" * 30)
            report.append("Statistics:")
            report.append(f"  Min: {stats.get('min')}")
            report.append(f"  Max: {stats.get('max')}")
            report.append(f"  Mean: {stats.get('mean')}")
            report.append(f"  Median: {stats.get('median')}")
            report.append(f"  Std Dev: {stats.get('std_dev')}")
            
        if result.errors:
            report.append("-" * 30)
            report.append("Errors:")
            for e in result.errors[:5]: # Show up to 5 errors to avoid flooding
                report.append(f"  - [{e.get('timestamp')}] {e.get('error_type')}: {e.get('error_message')}")
            if len(result.errors) > 5:
                report.append(f"  ... and {len(result.errors) - 5} more errors.")
                
        return "\n".join(report)
