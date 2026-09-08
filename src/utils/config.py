import yaml
from src.testing.types import Configuration
from src.testing.constants import (
    DEFAULT_TIMEOUT_SECONDS,
    DEFAULT_ACCEPTABLE_ERROR_RATE,
    DEFAULT_SAMPLING_FREQUENCY_HZ,
    DEFAULT_MEASUREMENTS_COUNT,
)


def load_config(config_path: str) -> Configuration:
    """
    Loads and strictly validates the testing configuration from a YAML file.
    Enforces that either count OR duration is provided, not both.
    Supports 'null' or missing values by falling back to robust defaults.
    """
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except (FileNotFoundError, yaml.YAMLError) as e:
        import logging

        logging.warning(
            f"Failed to load config from {config_path} ({e}). Using robust defaults."
        )
        data = {}

    sampling = data.get("testing", {}).get("sampling", {})
    if sampling is None:
        sampling = {}

    freq = sampling.get("sampling_frequency_hz")
    if freq == "NULL" or freq is None:
        freq = DEFAULT_SAMPLING_FREQUENCY_HZ
    freq = float(freq)
    if freq <= 0:
        raise ValueError("sampling_frequency_hz must be > 0")

    count = sampling.get("measurements_count")
    if count == "NULL":
        count = None
    elif count is not None:
        count = int(count)

    duration = sampling.get("total_duration_seconds")
    if duration == "NULL":
        duration = None
    elif duration is not None:
        duration = float(duration)

    if count is not None and duration is not None:
        raise ValueError(
            "Strict validation failed: Cannot define both measurements_count and total_duration_seconds. Choose one mode."
        )

    if count is not None:
        if count <= 0:
            raise ValueError("measurements_count must be > 0")
    elif duration is not None:
        if duration <= 0:
            raise ValueError("total_duration_seconds must be > 0")
    else:
        # Default fallback when both are null
        count = DEFAULT_MEASUREMENTS_COUNT

    timeout = sampling.get("timeout_seconds")
    if timeout == "NULL" or timeout is None:
        timeout = DEFAULT_TIMEOUT_SECONDS

    error_rate = sampling.get("acceptable_error_rate")
    if error_rate == "NULL" or error_rate is None:
        error_rate = DEFAULT_ACCEPTABLE_ERROR_RATE

    ammeters_config = data.get("ammeters", {})
    if ammeters_config is None:
        ammeters_config = {}

    analysis = data.get("analysis", {})
    if analysis is None:
        analysis = {}

    metrics = analysis.get("statistical_metrics")
    if metrics is None:
        metrics = ["mean", "median", "std_dev", "min", "max"]

    visualization = analysis.get("visualization", {})
    if visualization is None:
        visualization = {}

    vis_enabled = visualization.get("enabled", True)
    plot_types = visualization.get("plot_types")
    if plot_types is None:
        plot_types = [
            "time_series",
            "histogram",
            "global_pie_chart",
            "global_bar_chart",
        ]

    result_management = data.get("result_management", {})
    if result_management is None:
        result_management = {}

    base_dir = result_management.get("base_dir", "results/runs")

    return Configuration(
        sampling_frequency_hz=freq,
        timeout_seconds=float(timeout),
        measurements_count=count,
        duration_seconds=duration,
        acceptable_error_rate=float(error_rate),
        ammeters_config=ammeters_config,
        metrics=metrics,
        visualizations_enabled=vis_enabled,
        plot_types=plot_types,
        result_base_dir=base_dir,
    )
