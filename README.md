# Ammeter Testing QA Framework

A comprehensive, configuration-driven testing framework designed for automated Quality Assurance of Embedded Current Measurement Systems (Ammeters). 

This project provides a robust API to communicate with Greenlee, ENTES, and CIRCUTOR ammeter emulators, performing precise time-based sampling, statistical data analysis, automated UI dashboard generation, and historical consistency tracking.

---

## Key Features

* **Unified API:** A single `AmmeterClient` architecture seamlessly handles different TCP-based hardware.
* **Precision Sampling:** Absolute time scheduling (`time.monotonic()`) eliminates cumulative drift during long duration tests.
* **Configurable Execution:** Control the framework entirely via `config/config.yaml` (Mode, Duration, Frequency, Tolerances).
* **Automated Dashboards:** Automatically generates static HTML reports and Matplotlib graphs without requiring a web server.
* **Historical Analysis:** Tracks hardware performance over time to calculate "Relative Consistency" across devices.
* **Resilient Architecture:** Structured error handling for network timeouts, bad connections, and malformed hardware data.

---

## Getting Started

### 1. Prerequisites
Ensure you have Python 3.10+ installed. Install the minimal required dependencies:
```bash
pip install -r requirements.txt
```
*(Dependencies: `pytest` for the automated test suite, `pyyaml` for configuration parsing, and `matplotlib` for generating the dashboard charts).*

### 2. Configuration
Modify `config/config.yaml` to define your test parameters. The system supports two modes: `count` and `duration`.

```yaml
testing:
  sampling:
    mode: "count"              # "count" (fixed samples) or "duration" (time-based)
    measurements_count: 50     # Use for 'count' mode
    sampling_frequency_hz: 5   # Samples per second
    timeout_seconds: 2.0       # Timeout for TCP requests
    acceptable_error_rate: 0.1 # 10% packet loss tolerance for PASS status
```

### 3. Running the Framework
The framework is fully integrated into `main.py`. It boots up the local emulators (Greenlee on 5000, ENTES on 5001, Circutor on 5002) and executes the automated test suites.

```bash
# Run tests on all ammeters sequentially
python main.py --ammeter all

# Run a test on a specific ammeter
python main.py --ammeter greenlee
```

---

## Viewing Results

After execution, the framework automatically generates a unified data structure in the `results/` directory.

To view your test results, open `index.html` in your web browser. 

### The Global Dashboard
The `index.html` file serves as the master dashboard. It features:
- **Global Statistics:** Visual pie and bar charts showing overall pass rates across the system.
- **Consistency Analysis:** A breakdown of how reliable each ammeter is historically (Mean of Means, Std Dev of Means).
- **Recent Executions:** A dynamically sortable table (via Javascript) of every test run, allowing you to instantly open individual test reports.

### The Unified Folder Structure
Raw data and specific test artifacts are stored in `results/runs/`. Each execution of `main.py` creates a timestamped **session folder** (e.g., `2026-09-08_002530/`). Inside, each ammeter tested gets its own subfolder (e.g., `greenlee/`) containing:
1. `data.json`: Raw telemetry data and metadata.
2. `report.html`: The individual HTML dashboard for that specific run.
3. `time_series.png` & `histogram.png`: Data visualizations.

---

## Testing the Framework
The framework includes a fully automated `pytest` suite simulating edge cases, configuration validation, consistency algorithms, and persistence mapping without invoking network requests.

```bash
python -m pytest tests/
```

---

## Documentation
For a deep dive into the architectural decisions, structural patterns, and the bugs fixed from the original emulator codebase, please refer to the technical specification in [docs/design.md](docs/design.md).