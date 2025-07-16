#!/usr/bin/env python3
"""
FastAPI wrapper for the Simple MCP Server to enable HTTP/SSE communication.
This allows the MCP server to be deployed to Azure and accessed via web clients.
"""

import json
import asyncio
from typing import Any, Dict
from fastapi import FastAPI, Depends
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from simple_mcp_server import SimpleMCPServer
from api_key_auth import ensure_valid_api_key
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Simple MCP Server API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the MCP server
mcp_server = SimpleMCPServer()


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Simple MCP Server is running", "version": "1.0.0"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/sse")
async def sse_endpoint(
    request: Dict[str, Any],
    api_key: str = Depends(ensure_valid_api_key)
):
    """
    Server-Sent Events endpoint for MCP communication.
    This endpoint handles MCP requests via HTTP POST and returns streaming responses.
    """
    
    async def generate_response():
        try:
            # Handle the MCP request
            response = await mcp_server.handle_request(request)
            
            # Format as SSE
            sse_data = f"data: {json.dumps(response)}\n\n"
            yield sse_data
            
        except Exception as e:
            # Send error response in SSE format
            error_response = {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
            sse_data = f"data: {json.dumps(error_response)}\n\n"
            yield sse_data
    
    return StreamingResponse(
        generate_response(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )


@app.post("/mcp")
async def mcp_endpoint(
    request: Dict[str, Any],
    api_key: str = Depends(ensure_valid_api_key)
):
    """
    Direct MCP endpoint for JSON-RPC communication.
    This endpoint handles MCP requests and returns JSON responses directly.
    """
    try:
        response = await mcp_server.handle_request(request)
        return response
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }


@app.get("/tools")
async def list_tools(api_key: str = Depends(ensure_valid_api_key)):
    """List available tools."""
    request = {
        "jsonrpc": "2.0",
        "id": "list_tools",
        "method": "tools/list",
        "params": {}
    }
    response = await mcp_server.handle_request(request)
    return response.get("result", {})


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
