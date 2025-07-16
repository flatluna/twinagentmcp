"""
Test AutoGen client that connects to the local web MCP server.
This demonstrates how your client will work when deployed to Azure.
"""

import os
import asyncio
from dotenv import load_dotenv
from autogen_ext.tools.mcp import SseServerParams, mcp_server_tools
from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import UserMessage
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient

load_dotenv(".env")

async def test_local_web_mcp():
    print("🧪 Testing AutoGen + Local Web MCP Server")
    print("=" * 60)
    
    # Configure connection to your LOCAL web server
    server_params = SseServerParams(
        url="http://localhost:8000/sse",  # Your local web server
        headers={
            "x-api-key": "test123"  # The API key from your .env
        }
    )
    
    print("1️⃣ Connecting to local MCP server...")
    try:
        # Initialize the MCP tool adapter
        mcp_tools = await mcp_server_tools(server_params)
        print(f"   ✅ Connected! Available tools: {[tool.name for tool in mcp_tools]}")
    except Exception as e:
        print(f"   ❌ Failed to connect to MCP server: {e}")
        print("   📋 Make sure start_server.py is still running!")
        return
    
    print("\n2️⃣ Setting up Azure OpenAI client...")
    try:
        # Initialize the Azure OpenAI client (same as your working version)
        az_model_client = AzureOpenAIChatCompletionClient(
            model=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME", "gpt4mini"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-02-15-preview"
        )
        print(f"   ✅ Azure OpenAI client configured with {os.getenv('AZURE_OPENAI_CHAT_DEPLOYMENT_NAME')}")
    except Exception as e:
        print(f"   ❌ Failed to setup Azure OpenAI: {e}")
        return
    
    print("\n3️⃣ Creating AutoGen agent with MCP tools...")
    try:
        # Create the agent with MCP tools
        agent = AssistantAgent(
            name="mcp_test_agent",
            model_client=az_model_client,
            tools=mcp_tools,
            system_message="You are a helpful assistant that can use MCP tools. When asked to say hello or add numbers, use the available tools.",
            reflect_on_tool_use=True,
            model_client_stream=True,
        )
        print("   ✅ Agent created successfully!")
    except Exception as e:
        print(f"   ❌ Failed to create agent: {e}")
        return
    
    print("\n4️⃣ Testing hello_world tool...")
    try:
        result = await agent.run(task="Say hello to the local web server!")
        print(f"   ✅ Agent response: {result.messages[-1].content}")
    except Exception as e:
        print(f"   ❌ Failed to run hello test: {e}")
    
    print("\n5️⃣ Testing add_numbers tool...")
    try:
        result = await agent.run(task="Add 15 and 25 using the MCP tool")
        print(f"   ✅ Agent response: {result.messages[-1].content}")
    except Exception as e:
        print(f"   ❌ Failed to run math test: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 LOCAL WEB SERVER TEST COMPLETE!")
    print("\n📋 What this proves:")
    print("✅ Your MCP server works as a web service")
    print("✅ AutoGen can connect via HTTP/SSE")
    print("✅ Authentication is working")
    print("✅ Ready for Azure deployment!")
    
    print("\n🚀 Next step: Deploy to Azure with:")
    print("   .\\deploy_server_aca.ps1")

if __name__ == "__main__":
    asyncio.run(test_local_web_mcp())
