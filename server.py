"""
Wrapper server: serves the chat UI at / and the ADK agent API at /run
"""
import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

# Boot the ADK app
from google.adk.cli.fast_api import get_fast_api_app

# ADK mounts all agent routes including /run
adk_app = get_fast_api_app(
    agents_dir=str(Path(__file__).parent),
    web=False,
    allow_origins=["*"],
)

# Serve the chat UI at root
@adk_app.get("/", response_class=HTMLResponse)
async def index():
    html = Path("static/index.html").read_text(encoding="utf-8")
    return HTMLResponse(content=html)

app = adk_app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("server:app", host="0.0.0.0", port=port)
