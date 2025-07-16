"""
Test what the MCP tools actually look like and how to call them.
"""

import asyncio
from autogen_ext.tools.mcp import SseServerParams, mcp_server_tools
from dotenv import load_dotenv

load_dotenv()

async def inspect_mcp_tools():
    print("🔍 Inspecting MCP Tools")
    print("=" * 40)
    
    server_params = SseServerParams(
        url="http://localhost:8000/sse",
        headers={"x-api-key": "test123"}
    )
    
    mcp_tools = await mcp_server_tools(server_params)
    
    print(f"Number of tools: {len(mcp_tools)}")
    
    for tool in mcp_tools:
        print(f"\n📋 Tool: {tool.name}")
        print(f"   Type: {type(tool)}")
        print(f"   Description: {tool.description}")
        print(f"   Methods: {[method for method in dir(tool) if not method.startswith('_')]}")
        
        # Check if it has args_type
        if hasattr(tool, 'args_type'):
            print(f"   Args type: {tool.args_type}")
        
        # Check if it has input_schema
        if hasattr(tool, 'input_schema'):
            print(f"   Input schema: {tool.input_schema}")

if __name__ == "__main__":
    asyncio.run(inspect_mcp_tools())
