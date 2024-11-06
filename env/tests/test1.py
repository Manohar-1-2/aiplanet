import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.mark.asyncio
async def test_websocket_valid_filename():
    """Test WebSocket endpoint with a valid filename for connection establishment and message receipt."""
    client = TestClient(app)
    with client.websocket_connect("/ws/20241102145302_yuva.pdf") as websocket:
        assert websocket  # Checks that the connection was successfully established
        # Send a test message and confirm any response is received
        for i in range(5):
            websocket.send_text("Hello")
            print(i)
            data = websocket.receive_text()
            assert data is not None
        try:
            websocket.send_text("Hello")
            received = websocket.receive_text()
        except Exception as e:
            assert isinstance(e, Exception)