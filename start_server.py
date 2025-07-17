from fastapi import FastAPI, Request, Depends
from mcp.server.sse import SseServerTransport
from starlette.routing import Mount
from api_key_auth import ensure_valid_api_key
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import argparse
import os
from datetime import datetime

try:
    from azure.cosmos import CosmosClient, PartitionKey
    from azure.cosmos.exceptions import CosmosResourceExistsError, CosmosResourceNotFoundError
    COSMOS_AVAILABLE = True
except ImportError:
    COSMOS_AVAILABLE = False

# Create app without global API key dependency for health endpoints
app = FastAPI(docs_url=None, redoc_url=None)

# Initialize Cosmos DB
cosmos_client = None
database = None
container = None

def initialize_cosmos_db():
    """Initialize Cosmos DB client and database/container."""
    global cosmos_client, database, container
    
    if not COSMOS_AVAILABLE:
        print("Warning: Azure Cosmos DB SDK not available. Twin storage functionality disabled.")
        return
        
    try:
        # Get Cosmos DB configuration from environment variables
        cosmos_endpoint = os.getenv("COSMOS_ENDPOINT")
        cosmos_key = os.getenv("COSMOS_KEY")
        
        if not cosmos_endpoint or not cosmos_key:
            print("Warning: COSMOS_ENDPOINT and COSMOS_KEY environment variables not set. Twin storage functionality disabled.")
            return
            
        # Initialize the Cosmos client
        cosmos_client = CosmosClient(cosmos_endpoint, cosmos_key)
        
        # Create database if it doesn't exist
        database_name = "TwinHumanDB"
        try:
            database = cosmos_client.create_database(id=database_name)
        except CosmosResourceExistsError:
            database = cosmos_client.get_database_client(database_name)
        
        # Create container if it doesn't exist
        container_name = "TwinHumanContainer"
        try:
            # Don't set throughput for serverless accounts
            container = database.create_container(
                id=container_name,
                partition_key=PartitionKey(path="/CountryID")
            )
        except CosmosResourceExistsError:
            container = database.get_container_client(container_name)
            
        print("Successfully initialized Cosmos DB for Twin storage.")
        
    except Exception as e:
        print(f"Failed to initialize Cosmos DB: {str(e)}")
        cosmos_client = None
        database = None
        container = None

# Initialize Cosmos DB on startup
initialize_cosmos_db()

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
                        },
                        {
                            "name": "getdatetime",
                            "description": "Get the current date and time",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "format": {"type": "string", "description": "Format: 'iso' or 'readable'"}
                                },
                                "required": []
                            }
                        },
                        {
                            "name": "save_twin_info",
                            "description": "Save Twin information to Cosmos DB",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "firstName": {"type": "string", "description": "The first name of the Twin"},
                                    "lastName": {"type": "string", "description": "The last name of the Twin"},
                                    "email": {"type": "string", "description": "The email address of the Twin (used as ID)"},
                                    "telephoneNumber": {"type": "string", "description": "The telephone number of the Twin"},
                                    "countryId": {"type": "string", "description": "The country ID for partitioning"}
                                },
                                "required": ["firstName", "lastName", "email", "telephoneNumber", "countryId"]
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
            elif tool_name == "getdatetime":
                format_type = arguments.get("format", "readable")
                now = datetime.now()
                if format_type == "iso":
                    result_text = now.isoformat()
                else:  # readable format
                    result_text = now.strftime("%A, %B %d, %Y at %I:%M:%S %p")
                result = f"Current date and time: {result_text}"
            elif tool_name == "save_twin_info":
                # Check if Cosmos DB is available
                if not container:
                    return {
                        "jsonrpc": "2.0",
                        "id": json_data.get("id"),
                        "error": {
                            "code": -32603,
                            "message": "Cosmos DB not available. Please check configuration."
                        }
                    }
                
                try:
                    # Extract Twin information
                    firstName = arguments.get("firstName")
                    lastName = arguments.get("lastName") 
                    email = arguments.get("email")
                    telephoneNumber = arguments.get("telephoneNumber")
                    countryId = arguments.get("countryId")
                    
                    # Validate required fields
                    if not all([firstName, lastName, email, telephoneNumber, countryId]):
                        return {
                            "jsonrpc": "2.0",
                            "id": json_data.get("id"),
                            "error": {
                                "code": -32602,
                                "message": "Missing required fields: firstName, lastName, email, telephoneNumber, countryId"
                            }
                        }
                    
                    # Create Twin document with nested Profile structure
                    twin_document = {
                        "id": email,  # Use email as the unique ID
                        "CountryID": countryId,  # Use uppercase CountryID for partition key
                        "Profile": {
                            "firstName": firstName,
                            "lastName": lastName,
                            "email": email,
                            "telephoneNumber": telephoneNumber
                        },
                        "createdAt": datetime.now().isoformat(),
                        "lastModified": datetime.now().isoformat()
                    }
                    
                    # Save to Cosmos DB
                    response_doc = container.upsert_item(body=twin_document)
                    result = f"Successfully saved Twin information for {firstName} {lastName} (ID: {email}) in country {countryId}"
                    
                except Exception as e:
                    return {
                        "jsonrpc": "2.0",
                        "id": json_data.get("id"),
                        "error": {
                            "code": -32603,
                            "message": f"Failed to save Twin information: {str(e)}"
                        }
                    }
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
