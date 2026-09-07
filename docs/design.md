# System Design & Architecture Decisions

This document outlines the core technical and architectural decisions made while designing the Ammeter Testing QA Framework, explicitly addressing the requirements of the **Embedded Systems Quality Assurance** exam.

## Compliance with Exam Specification

### 1. Unified Measurement API
**Requirement:** Work with multiple ammeter types and provide consistent reporting.
**Solution:** We implemented the **Factory Pattern** combined with a **Stateless Client Wrapper**. 
The [`AmmeterFactory`](../src/testing/ammeter_factory.py) instantiates an [`AmmeterClient`](../src/testing/ammeter_client.py) which handles pure TCP socket logic. The client knows nothing about the internal math of the ammeters—it only knows which byte payload to send and what port to connect to. This guarantees uniform exception handling across all devices (connection timeouts, parsing errors, etc.).

### 2. Measurement Sampling
**Requirement:** Configurable number of measurements, duration, and sampling frequency with precise timing.
**Solution:** 
- Configuration supports both `count` and `duration` modes.
- We used an **Absolute Deadline Scheduling** algorithm using `time.monotonic()`. The [`TestFramework`](../src/testing/test_framework.py) calculates the precise timestamp for every future measurement sample before the loop starts. If a specific TCP request times out, the engine skips the sleep delay and instantly attempts to catch up to the absolute schedule, eliminating cumulative timing drift.

### 3. Result Analysis & Accuracy Assessment
**Requirement:** Compute statistical metrics, analyze performance consistency, and determine relative accuracy.
**Solution:** 
- The [`AnalysisEngine`](../src/testing/analysis_engine.py) computes standard metrics (mean, median, std dev, min, max) using the Python standard library (`statistics`), cleanly handling edge cases (0 or 1 samples).
- **Consistency Analyzer (Bonus):** Without a calibrated reference, absolute accuracy cannot be proven. Instead, we dynamically evaluate **Relative Consistency** by traversing the history of all runs via the [`ConsistencyAnalyzer`](../src/testing/consistency_analyzer.py), calculating the "Mean of Means" and "Standard Deviation of Means" for each ammeter type over time. This dynamically identifies which ammeter type produces the most reliable, stable outputs across hundreds of testing sessions.

### 4. Result Management & Visualization
**Requirement:** Robust result archiving, visualization, and zero-server UI.
**Solution:** 
- **Unified Hierarchy:** All test runs are grouped by timestamp under `results/runs/`. Each contains a raw `data.json` file.
- **Client-Side Interactive Dashboard (Bonus):** We eliminated external dependencies like `matplotlib` or web servers (Flask/Django). The framework generates a completely static Single Page Application (SPA) in [`index.html`](../index.html). It dynamically injects all historical JSON data and uses **Chart.js** to render interactive, client-side visualizations (Pass Rate Trends, Mean Stability multiline graphs, Error Distribution doughnuts, and Sample Status Timelines).

### 5. Configuration-Driven Architecture (Bonus)
**Requirement:** Create a configuration-driven testing approach.
**Solution:** 
Eliminated all hardcoded parameters from the codebase. The entire framework is orchestrated strictly by [`config/config.yaml`](../config/config.yaml). The factory reads ports/commands, the analysis engine reads requested metrics, and the sampling engine reads timings natively from the configuration file.

---

## Development Methodology

To ensure a robust and production-ready solution, the project was executed in the following structured methodology:

- **1. Legacy Code Review & Bug Fixes:** 
  To meet the strict requirement of using the existing ammeter emulation infrastructure, we first had to identify and patch several critical bugs in the provided boilerplate code:
  - **Port Mismatches:** [`main.py`](../main.py) initialized emulators on ports 5001, 5002, and 5003, which violated the documented specification. We corrected these to 5000, 5001, and 5002.
  - **Incorrect Client Commands:** The placeholder client calls in [`main.py`](../main.py) were missing required instruction flags. We updated them to send the exact required bytes (e.g., `MEASURE_GREENLEE -get_measurement` instead of just `MEASURE_GREENLEE`).
  - **Circutor Extraneous Flag:** The Circutor emulator source code incorrectly demanded an undocumented `-current` flag. We patched the emulator to accept the standard measurement command.
  - **Broken Logger:** [`TestLogger`](../src/utils/logger.py) initialized a log directory but never attached a `FileHandler`, resulting in lost logs. We attached the handler to ensure proper file persistence.
  - **Broken Examples & Missing Imports:** We fixed a missing `Dict` import that crashed the skeleton test framework, and patched `examples/run_tests.py`, which was attempting to call functions without the required positional arguments.
  
- **2. Domain Modeling & Architecture:** 
  We completely separated the data layer from the execution layer using strict `dataclasses` defined in [`src/testing/types.py`](../src/testing/types.py). This enforces a strict schema for all data passing through the system:
  
  - **`MeasurementResult`**: Represents a single sample. Tracks:
    - `timestamp` (str): Exact time of measurement.
    - `value` (float | None): The recorded amperage (if successful).
    - `success` (bool): True if parsed correctly.
    - `error_type` / `error_message`: Categorizes failure (e.g., `TimeoutError`, `ParseError`) instead of crashing the system.
  
  - **`TestRunResult`**: Represents an entire testing session. Tracks:
    - Metadata (`test_id`, `timestamp`, `ammeter_type`).
    - The `Configuration` block used (for perfect historical reproducibility).
    - Integrity metrics (`expected_samples`, `attempted_samples`, `successful_samples`, `failed_samples`).
    - The full list of `MeasurementResult` objects.
    - Calculated `statistics` (Mean, Median, StdDev, etc.).
    - A summary of aggregated `errors`.

  We then built the Factory and stateless `AmmeterClient` to handle the core TCP logic while passing these strict data objects around.

- **3. Engine Development:** 
  We implemented strict YAML validation (rejecting conflicting `count` and `duration` configurations) and built the absolute-time sampling engine to guarantee precise timing. Following this, we built the statistical math engine and JSON persistence layer.

- **4. Quality Assurance & Testing:** 
  We developed an exhaustive testing suite (`pytest`) comprising Unit Tests (using mocked sockets for deterministic edge-case testing) and Integration Tests (verifying communication with the live emulators), reaching high coverage and stability.

- **5. Frontend Visualization:** 
  While initially considering server-side image generation, we pivoted to a much cleaner architectural approach: an interactive, zero-dependency SPA (Single Page Application) utilizing **Chart.js**. This separates the backend data generation from frontend presentation, delivering a highly professional testing dashboard.

---

## Technical Constraints Respected
- **Minimize External Dependencies:** Only `pyyaml` (for config parsing) and `pytest` (for automated testing) were added. Standard libraries handle all core processing. No `pandas`, `numpy`, or `matplotlib` are required to run the engine.
- **Cross-Platform:** Relies exclusively on standard library OS and socket tools.
- **Maintainability:** Enforced strict Python type-hinting across all files for maximum readability, self-documentation, and IDE safety.
