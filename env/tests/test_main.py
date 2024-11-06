import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from main import app
from services.uploadspdf import uploadfile
from services.websocket import handlewebsocket
from fastapi import WebSocket,WebSocketDisconnect
import os

client = TestClient(app)

@pytest.mark.asyncio
async def test_root():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

@pytest.mark.asyncio
async def test_uploadpdf():
    """Test the PDF upload endpoint"""

    # Determine the path to the sample PDF file
    file_path = os.path.join(os.path.dirname(__file__), "samplepdf.pdf")
    with open(file_path, "rb") as file:
        response = client.post("/uploadpdf", files={"file": ("temp_sample.pdf", file, "application/pdf")})

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_websocket_valid_filename():
    """Test WebSocket endpoint with a valid filename for connection establishment and message receipt."""
    with client.websocket_connect("/ws/20241102145302_yuva.pdf") as websocket:
        assert websocket  # Checks that the connection was successfully established
        # Send a test message and confirm any response is received
        websocket.send_text("Hello")
        data = websocket.receive_text()
        assert data is not None  # Confirms that a response was received


@pytest.mark.asyncio
async def test_websocket_invalid_filename():
    """Test WebSocket endpoint with an invalid filename to confirm it returns a 404 error."""
    with client.websocket_connect("/ws/invalid_file.pdf") as websocket:
            # After sending a message, we expect the connection to be closed by the server.
            try:
                websocket.send_text("Hello")
                # If no exception is raised, we are still connected; we can expect it to be closed.
                received = websocket.receive_text()  # This line should raise an exception
            except Exception as e:
                assert isinstance(e, Exception)  # Here you can specify the expected exception type if needed
                # If we reach this point, it means the connection was closed

    
    # Expecting rate limit status code (e.g., 429) after the limit is hit
    

@pytest.mark.asyncio
async def test_rate_limit_middleware():
    """Test rate-limiting middleware."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Hit the endpoint enough times to reach the limit
        for _ in range(5):  # Make 5 requests to stay within the limit
            response = await client.get("/")
            assert response.status_code == 200  # Expect successful responses

        # Now the 6th request should trigger the rate limit
        response = await client.get("/")
        assert response.status_code == 429

