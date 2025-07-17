"""
Math Agent Client - A specialized AutoGen agent that does math calculations
and provides timestamps using the MCP server.
"""

import os
import asyncio
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if AutoGen is available
try:
    from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
    from autogen_agentchat.teams import RoundRobinGroupChat
    from autogen_agentchat.conditions import TextMentionTermination
    from autogen_agentchat.ui import Console
    from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
    
    AUTOGEN_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  AutoGen packages not installed: {e}")
    print("💡 Install with: pip install autogen-agentchat autogen-ext")
    AUTOGEN_AVAILABLE = False


def get_azure_openai_client():
    """Create and return an Azure OpenAI client."""
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


# Specialized Math Agent Prompt
math_agent_prompt = """
You are a specialized Math Calculator Agent! 🧮

Your capabilities:
1. 🔢 MATH CALCULATIONS: You can add, subtract, multiply, divide numbers
2. 🕒 TIMESTAMPS: You provide the exact date and time when calculations are performed

When a user asks for math:
1. First, perform the calculation using the MCP math function
2. Then, get the current timestamp using the MCP datetime function  
3. Present the result with the timestamp

Example interaction:
User: "What's 25 + 17?"
You: "Let me calculate that for you and provide a timestamp..."
[Use MCP functions]
You: "The result is 42, calculated on Wednesday, July 16, 2025 at 05:30:15 PM"

Always be precise, helpful, and include timestamps for all calculations!
"""


# ============================================================================
# 🎯 MCP SERVER INTEGRATION FOR MATH AGENT
# ============================================================================

async def mcp_add_numbers_for_math_agent(a: float, b: float) -> str:
    """Connect to MCP server to perform addition."""
    print(f"🔢 Math Agent calling MCP server: {a} + {b}")
    
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
                "clientInfo": {"name": "math-agent", "version": "1.0.0"}
            }
        }
        
        process.stdin.write((json.dumps(init_request) + "\n").encode())
        await process.stdin.drain()
        await process.stdout.readline()  # Read init response
        
        # Call the add_numbers tool
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
        
        # Read response
        response_line = await process.stdout.readline()
        response = json.loads(response_line.decode().strip())
        
        # Clean up
        process.terminate()
        await process.wait()
        
        result = response['result']['content'][0]['text']
        print(f"📊 MCP Server calculated: {result}")
        return result
        
    except Exception as e:
        return f"Error calling MCP server for math: {e}"


async def mcp_get_timestamp_for_math_agent() -> str:
    """Connect to MCP server to get current timestamp."""
    print("🕒 Math Agent getting timestamp from MCP server...")
    
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
                "clientInfo": {"name": "math-agent", "version": "1.0.0"}
            }
        }
        
        process.stdin.write((json.dumps(init_request) + "\n").encode())
        await process.stdin.drain()
        await process.stdout.readline()  # Read init response
        
        # Call the getdatetime tool
        tool_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "getdatetime",
                "arguments": {"format": "readable"}
            }
        }
        
        process.stdin.write((json.dumps(tool_request) + "\n").encode())
        await process.stdin.drain()
        
        # Read response
        response_line = await process.stdout.readline()
        response = json.loads(response_line.decode().strip())
        
        # Clean up
        process.terminate()
        await process.wait()
        
        result = response['result']['content'][0]['text']
        print(f"📅 MCP Server timestamp: {result}")
        return result
        
    except Exception as e:
        return f"Error calling MCP server for timestamp: {e}"


class MathAgentManager:
    """Manages MCP server interactions specifically for the Math Agent."""
    
    def __init__(self):
        self.math_function = mcp_add_numbers_for_math_agent
        self.timestamp_function = mcp_get_timestamp_for_math_agent
    
    async def perform_calculation_with_timestamp(self, a: float, b: float) -> str:
        """Perform a math calculation and provide timestamp."""
        print(f"🧮 Math Agent performing calculation: {a} + {b}")
        
        # Get the math result
        math_result = await self.math_function(a, b)
        
        # Get the timestamp
        timestamp = await self.timestamp_function()
        
        # Combine results
        final_result = f"{math_result}, calculated on {timestamp.replace('Current date and time: ', '')}"
        
        return final_result
    
    async def demonstrate_math_agent(self):
        """Demonstrate the Math Agent capabilities."""
        print("🧮 Math Agent Demo - Testing MCP integration...")
        print("")
        
        # Test calculation with timestamp
        result = await self.perform_calculation_with_timestamp(125, 375)
        print(f"📊 Final Result: {result}")
        print("")


async def main() -> None:
    """Main function to run the Math Agent."""
    
    if not AUTOGEN_AVAILABLE:
        print("❌ AutoGen packages not available.")
        print("💡 For now, running Math Agent demo without AutoGen...")
        
        # Run demo without AutoGen
        math_manager = MathAgentManager()
        await math_manager.demonstrate_math_agent()
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
        print("🧮 Setting up Math Agent...")
        
        # ============================================================================
        # 🎯 CREATE MATH AGENT MANAGER
        # ============================================================================
        math_manager = MathAgentManager()
        print("✅ Created Math Agent Manager with calculation and timestamp functions")
        
        # ============================================================================
        # 🎯 CREATE SPECIALIZED MATH AGENT
        # ============================================================================
        math_agent = AssistantAgent(
            name="math_agent",
            model_client=get_azure_openai_client(),
            system_message=math_agent_prompt,
        )
        print("✅ Created Math Agent - specialized for calculations with timestamps")
        
        user_proxy = UserProxyAgent("user")
        
        # Create termination condition
        termination = TextMentionTermination("exit")
        
        # Create the team
        team = RoundRobinGroupChat(
            [math_agent, user_proxy],
            termination_condition=termination,
        )
        
        # Start the conversation
        print("\n🧮 Math Agent Started!")
        print("💡 I specialize in math calculations with timestamps!")
        print("💬 Try: 'What is 25 + 17?' or 'Calculate 100 + 200'")
        print("🚪 Type 'exit' to quit\n")
        
        # ============================================================================
        # 🎯 DEMONSTRATE MATH AGENT CAPABILITIES
        # ============================================================================
        await math_manager.demonstrate_math_agent()
        
        initial_task = """Hello! I'm your Math Agent! 🧮 
        
I specialize in:
- 🔢 Mathematical calculations (addition, subtraction, etc.)
- 🕒 Providing precise timestamps for when calculations are performed

Try asking me to calculate something like "What's 25 + 17?" and I'll give you the result with a timestamp!"""
        
        await Console(team.run_stream(task=initial_task))
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        print("Make sure you have:")
        print("1. Set Azure OpenAI configuration in your .env file")
        print("2. Installed AutoGen packages: pip install autogen-agentchat autogen-ext")


if __name__ == "__main__":
    print("🚀 Starting Math Agent Client...")
    print("=" * 50)
    asyncio.run(main())
