import socket
from src.testing.types import MeasurementResult
from src.utils.Utils import get_current_timestamp


class AmmeterClient:
    def __init__(self, port: int, command: bytes, timeout: float = 2.0):
        self.port = port
        self.command = command
        self.timeout = timeout

    def measure(self) -> MeasurementResult:
        timestamp = get_current_timestamp()
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(self.timeout)
                s.connect(("127.0.0.1", self.port))
                s.sendall(self.command)

                # Receive data
                data = s.recv(1024)

                if not data:
                    return MeasurementResult.create_failure(
                        timestamp=timestamp,
                        error_type="EmptyResponse",
                        error_message="Received empty response from emulator",
                    )

                # The emulators return a string representation of a float
                decoded_str = data.decode("utf-8").strip()
                value = float(decoded_str)

                return MeasurementResult.create_success(timestamp=timestamp, value=value)

        except socket.timeout:
            return MeasurementResult.create_failure(
                timestamp=timestamp,
                error_type="TimeoutError",
                error_message="Socket timeout",
            )
        except ConnectionRefusedError:
            return MeasurementResult.create_failure(
                timestamp=timestamp,
                error_type="ConnectionError",
                error_message="Connection refused, is the emulator running on this port?",
            )
        except ValueError as e:
            return MeasurementResult.create_failure(
                timestamp=timestamp,
                error_type="ParseError",
                error_message=f"Failed to parse float from response: {e}",
            )
        except Exception as e:
            return MeasurementResult.create_failure(
                timestamp=timestamp,
                error_type=type(e).__name__,
                error_message=str(e),
            )
