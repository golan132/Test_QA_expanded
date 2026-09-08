# Ammeter Testing QA Framework

A comprehensive, configuration-driven testing framework designed for automated Quality Assurance of Embedded Current Measurement Systems (Ammeters). 

This project provides a robust API to communicate with Greenlee, ENTES, and CIRCUTOR ammeter emulators, performing precise time-based sampling, statistical data analysis, automated UI dashboard generation, and historical consistency tracking.

---

## Key Features

* **Unified API:** A single `AmmeterClient` architecture seamlessly handles different TCP-based hardware.
* **Precision Sampling:** Absolute time scheduling (`time.monotonic()`) eliminates cumulative drift during long duration tests.
* **Configurable Execution:** Control the framework entirely via `config/config.yaml` (Mode, Duration, Frequency, Tolerances).
* **Automated SPA Dashboard:** Automatically generates a beautiful, dependency-free Single Page Application (`index.html`) using **Chart.js**. No backend web server required.
* **Historical Analysis:** Tracks hardware performance over time to calculate "Relative Consistency" across devices.
* **Resilient Architecture:** Structured error handling for network timeouts, bad connections, and malformed hardware data.

---

## Getting Started

### 1. Prerequisites
Ensure you have Python 3.10+ installed. Install the minimal required dependencies:
```bash
pip install -r requirements.txt
```
*(Dependencies: `pytest` for the automated test suite and `pyyaml` for configuration parsing. The UI relies entirely on standard HTML/JS without Python visualization libraries).*

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

## Result Management & Analysis (CLI)

The framework strictly fulfills all Result Management and Result Analysis requirements natively within the terminal.

### Retrieve Historical Archive
List all past test executions, including their unique UUIDs, timestamp, and pass rates:
```bash
python main.py --history
```

### View Specific Run Statistics
Input a unique Test ID (UUID) to reconstruct the mathematical breakdown for that exact run (Mean, Median, Standard Deviation, Min, Max):
```bash
python main.py --show-run [TEST_ID]
```

### Accuracy Assessment & Precision 
Mathematically scan the entire history of runs to compute the **Mean of Means** and the **Drift (Standard Deviation)**, proving which ammeter is objectively the most reliable:
```bash
python main.py --analyze-consistency
```

---

## Viewing Results (Dashboard)

After execution, the framework automatically generates a unified data structure in the `results/` directory and rebuilds the frontend.

To view your test results visually, simply open `index.html` in your web browser. 

### The Global Dashboard
The `index.html` file serves as the master dashboard. It features two primary tabs:
- **Home (Recent Executions):** A dynamically sortable table (via Javascript) of every test run, allowing you to instantly view detailed pass rates and execution metadata. Hover over any column header for an interactive tooltip explaining the metric!
- **Full Dashboard (Analytics):** Visual line graphs and doughnut charts built in Chart.js showing overall pass rate trends, system volume, and the **Relative Consistency Analysis** comparing all hardware side-by-side.

### The Unified Folder Structure
Raw data and specific test artifacts are stored in `results/runs/`. Each execution of `main.py` creates a timestamped **session folder** (e.g., `2026-09-08_002530/`). Inside, each ammeter tested gets its own subfolder containing a strict `data.json` file carrying all telemetry and metadata.

---

## Testing the Framework
The framework includes a fully automated `pytest` suite simulating edge cases, configuration validation, consistency algorithms, and persistence mapping without invoking network requests.

```bash
python -m pytest tests/
```

---

## Documentation
For a deep dive into the architectural decisions, structural patterns, and the legacy bugs patched from the original emulator codebase, please refer to the technical specification in [docs/design.md](docs/design.md).