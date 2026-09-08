from dataclasses import dataclass, field
from typing import Optional, List, Dict


@dataclass
class Configuration:
    sampling_frequency_hz: float
    timeout_seconds: float
    measurements_count: Optional[int] = None
    duration_seconds: Optional[float] = None
    acceptable_error_rate: float = 0.1
    ammeters_config: Dict[str, Dict[str, any]] = field(default_factory=dict)
    metrics: List[str] = field(
        default_factory=lambda: ["mean", "median", "std_dev", "min", "max"]
    )
    result_base_dir: str = "results/runs"


@dataclass
class MeasurementResult:
    timestamp: str
    value: Optional[float]
    success: bool
    error_type: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class TestRunResult:
    test_id: str
    timestamp: str
    ammeter_type: str
    status: str
    configuration: Configuration
    expected_samples: int
    attempted_samples: int = 0
    successful_samples: int = 0
    failed_samples: int = 0
    measurements: List[MeasurementResult] = field(default_factory=list)
    statistics: Dict[str, Optional[float]] = field(default_factory=dict)
    errors: List[Dict[str, str]] = field(default_factory=list)
