import threading
import time
import argparse
import sys
import os
import yaml

from Ammeters.Circutor_Ammeter import CircutorAmmeter
from Ammeters.Entes_Ammeter import EntesAmmeter
from Ammeters.Greenlee_Ammeter import GreenleeAmmeter
from src.testing.test_framework import AmmeterTestFramework
from src.testing.consistency_analyzer import ConsistencyAnalyzer
from src.testing.persistence import PersistenceLayer
from src.testing.reporter import ConsoleReporter


def get_ammeter_ports():
    ports = {"greenlee": 5000, "entes": 5001, "circutor": 5002}
    try:
        if os.path.exists("config/config.yaml"):
            with open("config/config.yaml", "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                ammeters = data.get("ammeters", {})
                for name in ports:
                    ports[name] = ammeters.get(name, {}).get("port", ports[name])
    except Exception as e:
        print(f"Failed to load ports from config, using defaults: {e}")
    return ports


def run_greenlee_emulator(port):
    greenlee = GreenleeAmmeter(port)
    greenlee.start_server()


def run_entes_emulator(port):
    entes = EntesAmmeter(port)
    entes.start_server()


def run_circutor_emulator(port):
    circutor = CircutorAmmeter(port)
    circutor.start_server()


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
    args = parser.parse_args()

    if args.history:
        runs = PersistenceLayer.get_all_runs()
        if not runs:
            print("No historical test runs found.")
            sys.exit(0)

        print("\n=== Test Run History (Result Management) ===")
        print(
            f"{'Timestamp':<22} | {'Ammeter':<10} | {'Test ID':<38} | {'Status':<6} | {'Pass Rate'}"
        )
        print("-" * 105)
        for r in runs:
            print(
                f"{r['timestamp']:<22} | {r['ammeter_type']:<10} | {r['test_id']:<38} | {r['status']:<6} | {r['pass_rate']}"
            )
        print("-" * 105 + "\n")
        sys.exit(0)

    if args.show_run:
        run_data = PersistenceLayer.get_run_by_id(args.show_run)
        if not run_data:
            print(f"Test run '{args.show_run}' not found.")
            sys.exit(1)

        print("\n" + ConsoleReporter.generate_report_from_dict(run_data) + "\n")
        sys.exit(0)

    if args.analyze_consistency:
        print("\n--- Accuracy Assessment & Relative Precision ---")
        consistency = ConsistencyAnalyzer.analyze_history()

        if not consistency:
            print("No historical data found. Run some tests first.")
            sys.exit(0)

        print(
            f"{'Ammeter':<15} | {'Historical Runs':<15} | {'Mean of Means (A)':<20} | {'StdDev/Drift (A)'}"
        )
        print("-" * 75)
        for ammeter, stats in consistency.items():
            print(
                f"{ammeter.upper():<15} | {stats['historical_runs']:<15} | {stats['mean_of_means']:<20.5f} | {stats['std_dev_of_means']:.5f}"
            )

        print("\n" + "-" * 75)
        best = ConsistencyAnalyzer.get_most_reliable_ammeter(consistency)
        print(f"VERDICT: Most Reliable Measurement Method: {best}")
        print("-" * 75 + "\n")
        sys.exit(0)

    ports = get_ammeter_ports()

    # Start each ammeter in a separate thread
    threading.Thread(
        target=run_greenlee_emulator, args=(ports["greenlee"],), daemon=True
    ).start()
    threading.Thread(
        target=run_entes_emulator, args=(ports["entes"],), daemon=True
    ).start()
    threading.Thread(
        target=run_circutor_emulator, args=(ports["circutor"],), daemon=True
    ).start()

    # Wait for the servers to start
    time.sleep(1)

    if args.ammeter:
        framework = AmmeterTestFramework()
        ammeters_to_test = (
            ["greenlee", "entes", "circutor"]
            if args.ammeter == "all"
            else [args.ammeter]
        )

        for ammeter in ammeters_to_test:
            print(f"\nStarting test for {ammeter}...")
            framework.run_test(ammeter)
            time.sleep(1)
    else:
        print("\nEmulators are running. Use --ammeter to run tests.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Exiting...")
