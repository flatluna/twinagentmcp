from fastapi import FastAPI, Request, Depends
from mcp.server.sse import SseServerTransport
from starlette.routing import Mount
from simple_mcp_server_wrapper import mcp_simple_server
from api_key_auth import ensure_valid_api_key
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import argparse
import os

app = FastAPI(docs_url=None, redoc_url=None, dependencies=[Depends(ensure_valid_api_key)])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specify ["http://localhost:3000"] if you want to be strict
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sse = SseServerTransport("/messages/")
app.router.routes.append(Mount("/messages", app=sse.handle_post_message))

@app.get("/")
async def health_check():
    """Health check endpoint."""
    return {"message": "Simple MCP Server is running", "version": "1.0.0"}

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.get("/sse", tags=["MCP"])
async def handle_sse(request: Request):
    """Handle SSE connections for MCP communication."""
    async with sse.connect_sse(request.scope, request.receive, request._send) as (
        read_stream,
        write_stream,
    ):
        init_options = mcp_simple_server.create_initialization_options()

        await mcp_simple_server.run(
            read_stream,
            write_stream,
            init_options,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start FastAPI server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to (default: 8000)")
    args = parser.parse_args()

    # Use environment variable for port if available (for Azure deployment)
    port = int(os.getenv("PORT", args.port))
    
    uvicorn.run(app, host=args.host, port=port)
