import threading
import time
import argparse
import sys
import os
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")

from src.testing.test_framework import AmmeterTestFramework
from src.testing.consistency_analyzer import ConsistencyAnalyzer
from src.testing.persistence import PersistenceLayer
from src.testing.reporter import ConsoleReporter
from src.testing.error_simulation import ErrorSimulator
from concurrent.futures import ThreadPoolExecutor


from src.testing.emulator_manager import EmulatorManager


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ammeter Emulator & Testing Framework")
    parser.add_argument(
        "--ammeter",
        type=str,
        choices=["greenlee", "entes", "circutor", "all"],
        help="Run test framework against specified ammeter",
    )
    parser.add_argument(
        "--analyze-consistency",
        action="store_true",
        help="Analyze historical test runs for relative accuracy and precision",
    )
    parser.add_argument(
        "--history",
        action="store_true",
        help="List all historical test runs (Result Management)",
    )
    parser.add_argument(
        "--show-run",
        type=str,
        metavar="TEST_ID",
        help="Show detailed statistical report for a specific test run (Result Analysis)",
    )
    parser.add_argument("--count", type=int, help="Override number of measurements")
    parser.add_argument("--duration", type=int, help="Override total duration in seconds")
    parser.add_argument("--frequency", type=float, help="Override sampling frequency in Hz")
    parser.add_argument("--errors", action="store_true", help="Run the error simulation suite")
    parser.add_argument("--no-emulators", action="store_true", help="Do not start the emulators (useful when running from another process)")
    parser.add_argument("--export-run", type=str, metavar="TEST_ID", help="Export CSV and PNG graphs for a specific historical test run")
    args = parser.parse_args()

    # Input validation for CLI overrides
    if args.count is not None and args.count <= 0:
        logging.error("--count must be a positive integer")
        sys.exit(1)
    if args.duration is not None and args.duration <= 0:
        logging.error("--duration must be a positive integer")
        sys.exit(1)
    if args.frequency is not None and args.frequency <= 0:
        logging.error("--frequency must be a positive number")
        sys.exit(1)

    if args.errors:
        ErrorSimulator().run_all()
        sys.exit(0)

    if args.history:
        runs = PersistenceLayer.get_all_runs()
        if not runs:
            logging.info("No historical test runs found.")
            sys.exit(0)

        logging.info("\n=== Test Run History (Result Management) ===")
        logging.info(
            f"{'Timestamp':<22} | {'Ammeter':<10} | {'Test ID':<38} | {'Status':<6} | {'Pass Rate'}"
        )
        logging.info("-" * 105)
        for r in runs:
            logging.info(
                f"{r['timestamp']:<22} | {r['ammeter_type']:<10} | {r['test_id']:<38} | {r['status']:<6} | {r['pass_rate']}"
            )
        logging.info("-" * 105 + "\n")
        sys.exit(0)

    if args.show_run:
        run_data = PersistenceLayer.get_run_by_id(args.show_run)
        if not run_data:
            logging.info(f"Test run '{args.show_run}' not found.")
            sys.exit(1)

        logging.info("\n" + ConsoleReporter.generate_report_from_dict(run_data) + "\n")
        sys.exit(0)

    if args.export_run:
        run_data = PersistenceLayer.get_run_by_id(args.export_run)
        if not run_data:
            logging.info(f"Test run '{args.export_run}' not found.")
            sys.exit(1)
        
        runs_dir = "results/runs"
        target_dir = run_data.get("_source_dir")
        if not target_dir or not os.path.exists(target_dir):
            logging.error("Source directory for this run could not be determined.")
            sys.exit(1)
        
        csv_path = PersistenceLayer.export_csv(run_data, target_dir)
        ts_path, hist_path = PersistenceLayer.export_graphs(run_data, target_dir)
        
        logging.info(f"\nSuccessfully generated exports for Test ID: {args.export_run}")
        logging.info(f"CSV: {csv_path}")
        logging.info(f"Time Series Graph: {ts_path}")
        logging.info(f"Histogram Graph: {hist_path}")
        sys.exit(0)


    if args.analyze_consistency:
        logging.info("\n--- Accuracy Assessment & Relative Precision ---")
        consistency = ConsistencyAnalyzer.analyze_history()

        if not consistency:
            logging.info("No historical data found. Run some tests first.")
            sys.exit(0)

        logging.info(
            f"{'Ammeter':<15} | {'Historical Runs':<15} | {'Mean of Means (A)':<20} | {'StdDev/Drift (A)'}"
        )
        logging.info("-" * 75)
        for ammeter, stats in consistency.items():
            logging.info(
                f"{ammeter.upper():<15} | {stats['historical_runs']:<15} | {stats['mean_of_means']:<20.5f} | {stats['std_dev_of_means']:.5f}"
            )

        logging.info("\n" + "-" * 75)
        best = ConsistencyAnalyzer.get_most_reliable_ammeter(consistency)
        logging.info(f"VERDICT: Most Reliable Measurement Method: {best}")
        logging.info("-" * 75 + "\n")
        sys.exit(0)

    if not args.no_emulators:
        EmulatorManager().start_all_emulators_in_background()

    if args.ammeter:
        framework = AmmeterTestFramework()
        
        # Apply CLI overrides
        if args.count is not None:
            framework.config.measurements_count = args.count
        if args.duration is not None:
            framework.config.duration_seconds = args.duration
        if args.frequency is not None:
            framework.config.sampling_frequency_hz = args.frequency

        ammeters_to_test = (
            ["greenlee", "entes", "circutor"]
            if args.ammeter == "all"
            else [args.ammeter]
        )

        if args.ammeter == "all":
            logging.info("\nRunning tests in parallel...")
            with ThreadPoolExecutor(max_workers=3) as executor:
                # Submit all tests to run concurrently
                futures = {executor.submit(framework.run_test, ammeter): ammeter for ammeter in ammeters_to_test}
                for future in futures:
                    future.result() # Wait for all to finish
        else:
            for ammeter in ammeters_to_test:
                logging.info(f"\nStarting test for {ammeter}...")
                framework.run_test(ammeter)
    else:
        logging.info("\nEmulators are running. Use --ammeter to run tests.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info("Exiting...")
