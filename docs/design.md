# System Design & Architecture Decisions

This document outlines the core technical and architectural decisions made while designing the Ammeter Testing QA Framework to satisfy the requirements of the Embedded Systems Quality Assurance exam.

## 1. Unified Measurement API
A central requirement was to interact with disparate devices (Greenlee, ENTES, Circutor) using a unified testing interface.
- **Decision:** We implemented the **Factory Pattern** combined with a **Stateless Client Wrapper**. 
- **Implementation:** The `AmmeterFactory` instantiates an `AmmeterClient` which handles pure TCP socket logic. The client knows nothing about the internal math of the ammeters—it only knows which byte payload to send and what port to connect to. This guarantees uniform exception handling across all devices (connection timeouts, parsing errors, etc.).

## 2. Accurate Timing and Sampling Strategy
In embedded systems, temporal accuracy is paramount. A naive `time.sleep(interval)` loop suffers from cumulative drift.
- **Decision:** We use an **Absolute Deadline Scheduling** algorithm using `time.monotonic()`.
- **Implementation:** The `TestFramework` calculates the precise timestamp for every future measurement sample before the loop starts. If a specific TCP request times out and exceeds its time slot, the engine skips the sleep delay and instantly attempts to catch up to the absolute schedule. This guarantees that a 10-second test at 10Hz takes exactly 10 seconds, regardless of intermittent network latency.

## 3. Separation of Concerns & Typed Models
- **Decision:** Strict segregation between data persistence, test execution, UI generation, and core data models.
- **Implementation:** 
  - `src/testing/types.py` uses `dataclasses` to strictly type the entities (`MeasurementResult`, `TestRunResult`, `Configuration`).
  - `src/testing/test_framework.py` coordinates the test.
  - `src/testing/persistence.py` handles saving to disk.
  - `src/testing/dashboard_generator.py` manages UI logic.
  This allows testing individual pieces via `pytest` deterministically using mocked data structures.

## 4. Minimizing External Dependencies
- **Decision:** Stick to Python's robust Standard Library for the heavy lifting.
- **Implementation:** We completely avoided bulky libraries like `pandas` or `numpy`. The entire parsing, HTTP-generation, and statistical analysis (mean, median, standard deviation) rely on standard Python libraries (`json`, `statistics`, `os`). The *only* external dependency we retained is `matplotlib` to fulfill the "Advanced Visualization" bonus challenge.

## 5. Result Management: Unified Flat Hierarchy
Instead of splitting JSON logs into one hierarchy and HTML files into another, or naming folders with unreadable 36-character UUIDs, we designed a unified architecture.
- **Decision:** `results/runs/YYYY-MM-DD_HHMMSS/{ammeter_type}/`
- **Implementation:** All tests from a single execution of `main.py` are grouped under one timestamped session folder. Each ammeter gets its own subfolder containing the raw `data.json`, the `report.html` dashboard, and the graphs (`time_series.png`, `histogram.png`). Running `--ammeter all` produces three ammeter subfolders inside the same session; running `--ammeter greenlee` produces only one. This makes results portable and trivially easy to share with other QA engineers.

## 6. Relative Consistency Analysis
Given the context of ammeter testing, absolute accuracy cannot be determined without a calibrated reference node.
- **Decision:** We evaluate *Relative Consistency*.
- **Implementation:** The `ConsistencyAnalyzer` traverses the history of all runs, calculating the "Mean of Means" and "Standard Deviation of Means" for each ammeter type over time. This dynamically identifies which ammeter type produces the most reliable, stable outputs across hundreds of testing sessions, providing critical hardware feedback.

## 7. Zero-Server UI Dashboards
- **Decision:** Eliminate the need for Web Servers (like Flask or Django) for result visualization.
- **Implementation:** We generated completely static, cross-linked HTML files embedded with Vanilla Javascript. QA testers can simply double-click `index.html` from their local filesystem to access dynamic table sorting and statistical graphs instantly.

## 8. Configuration-Driven Architecture
- **Decision:** Eliminate all hardcoded parameters (ports, commands, statistical metrics, graph types, save directories) from the codebase to maximize flexibility.
- **Implementation:** The entire framework is orchestrated strictly by `config.yaml`. 
  - `ammeter_factory.py` reads ports and byte-commands directly from the config tree.
  - `analysis_engine.py` dynamically computes only the statistical metrics explicitly requested in the config.
  - `dashboard_generator.py` conditionally renders graphs based on the `visualization` config block.
  This ensures that future changes to hardware or reporting requirements require zero code modifications, only a YAML update.

## 9. Original Bug Fixes
To make the framework functional and production-ready, we identified and corrected the following legacy bugs in the provided infrastructure:
1. **Port Mismatch:** `main.py` initialized emulators on 5001, 5002, 5003 instead of the documented 5000, 5001, 5002.
2. **Command Mismatch:** `main.py` was missing the `-get_measurement` and `-get_data` flags.
3. **Circutor Emulator Bug:** The original code expected an undocumented `-current` flag. This was patched.
4. **Logger Fix & Integration:** Attached `logging.FileHandler` to actually persist emulator logs to disk. Additionally, the `TestLogger` was completely unused in the framework; it was integrated into `AmmeterTestFramework` along with a `StreamHandler` to replace amateur `print()` statements with professional, dual-stream logging (console + file).
