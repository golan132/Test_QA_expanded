import pytest
from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_api_run_success(mocker):
    # Mock the AmmeterTestFramework to avoid actually running tests
    mock_framework_class = mocker.patch("server.AmmeterTestFramework")
    mock_instance = mock_framework_class.return_value
    mock_instance.run_test.return_value = {"mocked": "result"}

    response = client.post(
        "/api/run",
        json={"ammeter": "greenlee", "count": 10, "duration": 5, "frequency": 2.0}
    )

    assert response.status_code == 200
    assert response.json() == {"status": "success", "executed_runs": 1}
    
    # Verify the framework was instantiated and configured correctly
    assert mock_instance.config.measurements_count == 10
    assert mock_instance.config.duration_seconds == 5
    assert mock_instance.config.sampling_frequency_hz == 2.0
    mock_instance.run_test.assert_called_once_with("greenlee")

def test_api_run_all(mocker):
    mock_framework_class = mocker.patch("server.AmmeterTestFramework")
    mock_instance = mock_framework_class.return_value

    response = client.post(
        "/api/run",
        json={"ammeter": "all"}
    )

    assert response.status_code == 200
    assert response.json() == {"status": "success", "executed_runs": 3}
    assert mock_instance.run_test.call_count == 3

def test_api_run_errors(mocker):
    mock_simulator_class = mocker.patch("server.ErrorSimulator")
    mock_instance = mock_simulator_class.return_value

    response = client.post("/api/run_errors")

    assert response.status_code == 200
    assert response.json() == {"status": "success"}
    mock_instance.run_all.assert_called_once()

def test_api_runs(mocker):
    # Mock os.walk and open to simulate reading data.json files
    mocker.patch("os.path.exists", return_value=True)
    mocker.patch("os.walk", return_value=[
        ("results/runs/mock_run", [], ["data.json"])
    ])
    
    # Mock open and json.load
    mock_open = mocker.mock_open(read_data='{"test_id": "123", "timestamp": "2026-09-08"}')
    mocker.patch("builtins.open", mock_open)
    
    response = client.get("/api/runs")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 1
    assert response.json()[0]["test_id"] == "123"

def test_api_consistency(mocker):
    mock_analyze = mocker.patch("server.ConsistencyAnalyzer.analyze_history")
    mock_analyze.return_value = {"historical_runs": 10, "mean_of_means": 5.0}

    response = client.get("/api/consistency")

    assert response.status_code == 200
    assert response.json() == {"historical_runs": 10, "mean_of_means": 5.0}
    mock_analyze.assert_called_once_with("results/runs")
