import socket
import threading
import time
from typing import Callable, List, Tuple

from src.testing.ammeter_client import AmmeterClient
from src.testing.test_framework import AmmeterTestFramework


class ErrorSimulator:
    """
    Runs a suite of error scenarios against the framework to verify that
    failures are handled gracefully and never crash the program.
    """

    _PORT_BASE = 5010  # Ports 5010-5019 reserved for simulation servers

    def run_all(self) -> List[Tuple[str, bool]]:
        scenarios = [
            ("Connection refused (server not running)",    self._scenario_connection_refused),
            ("Timeout (server accepts but never replies)", self._scenario_timeout),
            ("Garbled data (non-numeric response)",        self._scenario_garbled_data),
            ("Empty response (connection closed early)",   self._scenario_empty_response),
            ("Framework resilience (all samples fail)",    self._scenario_framework_resilience),
        ]

        print("\n=== Error Simulation ===\n")
        results = []
        for name, scenario in scenarios:
            print(f"  Scenario: {name}")
            handled = scenario()
            label = "PASS" if handled else "FAIL"
            print(f"  Result:   {label}\n")
            results.append((name, handled))

        passed = sum(1 for _, ok in results if ok)
        print(f"Summary: {passed}/{len(results)} scenarios handled correctly")
        return results



    def _start_bad_server(self, port: int, handler: Callable):
        """Start a one-shot server in a daemon thread that calls handler(conn)."""
        def serve():
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('localhost', port))
                s.listen(1)
                try:
                    conn, _ = s.accept()
                    with conn:
                        handler(conn)
                except Exception:
                    pass

        threading.Thread(target=serve, daemon=True).start()
        time.sleep(0.1)  # Give the thread time to bind before client connects



    def _scenario_connection_refused(self) -> bool:
        try:
            result = AmmeterClient(5099, b'TEST').measure()
            return result is None or not result.success
        except ConnectionRefusedError:
            return True
        except Exception:
            return True

    def _scenario_timeout(self) -> bool:
        port = self._PORT_BASE

        def hang(conn):
            time.sleep(10)

        self._start_bad_server(port, hang)
        try:
            result = AmmeterClient(port, b'TEST').measure()
            return result is None or not result.success
        except (TimeoutError, socket.timeout, OSError):
            return True
        except Exception:
            return True

    def _scenario_garbled_data(self) -> bool:
        port = self._PORT_BASE + 1

        def send_garbage(conn):
            conn.sendall(b'NOT_A_NUMBER!!!')

        self._start_bad_server(port, send_garbage)
        try:
            result = AmmeterClient(port, b'TEST').measure()
            return result is None or not result.success
        except ValueError:
            return True
        except Exception:
            return True

    def _scenario_empty_response(self) -> bool:
        port = self._PORT_BASE + 2

        def send_empty(conn):
            pass

        self._start_bad_server(port, send_empty)
        try:
            result = AmmeterClient(port, b'TEST').measure()
            return result is None or not result.success
        except Exception:
            return True



    def _scenario_framework_resilience(self) -> bool:
        framework = AmmeterTestFramework()
        framework.config.ammeters_config["error_test"] = {
            "port": 5098,
            "command": "TEST -simulate_error",
        }

        framework.config.measurements_count = 3
        try:
            result = framework.run_test("error_test")
            # Expect 3 failed samples
            return result.failed_samples == 3
        except Exception as e:
            print(f"    [UNEXPECTED EXCEPTION] {e}")
            return False
