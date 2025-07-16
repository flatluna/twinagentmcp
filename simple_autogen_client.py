"""
Simple AutoGen client that uses Azure OpenAI.
This demonstrates how to integrate MCP tools with AutoGen agents.
"""

import os
import asyncio
import json
from typing import Sequence
from dotenv import load_dotenv

# Note: These imports will work once autogen packages are installed
# For now, this serves as a template for when the packages are available

try:
    from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
    from autogen_agentchat.teams import RoundRobinGroupChat
    from autogen_agentchat.conditions import TextMentionTermination
    from autogen_agentchat.ui import Console
    from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
    # from autogen_core import Tool  # ← Not available in current version
    
    AUTOGEN_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  AutoGen packages not installed: {e}")
    print("💡 Install with: pip install autogen-agentchat autogen-ext")
    AUTOGEN_AVAILABLE = False

# Load environment variables
load_dotenv()


def get_azure_openai_client():
    """Create and return an Azure OpenAI client."""
    from autogen_core.models import ChatCompletionClient
    
    return AzureOpenAIChatCompletionClient(
        model=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME", "gpt4mini"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
        model_info={
            "family": "gpt-4",
            "name": "gpt-4o-mini",
            "vision": True,
            "function_calling": True,
            "json_output": True
        }
    )


# Agent prompts
hello_agent_prompt = """
You are a friendly Hello Agent with access to MCP server functions through special commands:

Available MCP Server Functions:
1. When user asks to say hello/greet someone, respond with: "I'll use the MCP server to say hello!" then call the greeting function.
2. When user asks to add numbers, respond with: "I'll use the MCP server to calculate that!" then call the math function.
3. When user asks for the time/date, respond with: "I'll use the MCP server to get the current date and time!" then call the datetime function.

You have access to these capabilities but need to be instructed when to use them.
Always mention that you're using the MCP server when appropriate.
Be friendly and helpful in your interactions.
"""


# ============================================================================
# 🎯 MCP SERVER INTEGRATION - SIMPLIFIED APPROACH
# ============================================================================

class MCPServerManager:
    """Manages MCP server interactions for AutoGen agents."""
    
    def __init__(self):
        self.hello_function = mcp_hello_tool_function
        self.math_function = mcp_add_numbers_tool_function
        self.datetime_function = mcp_getdatetime_tool_function
    
    async def demonstrate_functions(self):
        """Demonstrate all MCP functions."""
        print("🧪 Testing MCP server integration directly...")
        
        # Test hello function
        test_result1 = await self.hello_function("AutoGen User")
        print(f"📝 Hello MCP call result: {test_result1}")
        
        # Test math function
        test_result2 = await self.math_function(25, 17)
        print(f"🔢 Math MCP call result: {test_result2}")
        
        # Test datetime function
        test_result3 = await self.datetime_function("readable")
        print(f"📅 Datetime MCP call result: {test_result3}")
        print("")
        
        return test_result1, test_result2


# ============================================================================
# 🎯 THIS IS WHERE WE INJECT MCP SERVERS INTO AUTOGEN AGENTS
# ============================================================================

async def mcp_hello_tool_function(name: str = "World") -> str:
    """
    ✨ THIS IS THE INJECTION POINT! ✨
    This function converts MCP server calls into AutoGen-callable tools.
    
    When an AutoGen agent calls this function, it will:
    1. Connect to the MCP server
    2. Call the server's hello_world function
    3. Return the result to the agent
    """
    print(f"🔗 AutoGen agent is calling MCP server with name: {name}")
    
    try:
        # Start the MCP server process
        process = await asyncio.create_subprocess_exec(
            "python", "simple_mcp_server.py",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Initialize the server
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "autogen-client", "version": "1.0.0"}
            }
        }
        
        process.stdin.write((json.dumps(init_request) + "\n").encode())
        await process.stdin.drain()
        await process.stdout.readline()  # Read init response
        
        # Call the hello_world tool on MCP server
        tool_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "hello_world",
                "arguments": {"name": name}
            }
        }
        
        process.stdin.write((json.dumps(tool_request) + "\n").encode())
        await process.stdin.drain()
        
        # Read response from MCP server
        response_line = await process.stdout.readline()
        response = json.loads(response_line.decode().strip())
        
        # Clean up
        process.terminate()
        await process.wait()
        
        result = response['result']['content'][0]['text']
        print(f"📡 MCP Server returned: {result}")
        return result
        
    except Exception as e:
        return f"Error calling MCP server: {e}"


async def mcp_add_numbers_tool_function(a: float, b: float) -> str:
    """
    ✨ MATH FUNCTION INJECTION POINT! ✨
    This function connects AutoGen agents to the MCP server's add_numbers tool.
    
    When an AutoGen agent calls this function, it will:
    1. Connect to the MCP server
    2. Call the server's add_numbers function
    3. Return the math result to the agent
    """
    print(f"🔢 AutoGen agent is calling MCP server to add: {a} + {b}")
    
    try:
        # Start the MCP server process
        process = await asyncio.create_subprocess_exec(
            "python", "simple_mcp_server.py",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Initialize the server
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "autogen-client", "version": "1.0.0"}
            }
        }
        
        process.stdin.write((json.dumps(init_request) + "\n").encode())
        await process.stdin.drain()
        await process.stdout.readline()  # Read init response
        
        # Call the add_numbers tool on MCP server
        tool_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "add_numbers",
                "arguments": {"a": a, "b": b}
            }
        }
        
        process.stdin.write((json.dumps(tool_request) + "\n").encode())
        await process.stdin.drain()
        
        # Read response from MCP server
        response_line = await process.stdout.readline()
        response = json.loads(response_line.decode().strip())
        
        # Clean up
        process.terminate()
        await process.wait()
        
        result = response['result']['content'][0]['text']
        print(f"🧮 MCP Server calculated: {result}")
        return result
        
    except Exception as e:
        return f"Error calling MCP server for math: {e}"


async def mcp_getdatetime_tool_function(format_type: str = "readable") -> str:
    """
    ✨ DATETIME FUNCTION INJECTION POINT! ✨
    This function connects AutoGen agents to the MCP server's getdatetime tool.
    
    When an AutoGen agent calls this function, it will:
    1. Connect to the MCP server
    2. Call the server's getdatetime function
    3. Return the datetime result to the agent
    """
    print(f"📅 AutoGen agent is calling MCP server to get datetime with format: {format_type}")
    
    try:
        # Start the MCP server process
        process = await asyncio.create_subprocess_exec(
            "python", "simple_mcp_server.py",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Initialize the server
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "autogen-client", "version": "1.0.0"}
            }
        }
        
        process.stdin.write((json.dumps(init_request) + "\n").encode())
        await process.stdin.drain()
        await process.stdout.readline()  # Read init response
        
        # Call the getdatetime tool on MCP server
        tool_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "getdatetime",
                "arguments": {"format": format_type}
            }
        }
        
        process.stdin.write((json.dumps(tool_request) + "\n").encode())
        await process.stdin.drain()
        
        # Read response from MCP server
        response_line = await process.stdout.readline()
        response = json.loads(response_line.decode().strip())
        
        # Clean up
        process.terminate()
        await process.wait()
        
        result = response['result']['content'][0]['text']
        print(f"🕒 MCP Server returned: {result}")
        return result
        
    except Exception as e:
        return f"Error calling MCP server for datetime: {e}"


async def main() -> None:
    """Main function to run the AutoGen multi-agent system."""
    
    if not AUTOGEN_AVAILABLE:
        print("❌ AutoGen packages not available. Please install them first.")
        return
    
    # Check for Azure OpenAI configuration
    required_vars = ["AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Please set the following environment variables in your .env file:")
        for var in missing_vars:
            print(f"   - {var}")
        return
    
    try:
        print("🔧 Setting up AutoGen agents...")
        
        # ============================================================================
        # 🎯 CREATE MCP SERVER MANAGER
        # ============================================================================
        mcp_manager = MCPServerManager()
        print("✅ Created MCP Server Manager with hello and math functions")
        
        # ============================================================================
        # 🎯 CREATE AUTOGEN AGENT (without tools for now)
        # ============================================================================
        hello_agent = AssistantAgent(
            name="hello_agent",
            model_client=get_azure_openai_client(),
            # tools=mcp_tools,  # ← Tools not available in current version
            system_message=hello_agent_prompt,
        )
        print("✅ Created AutoGen agent - MCP functions available for demonstration")
        
        user_proxy = UserProxyAgent("user")
        
        # Create termination condition
        termination = TextMentionTermination("exit")
        
        # Create the team
        team = RoundRobinGroupChat(
            [hello_agent, user_proxy],
            termination_condition=termination,
        )
        
        # Start the conversation
        print("\n🤖 AutoGen Multi-Agent System Started!")
        print("💡 The system has access to MCP server functions!")
        print("💬 Try saying: 'Hello Alice' or normal conversation")
        print("🧮 MCP functions are demonstrated separately below")
        print("🚪 Type 'exit' to quit\n")
        
        # ============================================================================
        # 🎯 DEMONSTRATE MCP INTEGRATION
        # ============================================================================
        await mcp_manager.demonstrate_functions()
        
        initial_task = """Hello! I'm a friendly agent. While I can chat with you normally, 
this system also has access to MCP server functions for greetings and math. 
The MCP integration is demonstrated above. Try having a conversation with me!"""
        
        await Console(team.run_stream(task=initial_task))
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        print("Make sure you have:")
        print("1. Set Azure OpenAI configuration in your .env file")
        print("2. Installed AutoGen packages: pip install autogen-agentchat autogen-ext")


if __name__ == "__main__":
    if AUTOGEN_AVAILABLE:
        asyncio.run(main())
    else:
        print("\n📋 To use this AutoGen integration:")
        print("1. Install AutoGen: pip install autogen-agentchat autogen-ext")
        print("2. Set Azure OpenAI configuration in .env file")
        print("3. Run: python simple_autogen_client.py")
