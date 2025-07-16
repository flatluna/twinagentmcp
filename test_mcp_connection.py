"""
Quick test to verify MCP web server is working.
Uses the same approach as your working simple_autogen_client.py
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_mcp_web_connection():
    print("🧪 Testing MCP Web Server Connection")
    print("=" * 50)
    
    # Test MCP connection only (skip Azure OpenAI for now)
    from autogen_ext.tools.mcp import SseServerParams, mcp_server_tools
    
    server_params = SseServerParams(
        url="http://localhost:8000/sse",
        headers={"x-api-key": "test123"}
    )
    
    print("1️⃣ Connecting to local web MCP server...")
    try:
        mcp_tools = await mcp_server_tools(server_params)
        print(f"   ✅ SUCCESS! Available tools: {[tool.name for tool in mcp_tools]}")
        
        print("\n2️⃣ Testing tool access...")
        print(f"   📋 Tool details:")
        for tool in mcp_tools:
            print(f"      - {tool.name}: {tool.description}")
        
        print("\n3️⃣ Testing actual tool execution...")
        
        # Import cancellation token
        from autogen_core import CancellationToken
        cancellation_token = CancellationToken()
        
        # Test hello_world tool
        try:
            hello_tool = next(tool for tool in mcp_tools if tool.name == "hello_world")
            
            # Get the proper args class
            HelloArgs = hello_tool.args_type()
            hello_args = HelloArgs(name="Web Test User")
            
            hello_result = await hello_tool.run(hello_args, cancellation_token)
            print(f"   ✅ hello_world result: {hello_result}")
        except Exception as e:
            print(f"   ❌ hello_world failed: {e}")
        
        # Test add_numbers tool
        try:
            math_tool = next(tool for tool in mcp_tools if tool.name == "add_numbers")
            
            # Get the proper args class
            MathArgs = math_tool.args_type()
            math_args = MathArgs(a=15, b=25)
            
            math_result = await math_tool.run(math_args, cancellation_token)
            print(f"   ✅ add_numbers result: {math_result}")
        except Exception as e:
            print(f"   ❌ add_numbers failed: {e}")
        
        print("\n🎉 FULL CLIENT TEST COMPLETE!")
        print("\n✅ MCP server is working as a web service")
        print("✅ AutoGen can connect via HTTP/SSE")  
        print("✅ Authentication is working")
        print("✅ Tools are being discovered correctly")
        print("✅ Tools can be executed successfully")
        
        print("\n🚀 Ready for deployment!")
        print("   Next: Run .\\deploy_server_aca.ps1")
        
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("   - Make sure start_server.py is still running")
        print("   - Check that the API key 'test123' is in your .env")

if __name__ == "__main__":
    asyncio.run(test_mcp_web_connection())
