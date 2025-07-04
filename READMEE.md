# 🛡️ MCP Server Secure Template

This is a secure FastAPI-based MCP (Model Context Proxy) server for safely connecting LLM agents to real-world tools.

## 🔐 Features

- API key authentication
- IP-based rate limiting
- Tool whitelisting (e.g. search, calculator)
- TLS support
- Logging and healthcheck

## 🚀 How to Run

```bash
export MCP_API_KEY="your-secret-key"
uvicorn main:app --host 0.0.0.0 --port 8000 --ssl-keyfile key.pem --ssl-certfile cert.pem
