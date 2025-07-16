from fastapi import FastAPI, Request, Depends
from mcp.server.sse import SseServerTransport
from starlette.routing import Mount
from simple_mcp_server_wrapper import mcp_simple_server
from api_key_auth import ensure_valid_api_key
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import argparse
import os

# Create app without global API key dependency for health endpoints
app = FastAPI(docs_url=None, redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specify ["http://localhost:3000"] if you want to be strict
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sse = SseServerTransport("/sse/")
app.router.routes.append(Mount("/sse", app=sse.handle_post_message))

@app.get("/")
async def health_check():
    """Health check endpoint."""
    return {"message": "Simple MCP Server is running", "version": "1.0.0"}

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "api_keys_configured": bool(os.getenv("API_KEYS"))}

@app.post("/mcp", tags=["MCP"])
async def handle_mcp_post(request: Request):
    """Handle MCP JSON-RPC requests via POST."""
    # Validate API key
    ensure_valid_api_key(request)
    
    # Get the JSON-RPC request
    try:
        json_data = await request.json()
        print(f"📨 Received MCP request: {json_data}")
        
        # Create a simple response for testing
        if json_data.get("method") == "initialize":
            response = {
                "jsonrpc": "2.0",
                "id": json_data.get("id"),
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {"listChanged": True}
                    },
                    "serverInfo": {
                        "name": "simple-mcp-server",
                        "version": "1.0.0"
                    }
                }
            }
            return response
            
        elif json_data.get("method") == "tools/list":
            response = {
                "jsonrpc": "2.0", 
                "id": json_data.get("id"),
                "result": {
                    "tools": [
                        {
                            "name": "hello_world",
                            "description": "Says hello to the world",
                            "inputSchema": {
                                "type": "object",
                                "properties": {},
                                "required": []
                            }
                        },
                        {
                            "name": "add_numbers", 
                            "description": "Add two numbers together",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "a": {"type": "number", "description": "First number"},
                                    "b": {"type": "number", "description": "Second number"}
                                },
                                "required": ["a", "b"]
                            }
                        }
                    ]
                }
            }
            return response
            
        elif json_data.get("method") == "tools/call":
            tool_name = json_data.get("params", {}).get("name")
            arguments = json_data.get("params", {}).get("arguments", {})
            
            if tool_name == "hello_world":
                result = "Hello, World! This is your MCP server running on Azure! 🌟"
            elif tool_name == "add_numbers":
                a = arguments.get("a", 0)
                b = arguments.get("b", 0)
                result = f"The sum of {a} + {b} = {a + b}"
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": json_data.get("id"),
                    "error": {
                        "code": -32601,
                        "message": f"Unknown tool: {tool_name}"
                    }
                }
            
            response = {
                "jsonrpc": "2.0",
                "id": json_data.get("id"),
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                }
            }
            return response
            
        else:
            return {
                "jsonrpc": "2.0",
                "id": json_data.get("id"),
                "error": {
                    "code": -32601,
                    "message": f"Unknown method: {json_data.get('method')}"
                }
            }
            
    except Exception as e:
        print(f"❌ Error processing MCP request: {e}")
        return {
            "jsonrpc": "2.0",
            "id": json_data.get("id") if 'json_data' in locals() else None,
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start FastAPI server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to (default: 8000)")
    args = parser.parse_args()

    # Use environment variable for port if available (for Azure deployment)
    # Azure Container Apps can use different environment variables for port
    port = int(os.getenv("PORT", os.getenv("WEBSITES_PORT", args.port)))
    
    print(f"Starting server on {args.host}:{port}")
    uvicorn.run(app, host=args.host, port=port)
