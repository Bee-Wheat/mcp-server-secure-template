# mcp-server-secure-template
# Secure MCP (Model Context Proxy) server for AI agent integrations

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
import uvicorn
import os
import logging
import time
from typing import List

# Configuration
API_KEY = os.getenv("MCP_API_KEY", "changeme123")
ALLOWED_TOOLS = {"search", "calculator"}  # Define safe tools only

# Rate limiting (simple in-memory)
RATE_LIMIT = {}
MAX_REQUESTS = 10
WINDOW = 60  # seconds

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# FastAPI app
app = FastAPI()
api_key_header = APIKeyHeader(name="X-API-Key")

# Request Models
class AgentRequest(BaseModel):
    tool: str
    input: str

class AgentResponse(BaseModel):
    result: str

# Rate limit check
async def check_rate_limit(request: Request):
    ip = request.client.host
    now = time.time()
    RATE_LIMIT.setdefault(ip, []).append(now)
    RATE_LIMIT[ip] = [t for t in RATE_LIMIT[ip] if now - t < WINDOW]
    if len(RATE_LIMIT[ip]) > MAX_REQUESTS:
        logging.warning(f"Rate limit exceeded for {ip}")
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

# Auth check
async def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return api_key

# Main endpoint
@app.post("/agent", response_model=AgentResponse)
async def process_agent(request: Request, payload: AgentRequest, api_key: str = Depends(get_api_key)):
    await check_rate_limit(request)
    logging.info(f"Request from {request.client.host}: tool={payload.tool}, input={payload.input}")

    if payload.tool not in ALLOWED_TOOLS:
        raise HTTPException(status_code=400, detail="Tool not allowed")

    # Tool simulation
    if payload.tool == "search":
        result = f"Search results for: {payload.input}"
    elif payload.tool == "calculator":
        try:
            result = str(eval(payload.input, {"__builtins__": {}}))
        except Exception as e:
            result = f"Calculation error: {e}"
    else:
        result = "Invalid tool"

    return AgentResponse(result=result)

# Healthcheck
@app.get("/health")
async def health():
    return {"status": "ok"}

# Entry
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, ssl_keyfile="key.pem", ssl_certfile="cert.pem")
