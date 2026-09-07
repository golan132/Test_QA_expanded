import socket
from datetime import datetime, timezone
from src.testing.types import MeasurementResult

class AmmeterClient:
    def __init__(self, port: int, command: bytes, timeout: float = 2.0):
        self.port = port
        self.command = command
        self.timeout = timeout
        
    def measure(self) -> MeasurementResult:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(self.timeout)
                s.connect(('127.0.0.1', self.port))
                s.sendall(self.command)
                
                # Receive data
                data = s.recv(1024)
                
                if not data:
                    return MeasurementResult(
                        timestamp=timestamp,
                        value=None,
                        success=False,
                        error_type="EmptyResponse",
                        error_message="Received empty response from emulator"
                    )
                    
                # The emulators return a string representation of a float
                decoded_str = data.decode('utf-8').strip()
                value = float(decoded_str)
                
                return MeasurementResult(
                    timestamp=timestamp,
                    value=value,
                    success=True
                )
                
        except socket.timeout as e:
            return MeasurementResult(
                timestamp=timestamp,
                value=None,
                success=False,
                error_type="TimeoutError",
                error_message="Socket timeout"
            )
        except ConnectionRefusedError as e:
            return MeasurementResult(
                timestamp=timestamp,
                value=None,
                success=False,
                error_type="ConnectionError",
                error_message="Connection refused, is the emulator running on this port?"
            )
        except ValueError as e:
            return MeasurementResult(
                timestamp=timestamp,
                value=None,
                success=False,
                error_type="ParseError",
                error_message=f"Failed to parse float from response: {e}"
            )
        except Exception as e:
            return MeasurementResult(
                timestamp=timestamp,
                value=None,
                success=False,
                error_type=type(e).__name__,
                error_message=str(e)
            )
