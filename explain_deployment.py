"""
Simple test to demonstrate the difference between:
1. Direct MCP server (stdio communication)
2. Web-wrapped MCP server (HTTP communication)
"""

import asyncio
import json
import subprocess
import time
import requests
from simple_mcp_server import SimpleMCPServer

async def test_direct_mcp():
    """Test the MCP server directly (how it works locally)"""
    print("🔹 Testing Direct MCP Server (stdio)...")
    
    server = SimpleMCPServer()
    
    # Simulate a client request
    request = {
        "jsonrpc": "2.0",
        "id": "test",
        "method": "tools/call",
        "params": {
            "name": "hello_world",
            "arguments": {"name": "Direct Test"}
        }
    }
    
    response = await server.handle_request(request)
    print(f"✅ Direct response: {response['result']['content'][0]['text']}")

def test_web_mcp():
    """Test the web-wrapped MCP server (how it works on Azure)"""
    print("\n🔹 Testing Web MCP Server (HTTP)...")
    print("ℹ️  This requires start_server.py to be running...")
    
    # This would work if the web server was running
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        print(f"✅ Web server is running: {response.json()}")
        
        # Test the actual MCP endpoint
        mcp_request = {
            "jsonrpc": "2.0",
            "id": "web_test",
            "method": "tools/call",
            "params": {
                "name": "hello_world",
                "arguments": {"name": "Web Test"}
            }
        }
        
        # Note: This would need proper authentication in real deployment
        print("ℹ️  To test MCP endpoint, you'd need API key authentication")
        
    except requests.exceptions.ConnectionError:
        print("❌ Web server is not running")
        print("   To start it: python start_server.py")

async def main():
    print("🚀 MCP Server Deployment Demo\n")
    
    print("="*50)
    print("UNDERSTANDING THE COMPONENTS:")
    print("="*50)
    
    print("""
📁 simple_mcp_server.py
   └── Your core MCP logic (hello_world, add_numbers)
   └── Works with stdin/stdout (terminal communication)
   └── ✅ Perfect for local testing

📁 start_server.py  
   └── Web wrapper around simple_mcp_server.py
   └── Provides HTTP endpoints (/sse, /health)
   └── Handles API key authentication
   └── ✅ Required for Azure deployment

📁 Dockerfile
   └── Instructions to package everything into a container
   └── ✅ Required for Azure Container Apps

📁 deploy_server_aca.ps1
   └── Script to deploy to Azure
   └── ✅ Automates the deployment process
""")
    
    print("="*50)
    print("TESTING:")
    print("="*50)
    
    # Test direct MCP
    await test_direct_mcp()
    
    # Test web MCP
    test_web_mcp()
    
    print("\n" + "="*50)
    print("NEXT STEPS FOR DEPLOYMENT:")
    print("="*50)
    print("""
1. Set up environment:
   📝 Copy sample.env to .env
   📝 Add your API keys
   
2. Test locally:
   🔧 pip install -r requirements.txt
   🔧 python start_server.py
   🔧 Visit http://localhost:8000/health
   
3. Deploy to Azure:
   ☁️  Run: ./deploy_server_aca.ps1
   ☁️  Use the generated API key and URL in your client
""")

if __name__ == "__main__":
    asyncio.run(main())
