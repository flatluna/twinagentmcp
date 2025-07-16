"""
Enhanced AutoGen client that demonstrates how AutoGen agents 
call MCP server functions more explicitly.
"""

import os
import asyncio
import json
from typing import Any, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
    from autogen_agentchat.teams import RoundRobinGroupChat
    from autogen_agentchat.conditions import TextMentionTermination
    from autogen_agentchat.ui import Console
    from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
    from autogen_core import FunctionCall, Tool
    AUTOGEN_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  AutoGen packages not installed: {e}")
    AUTOGEN_AVAILABLE = False


class MCPServerTool:
    """
    A tool that wraps MCP server function calls for AutoGen agents.
    This shows how AutoGen agents can call MCP server functions.
    """
    
    def __init__(self):
        self.server_process = None
    
    async def start_mcp_server(self):
        """Start the MCP server process."""
        self.server_process = await asyncio.create_subprocess_exec(
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
                "clientInfo": {"name": "autogen-mcp-client", "version": "1.0.0"}
            }
        }
        
        self.server_process.stdin.write((json.dumps(init_request) + "\n").encode())
        await self.server_process.stdin.drain()
        await self.server_process.stdout.readline()  # Read init response
        
        print("🔗 MCP Server started and connected to AutoGen")
    
    async def call_mcp_function(self, function_name: str, arguments: Dict[str, Any]) -> str:
        """
        This is how AutoGen agents call MCP server functions.
        """
        if not self.server_process:
            await self.start_mcp_server()
        
        # Prepare the MCP tool call request
        tool_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": function_name,
                "arguments": arguments
            }
        }
        
        print(f"🤖 AutoGen Agent calling MCP function: {function_name} with args: {arguments}")
        
        # Send request to MCP server
        self.server_process.stdin.write((json.dumps(tool_request) + "\n").encode())
        await self.server_process.stdin.drain()
        
        # Read response from MCP server
        response_line = await self.server_process.stdout.readline()
        response = json.loads(response_line.decode().strip())
        
        result = response['result']['content'][0]['text']
        print(f"📡 MCP Server response: {result}")
        
        return result
    
    async def hello_world_function(self, name: str = "World") -> str:
        """
        AutoGen-callable function that wraps the MCP server's hello_world tool.
        This is what gets registered as a tool for AutoGen agents.
        """
        return await self.call_mcp_function("hello_world", {"name": name})
    
    async def stop_server(self):
        """Stop the MCP server."""
        if self.server_process:
            self.server_process.terminate()
            await self.server_process.wait()
            print("🛑 MCP Server stopped")


def get_azure_openai_client():
    """Create Azure OpenAI client for AutoGen agents."""
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
            "json_output": True,
            "structured_output": True
        }
    )


# Create a global MCP tool instance
mcp_tool = MCPServerTool()


async def hello_world_tool_for_autogen(name: str = "World") -> str:
    """
    This is the function that AutoGen agents can call.
    It acts as a bridge between AutoGen and the MCP server.
    """
    print(f"🎯 AutoGen agent called hello_world_tool_for_autogen with name: {name}")
    result = await mcp_tool.hello_world_function(name)
    return result


async def main():
    """Demonstrate AutoGen agents calling MCP server functions."""
    
    if not AUTOGEN_AVAILABLE:
        print("❌ AutoGen packages not available.")
        return
    
    # Check Azure OpenAI configuration
    required_vars = ["AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        return
    
    try:
        print("🚀 Starting AutoGen + MCP Integration Demo")
        print("=" * 60)
        
        # Start MCP server
        await mcp_tool.start_mcp_server()
        
        # Create AutoGen tool from MCP function
        hello_tool = Tool(
            name="say_hello",
            description="Say hello to someone using the MCP server",
            func=hello_world_tool_for_autogen
        )
        
        print("🛠️  Created AutoGen tool that calls MCP server")
        
        # Create AutoGen agents
        hello_agent = AssistantAgent(
            name="hello_agent",
            model_client=get_azure_openai_client(),
            tools=[hello_tool],  # This agent can call the MCP server function!
            system_message="""
            You are a friendly Hello Agent. You have access to a 'say_hello' tool 
            that can greet people via an MCP server. Use this tool when users ask 
            you to say hello to someone or greet them.
            
            When you use the tool, explain that you're calling the MCP server.
            """
        )
        
        user_proxy = UserProxyAgent("user")
        
        # Create team
        team = RoundRobinGroupChat(
            [hello_agent, user_proxy],
            termination_condition=TextMentionTermination("exit")
        )
        
        print("\n🤖 AutoGen Multi-Agent System with MCP Integration Started!")
        print("💡 The AutoGen agent can now call MCP server functions!")
        print("💬 Try: 'Please say hello to Alice using your tool'")
        print("🚪 Type 'exit' to quit\n")
        
        # Demonstrate the integration
        print("🧪 Testing AutoGen → MCP Server integration:")
        print("-" * 50)
        
        # Test direct function call
        result = await hello_world_tool_for_autogen("AutoGen User")
        print(f"✅ Direct call result: {result}")
        
        # Start interactive session
        initial_task = "Hello! I can use my say_hello tool to greet people via the MCP server. Try asking me to say hello to someone!"
        
        await Console(team.run_stream(task=initial_task))
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        await mcp_tool.stop_server()


if __name__ == "__main__":
    if AUTOGEN_AVAILABLE:
        asyncio.run(main())
    else:
        print("Install AutoGen packages to run this demo.")
