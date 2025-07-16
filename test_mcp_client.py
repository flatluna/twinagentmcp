"""
Simple standalone MCP client to test the MCP server.
This script demonstrates how to communicate with the MCP server directly
without requiring AutoGen dependencies.
"""

import json
import subprocess
import asyncio
import sys


class SimpleMCPClient:
    """A simple MCP client to test our server."""
    
    def __init__(self, server_command: list):
        self.server_command = server_command
        self.process = None
    
    async def start_server(self):
        """Start the MCP server process."""
        self.process = await asyncio.create_subprocess_exec(
            *self.server_command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        print("✅ MCP Server started")
    
    async def send_request(self, request: dict) -> dict:
        """Send a JSON-RPC request to the server."""
        if not self.process:
            raise RuntimeError("Server not started")
        
        # Send request
        request_json = json.dumps(request) + "\n"
        self.process.stdin.write(request_json.encode())
        await self.process.stdin.drain()
        
        # Read response
        response_line = await self.process.stdout.readline()
        response = json.loads(response_line.decode().strip())
        
        return response
    
    async def initialize(self):
        """Initialize the MCP connection."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "simple-mcp-client",
                    "version": "1.0.0"
                }
            }
        }
        
        response = await self.send_request(request)
        print(f"🔧 Initialization response: {response['result']['serverInfo']['name']}")
        return response
    
    async def list_tools(self):
        """List available tools from the server."""
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        response = await self.send_request(request)
        tools = response['result']['tools']
        print(f"🛠️  Available tools: {[tool['name'] for tool in tools]}")
        return tools
    
    async def call_hello_world(self, name: str = "World"):
        """Call the hello_world tool."""
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "hello_world",
                "arguments": {
                    "name": name
                }
            }
        }
        
        response = await self.send_request(request)
        result = response['result']['content'][0]['text']
        print(f"📝 Hello World Response: {result}")
        return result
    
    async def call_add_numbers(self, a: float, b: float):
        """Call the add_numbers tool."""
        request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "add_numbers",
                "arguments": {
                    "a": a,
                    "b": b
                }
            }
        }
        
        response = await self.send_request(request)
        result = response['result']['content'][0]['text']
        print(f"🔢 Math Response: {result}")
        return result
    
    async def stop_server(self):
        """Stop the MCP server process."""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            print("🛑 MCP Server stopped")


async def main():
    """Main function to demonstrate MCP client-server interaction."""
    print("🚀 Starting Simple MCP Demo")
    print("=" * 50)
    
    # Create client
    client = SimpleMCPClient(["python", "simple_mcp_server.py"])
    
    try:
        # Start server
        await client.start_server()
        
        # Initialize connection
        await client.initialize()
        
        # List available tools
        await client.list_tools()
        
        # Test the hello_world tool with different names
        print("\n🧪 Testing Hello World Tool:")
        print("-" * 30)
        
        await client.call_hello_world()  # Default "World"
        await client.call_hello_world("Alice")
        await client.call_hello_world("Bob")
        await client.call_hello_world("MCP User")
        
        # Test the add_numbers tool with different numbers
        print("\n🔢 Testing Math Tool:")
        print("-" * 30)
        
        await client.call_add_numbers(5, 3)
        await client.call_add_numbers(15.5, 24.7)
        await client.call_add_numbers(100, 200)
        await client.call_add_numbers(-10, 25)
        
        print("\n✅ Demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")
    
    finally:
        # Clean up
        await client.stop_server()


if __name__ == "__main__":
    asyncio.run(main())
