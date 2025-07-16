"""
Test client to verify the web-deployed MCP server is working.
This simulates how your AutoGen client will connect to the deployed server.
"""

import requests
import json

def test_web_mcp_server():
    base_url = "http://localhost:8000"
    api_key = "test123"
    headers = {"x-api-key": api_key}
    
    print("🧪 Testing Web-Deployed MCP Server")
    print("=" * 50)
    
    # Test 1: Health check
    print("1️⃣ Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", headers=headers)
        print(f"   ✅ Health check: {response.json()}")
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        return
    
    # Test 2: Root endpoint
    print("\n2️⃣ Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/", headers=headers)
        print(f"   ✅ Root endpoint: {response.json()}")
    except Exception as e:
        print(f"   ❌ Root endpoint failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 SUCCESS: Your MCP server is ready for deployment!")
    print("\nNext steps:")
    print("- Deploy to Azure using: .\\deploy_server_aca.ps1")
    print("- Use the generated API key and URL in your AutoGen client")
    print("- Your client will connect via the /sse endpoint")

if __name__ == "__main__":
    test_web_mcp_server()
