"""
Test MCP tool execution using the correct method.
"""

import asyncio
import json
from autogen_ext.tools.mcp import SseServerParams, mcp_server_tools
from dotenv import load_dotenv

load_dotenv()

async def test_tool_execution():
    print("🧪 Testing MCP Tool Execution")
    print("=" * 40)
    
    server_params = SseServerParams(
        url="http://localhost:8000/sse",
        headers={"x-api-key": "test123"}
    )
    
    mcp_tools = await mcp_server_tools(server_params)
    print(f"✅ Connected to MCP server with {len(mcp_tools)} tools")
    
    # Test hello_world tool
    print("\n1️⃣ Testing hello_world tool...")
    hello_tool = next(tool for tool in mcp_tools if tool.name == "hello_world")
    
    try:
        # Try run_json method
        hello_args = json.dumps({"name": "Web Test User"})
        hello_result = await hello_tool.run_json(hello_args)
        print(f"   ✅ hello_world result: {hello_result}")
    except Exception as e:
        print(f"   ❌ hello_world failed: {e}")
    
    # Test add_numbers tool  
    print("\n2️⃣ Testing add_numbers tool...")
    math_tool = next(tool for tool in mcp_tools if tool.name == "add_numbers")
    
    try:
        # Try run_json method
        math_args = json.dumps({"a": 15, "b": 25})
        math_result = await math_tool.run_json(math_args)
        print(f"   ✅ add_numbers result: {math_result}")
    except Exception as e:
        print(f"   ❌ add_numbers failed: {e}")
    
    print("\n🎉 TOOL EXECUTION TEST COMPLETE!")

if __name__ == "__main__":
    asyncio.run(test_tool_execution())
