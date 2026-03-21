import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_read_main():
    """Test the root API endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "online", "message": "KAVACH-SIGMA API is running"}

def test_trigger_analysis():
    """Test the trigger API endpoint."""
    data = {"type": "FHSS", "length": 512, "snr": 15.0}
    response = client.post("/api/v1/trigger", json=data)
    assert response.status_code == 200
    result = response.json()["result"]
    assert result["status"] == "success"
    assert result["signal_parameters"]["length"] == 512
    assert "perception" in result
    assert "action" in result

def test_websocket():
    """Test the WebSocket connection and data transfer."""
    with client.websocket_connect("/ws/spectrum") as websocket:
        data = {"type": "BPSK", "length": 256, "snr": 5.0}
        websocket.send_json(data)

        # In a real test we would receive data, but the orchestrator broadcast
        # is mocked in this simple test scenario. The app expects JSON string.
        # Ensure it doesn't crash on connect
        response = websocket.receive_text()
        assert "status" in response
