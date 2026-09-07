import time
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Optional

from src.testing.types import TestRunResult, MeasurementResult
from src.testing.constants import MODE_COUNT, MODE_DURATION
from src.testing.ammeter_factory import AmmeterFactory
from src.testing.analysis_engine import AnalysisEngine
from src.testing.persistence import PersistenceLayer
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
                
        # Basic counting (full logic in Phase 6/8)
        successful = sum(1 for r in results if r.success)
        failed = expected_samples - successful
        
        # Phase 6: Statistical Analysis
        stats = AnalysisEngine.analyze(results)
        
        run_result = TestRunResult(
            test_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            ammeter_type=ammeter_type,
            status="PENDING", # to be calculated in Phase 8
            configuration=self.config,
            expected_samples=expected_samples,
            attempted_samples=len(results),
            successful_samples=successful,
            failed_samples=failed,
            measurements=results,
            statistics=stats,
            errors=[] # to be calculated in Phase 8
        )
        
        # Phase 7: Persistence
        PersistenceLayer.save_result(run_result)
        
        return run_result