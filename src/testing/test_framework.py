import time
import os
import uuid
from src.utils.Utils import get_current_timestamp
from typing import List

from src.testing.types import TestRunResult, MeasurementResult
from src.testing.ammeter_factory import AmmeterFactory
from src.testing.analysis_engine import AnalysisEngine
from src.testing.persistence import PersistenceLayer
from src.testing.reporter import ConsoleReporter
from src.testing.dashboard_generator import DashboardGenerator
from src.utils.config import load_config
from src.utils.logger import TestLogger


class AmmeterTestFramework:
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = load_config(config_path)
        self.logger = TestLogger("framework")

        # Generate a single session folder for this execution.
        # All ammeter tests within this run share this folder.
        session_timestamp = get_current_timestamp().replace(":", "")
        self.session_dir = os.path.join(self.config.result_base_dir, session_timestamp)

    def run_test(self, ammeter_type: str) -> TestRunResult:
        try:
            client = AmmeterFactory.get_client(ammeter_type, self.config)

            # Calculate expected samples
            if self.config.measurements_count is not None:
                expected_samples = self.config.measurements_count
            else:
                expected_samples = int(
                    self.config.duration_seconds * self.config.sampling_frequency_hz
                )

            interval = 1.0 / self.config.sampling_frequency_hz
            results: List[MeasurementResult] = []

            start_time = time.monotonic()
            next_sample_deadline = start_time

            for _ in range(expected_samples):
                result = client.measure()
                results.append(result)

                next_sample_deadline += interval
                sleep_time = next_sample_deadline - time.monotonic()
                if sleep_time > 0:
                    time.sleep(sleep_time)

            successful = sum(1 for r in results if r.success)
            failed = expected_samples - successful

            stats = AnalysisEngine.analyze(results, self.config.metrics)

            errors = []
            for r in results:
                if not r.success and r.error_message:
                    errors.append(
                        {
                            "timestamp": r.timestamp,
                            "error_type": r.error_type or "Unknown",
                            "error_message": r.error_message,
                        }
                    )

            run_result = TestRunResult(
                test_id=str(uuid.uuid4()),
                timestamp=get_current_timestamp(),
                ammeter_type=ammeter_type,
                status="PENDING",
                configuration=self.config,
                expected_samples=expected_samples,
                attempted_samples=len(results),
                successful_samples=successful,
                failed_samples=failed,
                measurements=results,
                statistics=stats,
                errors=errors,
            )

            run_result.status = ConsoleReporter.calculate_status(run_result)

            run_dir = PersistenceLayer.save_result(run_result, self.session_dir)

            DashboardGenerator.generate_dashboard(run_result, run_dir, self.config)

            report_text = ConsoleReporter.generate_report(run_result)
            self.logger.info(report_text)
            self.logger.info(
                f"Full Dashboard: file:///{os.path.abspath('index.html').replace(chr(92), '/')}"
            )

            return run_result

        except Exception as e:
            self.logger.error(
                f"\n[FATAL ERROR] Test framework crashed during {ammeter_type} test: {e}"
            )

            # Construct an ERROR result so it's not silently lost
            error_result = TestRunResult(
                test_id=str(uuid.uuid4()),
                timestamp=get_current_timestamp(),
                ammeter_type=ammeter_type,
                status="ERROR",
                configuration=self.config,
                expected_samples=0,
                attempted_samples=0,
                successful_samples=0,
                failed_samples=0,
                measurements=[],
                statistics={m: None for m in self.config.metrics},
                errors=[
                    {
                        "timestamp": get_current_timestamp(),
                        "error_type": "FatalFrameworkError",
                        "error_message": str(e),
                    }
                ],
            )

            # Try to save the error report if possible
            try:
                run_dir = PersistenceLayer.save_result(error_result, self.session_dir)
                DashboardGenerator.generate_dashboard(
                    error_result, run_dir, self.config
                )
            except Exception as save_err:
                self.logger.error(f"Could not save fatal error report: {save_err}")

            return error_result
