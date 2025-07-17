#!/usr/bin/env python3
"""
Simple MCP Server that provides a Hello World tool.
This server demonstrates the basic structure of an MCP server
following the Model Context Protocol specification.
"""

import json
import sys
from typing import Any, Dict, List
import asyncio
from datetime import datetime
import os
try:
    from azure.cosmos import CosmosClient, PartitionKey
    from azure.cosmos.exceptions import CosmosResourceExistsError, CosmosResourceNotFoundError
    COSMOS_AVAILABLE = True
except ImportError:
    COSMOS_AVAILABLE = False


class SimpleMCPServer:
    """A simple MCP server that provides a hello world tool."""
    
    def __init__(self):
        self.cosmos_client = None
        self.database = None
        self.container = None
        self._initialize_cosmos_db()
        
        self.tools = {
            "hello_world": {
                "name": "hello_world",
                "description": "A simple tool that responds with a hello world message",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "The name to greet (optional)",
                            "default": "World"
                        }
                    }
                }
            },
            "add_numbers": {
                "name": "add_numbers",
                "description": "Add two numbers together and return the result",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "a": {
                            "type": "number",
                            "description": "The first number to add"
                        },
                        "b": {
                            "type": "number",
                            "description": "The second number to add"
                        }
                    },
                    "required": ["a", "b"]
                }
            },
            "getdatetime": {
                "name": "getdatetime",
                "description": "Get the current date and time",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "format": {
                            "type": "string",
                            "description": "Optional format for the datetime (e.g., 'iso', 'readable')",
                            "default": "readable"
                        }
                    }
                }
            },
            "save_twin_info": {
                "name": "save_twin_info",
                "description": "Save Twin information to Cosmos DB",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "firstName": {
                            "type": "string",
                            "description": "The first name of the Twin"
                        },
                        "lastName": {
                            "type": "string",
                            "description": "The last name of the Twin"
                        },
                        "email": {
                            "type": "string",
                            "description": "The email address of the Twin (used as ID)"
                        },
                        "telephoneNumber": {
                            "type": "string",
                            "description": "The telephone number of the Twin"
                        },
                        "countryId": {
                            "type": "string",
                            "description": "The country ID for partitioning"
                        }
                    },
                    "required": ["firstName", "lastName", "email", "telephoneNumber", "countryId"]
                }
            }
        }
    
    def _initialize_cosmos_db(self):
        """Initialize Cosmos DB client and database/container."""
        if not COSMOS_AVAILABLE:
            print("Warning: Azure Cosmos DB SDK not available. Twin storage functionality disabled.", file=sys.stderr)
            return
            
        try:
            # Get Cosmos DB configuration from environment variables
            cosmos_endpoint = os.getenv("COSMOS_ENDPOINT")
            cosmos_key = os.getenv("COSMOS_KEY")
            
            if not cosmos_endpoint or not cosmos_key:
                print("Warning: COSMOS_ENDPOINT and COSMOS_KEY environment variables not set. Twin storage functionality disabled.", file=sys.stderr)
                return
                
            # Initialize the Cosmos client
            self.cosmos_client = CosmosClient(cosmos_endpoint, cosmos_key)
            
            # Create database if it doesn't exist
            database_name = "TwinHumanDB"
            try:
                self.database = self.cosmos_client.create_database(id=database_name)
            except CosmosResourceExistsError:
                self.database = self.cosmos_client.get_database_client(database_name)
            
            # Create container if it doesn't exist
            container_name = "TwinHumanContainer"
            try:
                # Don't set throughput for serverless accounts
                self.container = self.database.create_container(
                    id=container_name,
                    partition_key=PartitionKey(path="/CountryID")
                )
            except CosmosResourceExistsError:
                self.container = self.database.get_container_client(container_name)
                
            print("Successfully initialized Cosmos DB for Twin storage.", file=sys.stderr)
            
        except Exception as e:
            print(f"Failed to initialize Cosmos DB: {str(e)}", file=sys.stderr)
            self.cosmos_client = None
            self.database = None
            self.container = None
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP requests."""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "simple-hello-mcp-server",
                        "version": "1.0.0"
                    }
                }
            }
        
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": list(self.tools.values())
                }
            }
        
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if tool_name == "hello_world":
                name = arguments.get("name", "World")
                response_text = f"Hello, {name}! This is a response from the MCP server."
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": response_text
                            }
                        ]
                    }
                }
            
            elif tool_name == "add_numbers":
                # Extract the numbers to add
                a = arguments.get("a", 0)
                b = arguments.get("b", 0)
                
                # Perform the addition
                result = a + b
                response_text = f"The sum of {a} + {b} = {result}"
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": response_text
                            }
                        ]
                    }
                }
            
            elif tool_name == "getdatetime":
                # Get the format preference
                format_type = arguments.get("format", "readable")
                
                # Get current datetime
                now = datetime.now()
                
                if format_type == "iso":
                    result_text = now.isoformat()
                else:  # readable format
                    result_text = now.strftime("%A, %B %d, %Y at %I:%M:%S %p")
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Current date and time: {result_text}"
                            }
                        ]
                    }
                }
            
            elif tool_name == "save_twin_info":
                # Check if Cosmos DB is available
                if not self.container:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
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
                            "id": request_id,
                            "error": {
                                "code": -32602,
                                "message": "Missing required fields: firstName, lastName, email, telephoneNumber, countryId"
                            }
                        }
                    
                    # Create Twin document with proper structure
                    twin_document = {
                        "id": email,  # Use email as the unique ID
                        "CountryID": countryId,  # Partition key
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
                    response = self.container.upsert_item(body=twin_document)
                    
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Successfully saved Twin information for {firstName} {lastName} (ID: {email}) in country {countryId}"
                                }
                            ]
                        }
                    }
                    
                except Exception as e:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32603,
                            "message": f"Failed to save Twin information: {str(e)}"
                        }
                    }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Unknown tool: {tool_name}"
                    }
                }
        
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Unknown method: {method}"
                }
            }
    
    async def run(self):
        """Run the MCP server using stdio."""
        while True:
            try:
                # Read from stdin
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                
                if not line:
                    break
                
                # Parse the JSON-RPC request
                try:
                    request = json.loads(line.strip())
                except json.JSONDecodeError:
                    continue
                
                # Handle the request
                response = await self.handle_request(request)
                
                # Send response to stdout
                print(json.dumps(response), flush=True)
                
            except Exception as e:
                # Send error response
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)


async def main():
    """Main entry point for the MCP server."""
    server = SimpleMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
