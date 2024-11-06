from fastapi import FastAPI, Request,HTTPException
from fastapi.responses import JSONResponse
from time import time
from typing import Dict, List
rate_limits: Dict[str, List[float]] = {}
limit = 5  # Max requests/messages
window = 10  # Time window in seconds

import logging
from time import time
rate_limits = {}
class RateLimitMiddleware:
    def __init__(self, app: FastAPI):
        self.app = app
        self.limit = 5
        self.window = 10

    async def __call__(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time()

        if client_ip not in rate_limits:
            rate_limits[client_ip] = []

        # Clean up old timestamps
        rate_limits[client_ip] = [t for t in rate_limits[client_ip] if current_time - t < self.window]

        if len(rate_limits[client_ip]) >= self.limit:
            
            return JSONResponse(status_code=429, content={"message": "Too Many Requests"})

        # Adding new timestamp
        rate_limits[client_ip].append(current_time)
        response = await call_next(request)
        return response

async def rate_limit(client_ip: str):
    current_time = time()
    print("message1")
    if client_ip not in rate_limits:
        rate_limits[client_ip] = []

    rate_limits[client_ip] = [t for t in rate_limits[client_ip] if current_time - t < window]

    if len(rate_limits[client_ip]) >= limit:
        return False  # Rate limit exceeded

    rate_limits[client_ip].append(current_time)
    return True  # Within limits
