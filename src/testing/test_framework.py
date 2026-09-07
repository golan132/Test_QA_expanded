import time
import os
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Optional

from src.testing.types import TestRunResult, MeasurementResult
from src.testing.constants import MODE_COUNT, MODE_DURATION
from src.testing.ammeter_factory import AmmeterFactory
from src.testing.analysis_engine import AnalysisEngine
from src.testing.persistence import PersistenceLayer
from src.testing.reporter import ConsoleReporter
from src.testing.dashboard_generator import DashboardGenerator
from src.utils.config import load_config

class AmmeterTestFramework:
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = load_config(config_path)
        
    def run_test(self, ammeter_type: str) -> TestRunResult:
        client = AmmeterFactory.get_client(ammeter_type, self.config.timeout_seconds)
        
        # Calculate expected samples
        if self.config.mode == MODE_COUNT:
            expected_samples = self.config.measurements_count
        else:
            expected_samples = int(self.config.duration_seconds * self.config.sampling_frequency_hz)
            
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
                
        # Basic counting
        successful = sum(1 for r in results if r.success)
        failed = expected_samples - successful
        
        # Phase 6: Statistical Analysis
        stats = AnalysisEngine.analyze(results)
        
        # Collect errors
        errors = []
        for r in results:
            if not r.success and r.error_message:
                errors.append({
                    "timestamp": r.timestamp,
                    "error_type": r.error_type or "Unknown",
                    "error_message": r.error_message
                })
        
        run_result = TestRunResult(
            test_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            ammeter_type=ammeter_type,
            status="PENDING", # to be calculated below
            configuration=self.config,
            expected_samples=expected_samples,
            attempted_samples=len(results),
            successful_samples=successful,
            failed_samples=failed,
            measurements=results,
            statistics=stats,
            errors=errors
        )
        
        # Phase 8: Calculate Status and Print Report
        run_result.status = ConsoleReporter.calculate_status(run_result)
        
        # Phase 7: Persistence
        PersistenceLayer.save_result(run_result)
        
        # Phase 12: HTML Dashboard Generation
        dashboard_path = DashboardGenerator.generate_dashboard(run_result)
        
        # Print report
        report_text = ConsoleReporter.generate_report(run_result)
        print(report_text)
        print(f"Full Dashboard: file:///{os.path.abspath(dashboard_path).replace(chr(92), '/')}")
        
        return run_result