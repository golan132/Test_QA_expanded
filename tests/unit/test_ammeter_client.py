import socket
from unittest.mock import patch, MagicMock
from src.testing.ammeter_client import AmmeterClient


def test_measure_empty_response():
    client = AmmeterClient(port=5000, command=b"TEST")
    with patch("socket.socket") as mock_socket:
        mock_sock_instance = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_sock_instance
        mock_sock_instance.recv.return_value = b""  # Empty response

        result = client.measure()
        assert result.success is False
        assert result.error_type == "EmptyResponse"


def test_measure_socket_timeout():
    client = AmmeterClient(port=5000, command=b"TEST")
    with patch("socket.socket") as mock_socket:
        mock_sock_instance = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_sock_instance
        # Simulate timeout
        mock_sock_instance.recv.side_effect = socket.timeout("timeout")

        result = client.measure()
        assert result.success is False
        assert result.error_type == "TimeoutError"


def test_measure_connection_refused():
    client = AmmeterClient(port=5000, command=b"TEST")
    with patch("socket.socket") as mock_socket:
        mock_sock_instance = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_sock_instance
        mock_sock_instance.connect.side_effect = ConnectionRefusedError("refused")

        result = client.measure()
        assert result.success is False
        assert result.error_type == "ConnectionError"


def test_measure_parse_error():
    client = AmmeterClient(port=5000, command=b"TEST")
    with patch("socket.socket") as mock_socket:
        mock_sock_instance = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_sock_instance
        mock_sock_instance.recv.return_value = b"NOT_A_FLOAT"

        result = client.measure()
        assert result.success is False
        assert result.error_type == "ParseError"


def test_measure_generic_exception():
    client = AmmeterClient(port=5000, command=b"TEST")
    with patch("socket.socket") as mock_socket:
        mock_sock_instance = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_sock_instance
        mock_sock_instance.recv.side_effect = RuntimeError("Something bad")

        result = client.measure()
        assert result.success is False
        assert result.error_type == "RuntimeError"
