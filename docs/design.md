# System Design & Architecture Decisions

This document outlines the core technical and architectural decisions made while designing the Ammeter Testing QA Framework, explicitly addressing the requirements of the **Embedded Systems Quality Assurance** exam.

## Compliance with Exam Specification

### 1. Unified Measurement API
**Requirement:** Work with multiple ammeter types and provide consistent reporting.
**Solution:** We implemented the **Factory Pattern** combined with a **Stateless Client Wrapper**. 
The `AmmeterFactory` instantiates an `AmmeterClient` which handles pure TCP socket logic. The client knows nothing about the internal math of the ammeters—it only knows which byte payload to send and what port to connect to. This guarantees uniform exception handling across all devices (connection timeouts, parsing errors, etc.).

### 2. Measurement Sampling & Timing Precision
**Requirement:** Configurable number of measurements, duration, and sampling frequency with precise timing.
**Solution:** 
- The framework dynamically infers the sampling strategy directly from the presence of `measurements_count` or `total_duration_seconds` in the configuration, eliminating redundant configuration flags.
- **Absolute Deadline Scheduling:** We used an absolute scheduling algorithm using `time.monotonic()`. The `TestFramework` calculates the precise timestamp for every future measurement sample before the loop starts. If a specific TCP request times out, the engine skips the sleep delay and instantly attempts to catch up to the absolute schedule, eliminating cumulative timing drift.
- **Strict Tick Enforcement:** The framework does *not* retry failed measurements within the same tick. A failed connection or timeout is recorded as an error and consumes that tick. This ensures the frequency schedule is rigorously maintained over time.

### 3. Result Analysis & Accuracy Assessment
**Requirement:** Compute statistical metrics, analyze performance consistency, and determine relative accuracy.
**Solution:** 
- The `AnalysisEngine` computes standard metrics (mean, median, std dev, min, max) using the Python standard library (`statistics`), cleanly handling edge cases (0 or 1 samples).
- **Consistency Analyzer (Bonus):** Without a calibrated reference, absolute accuracy cannot be proven. Instead, we dynamically evaluate **Relative Consistency** by traversing the history of all runs via the `ConsistencyAnalyzer`, calculating the "Mean of Means" and "Standard Deviation of Means" for each ammeter type over time. This dynamically identifies which ammeter type produces the most reliable, stable outputs across hundreds of testing sessions.

### 4. Test Status Evaluation Rules
**Requirement:** Deterministic evaluation of pass/fail criteria.
**Solution:** 
Statuses are rigorously evaluated against the `acceptable_error_rate` defined in the configuration (defaulting to 10% allowed failure):
- **PASS:** `successful_samples >= (1 - acceptable_error_rate) * expected_samples`.
- **PARTIAL:** `successful_samples > 0`, but below the PASS threshold.
- **FAIL:** `successful_samples == 0` when `expected_samples > 0`.
- **ERROR:** A fatal framework-level exception prevented normal completion.

### 5. Result Management & Visualization
**Requirement:** Robust result archiving, visualization, and zero-server UI.
**Solution:** 
- **Unified Hierarchy:** All test runs are grouped by timestamp under `results/runs/`. Each contains a raw `data.json` file.
- **Client-Side Interactive Dashboard (Bonus):** While initial plans considered generating static `.png` files via `matplotlib`, we pivoted to a much cleaner architectural approach: an interactive, zero-dependency SPA utilizing **Chart.js**. The framework generates a completely static HTML report that dynamically parses the JSON data to render interactive visualizations entirely on the client-side.

### 6. Configuration-Driven Architecture (Bonus)
**Requirement:** Create a configuration-driven testing approach.
**Solution:** 
Eliminated all hardcoded parameters from the codebase. The entire framework is orchestrated strictly by `config/config.yaml`. The factory reads ports/commands, the analysis engine reads requested metrics, and the sampling engine reads timings natively from the configuration file.

---

## Development Methodology

To ensure a robust and production-ready solution, the project was executed in the following structured methodology:

- **1. Legacy Code Review & Bug Fixes:** 
  To meet the strict requirement of using the existing ammeter emulation infrastructure without unnecessary structural changes to their logic, we first had to identify and patch several critical bugs in the provided boilerplate code:
  - **Port Mismatches:** `main.py` initialized emulators on ports 5001, 5002, and 5003, which violated the documented specification. We corrected these to 5000, 5001, and 5002.
  - **Incorrect Client Commands:** The placeholder client calls were missing required instruction flags. We updated them to send the exact required bytes (e.g., `MEASURE_GREENLEE -get_measurement` instead of just `MEASURE_GREENLEE`).
  - **Circutor Extraneous Flag:** The Circutor emulator source code incorrectly demanded an undocumented `-current` flag. We patched the emulator to accept the standard measurement command.
  - **Broken Logger:** `TestLogger` initialized a log directory but never attached a `FileHandler`, resulting in lost logs. We attached the handler to ensure proper file persistence.
  - **Broken Examples & Missing Imports:** We fixed a missing `Dict` import that crashed the original skeleton test framework, and patched broken function calls in the skeleton examples.
  
- **2. Domain Modeling & Architecture:** 
  We completely separated the data layer from the execution layer using strict `dataclasses` defined in `src/testing/types.py`. This enforces a strict schema for all data passing through the system:
  
  - **`MeasurementResult`**: Represents a single sample. Tracks timestamp, value, success flag, and specific error categories.
  - **`TestRunResult`**: Represents an entire testing session. Tracks metadata, configuration, integrity metrics, the full list of samples, calculated statistics, and aggregated errors.

  We then built the Factory and stateless `AmmeterClient` to handle the core TCP logic while passing these strict data objects around.

- **3. Engine Development:** 
  We implemented strict YAML validation (rejecting conflicting configurations) and built the absolute-time sampling engine to guarantee precise timing. Following this, we built the statistical math engine and JSON persistence layer.

- **4. Quality Assurance & Testing:** 
  We developed an exhaustive testing suite (`pytest`) comprising Unit Tests (using mocked sockets for deterministic edge-case testing) and Integration Tests (verifying communication with the live emulators). 
  - Achieved **98% overall test coverage** across over 50 unit tests.
  - Enforced strict PEP8 coding standards with `flake8` and `black` to ensure **0 linting errors**.

- **5. Frontend Visualization Modularization:** 
  To keep the frontend code maintainable, we modularized the UI into separate JavaScript and CSS files within `src/templates/`. The `dashboard_generator.py` script automatically concatenates and minifies these modules, injecting them directly into the final `index.html` report at runtime.

---

## Technical Constraints Respected & Design Trade-offs

- **Standard Library over External Analytics:** We explicitly avoided heavy data science libraries like `pandas`, `numpy`, or `scipy`. While this required building custom statistical parsing logic, given the relatively low mathematical complexity required (standard mean/median calculations), dropping these massive dependencies dramatically simplifies installation and cross-platform compatibility. Only `pyyaml` (for config parsing) and `pytest` (for automated testing) were added.
- **Stateless TCP Connections:** We utilized a fresh socket connection per measurement sample. While this adds minor connection overhead, it ensures absolute resilience against stale sockets and connection drops, especially since the rudimentary emulators do not reliably support persistent HTTP-style keep-alive logic.
- **Maintainability:** Enforced strict Python type-hinting across all files for maximum readability, self-documentation, and IDE safety.
