"""
Proper MCP client for cloud server using HTTP transport
"""

import asyncio
import json
import httpx
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters
import os

# Cloud MCP server configuration
MCP_SERVER_URL = "https://twinagentservices.politepond-2f6f686d.eastus.azurecontainerapps.io"
MCP_API_KEY = "B509918774DDE22A5BF94EDB4F145CB6E06F1CBCCC49D492D27FFD4AC3667A71"

async def test_cloud_mcp_direct():
    """Test cloud MCP server with direct HTTP requests"""
    print("🌐 Testing Cloud MCP Server - Direct HTTP Method")
    print("=" * 60)
    
    headers = {
        "x-api-key": MCP_API_KEY,
        "Content-Type": "application/json",
        "Accept": "text/event-stream"
    }
    
    # Test health first
    async with httpx.AsyncClient() as client:
        print("🔍 Testing health endpoint...")
        health_response = await client.get(f"{MCP_SERVER_URL}/health")
        print(f"✅ Health: {health_response.status_code} - {health_response.json()}")
        
        print("\n🔧 Testing MCP initialization...")
        
        # MCP Initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"roots": {"listChanged": True}},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }
        
        try:
            # Try the MCP endpoint with initialization
            response = await client.post(
                f"{MCP_SERVER_URL}/mcp",
                json=init_request,
                headers=headers,
                timeout=10.0
            )
            print(f"📡 Initialize Status: {response.status_code}")
            print(f"📄 Response: {response.json()}")
            
        except Exception as e:
            print(f"❌ MCP request failed: {e}")
            
        print("\n🛠️ Testing tools/list request...")
        
        # List available tools
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        try:
            response = await client.post(
                f"{MCP_SERVER_URL}/mcp",
                json=tools_request,
                headers=headers,
                timeout=10.0
            )
            print(f"📡 Tools list Status: {response.status_code}")
            print(f"📄 Response: {response.json()}")
            
            # If tools list worked, test calling hello_world
            if response.status_code == 200:
                print("\n🎉 Testing hello_world function...")
                hello_request = {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {
                        "name": "hello_world",
                        "arguments": {}
                    }
                }
                
                hello_response = await client.post(
                    f"{MCP_SERVER_URL}/mcp",
                    json=hello_request,
                    headers=headers,
                    timeout=10.0
                )
                print(f"📡 Hello Status: {hello_response.status_code}")
                print(f"📄 Hello Response: {hello_response.json()}")
                
                print("\n🧮 Testing add_numbers function...")
                add_request = {
                    "jsonrpc": "2.0",
                    "id": 4,
                    "method": "tools/call",
                    "params": {
                        "name": "add_numbers",
                        "arguments": {"a": 15, "b": 27}
                    }
                }
                
                add_response = await client.post(
                    f"{MCP_SERVER_URL}/mcp",
                    json=add_request,
                    headers=headers,
                    timeout=10.0
                )
                print(f"📡 Add Status: {add_response.status_code}")
                print(f"📄 Add Response: {add_response.json()}")
            
        except Exception as e:
            print(f"❌ Tools request failed: {e}")

async def test_with_curl_simulation():
    """Simulate what a working curl command would look like"""
    print("\n" + "=" * 60)
    print("📋 Equivalent curl commands that should work:")
    print("=" * 60)
    
    print(f"""
1. Health Check:
curl -X GET {MCP_SERVER_URL}/health

2. Initialize MCP:
curl -X POST {MCP_SERVER_URL}/mcp \\
  -H "x-api-key: {MCP_API_KEY}" \\
  -H "Content-Type: application/json" \\
  -d '{{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {{"protocolVersion": "2024-11-05", "capabilities": {{}}, "clientInfo": {{"name": "test", "version": "1.0"}}}}}}'

3. List Tools:
curl -X POST {MCP_SERVER_URL}/mcp \\
  -H "x-api-key: {MCP_API_KEY}" \\
  -H "Content-Type: application/json" \\
  -d '{{"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {{}}}}'

4. Call hello_world:
curl -X POST {MCP_SERVER_URL}/mcp \\
  -H "x-api-key: {MCP_API_KEY}" \\
  -H "Content-Type: application/json" \\
  -d '{{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {{"name": "hello_world", "arguments": {{}}}}}}'

5. Call add_numbers:
curl -X POST {MCP_SERVER_URL}/mcp \\
  -H "x-api-key: {MCP_API_KEY}" \\
  -H "Content-Type: application/json" \\
  -d '{{"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {{"name": "add_numbers", "arguments": {{"a": 15, "b": 27}}}}}}'
""")

if __name__ == "__main__":
    asyncio.run(test_cloud_mcp_direct())
    asyncio.run(test_with_curl_simulation())
