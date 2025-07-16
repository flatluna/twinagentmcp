"""
AutoGen client that uses the simple MCP server.
This demonstrates how to integrate MCP tools with AutoGen agents
as shown in the article.
"""

import os
import asyncio
from typing import Sequence
from dotenv import load_dotenv

from autogen_ext.tools.mcp import StdioServerParams, mcp_server_tools
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from autogen_agentchat.messages import BaseAgentEvent, BaseChatMessage
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.ui import Console

# Load environment variables
load_dotenv()


def get_model_client() -> AzureOpenAIChatCompletionClient:
    """Create and return an Azure OpenAI client."""
    return AzureOpenAIChatCompletionClient(
        azure_deployment=os.getenv("AZURE_OPENAI_MODEL_DEPLOYMENT"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        model="gpt-4o"
    )


# Agent prompts
hello_agent_prompt = """
You are a friendly Hello Agent. Use the hello_world tool to greet users and respond to their questions.
When a user asks about hello world or greets you, use the hello_world tool to provide a response.
Be friendly and helpful in your interactions.
"""

assistant_agent_prompt = """
You are a helpful AI assistant. You can help users with various tasks and answer their questions.
If the user asks about hello world or wants a greeting, let the Hello Agent handle it.
Otherwise, provide helpful responses based on your knowledge.
"""


async def main() -> None:
    """Main function to run the AutoGen multi-agent system with MCP."""
    
    # Configure the MCP server parameters
    # This points to our simple MCP server script
    mcp_server_params = StdioServerParams(
        command="python",
        args=["simple_mcp_server.py"],
        read_timeout_seconds=30
    )
    
    try:
        # Get tools from the MCP server
        print("Connecting to MCP server...")
        mcp_tools = await mcp_server_tools(mcp_server_params)
        print(f"Successfully connected! Available tools: {[tool.name for tool in mcp_tools]}")
        
        # Create agents
        hello_agent = AssistantAgent(
            name="hello_agent",
            model_client=get_model_client(),
            tools=mcp_tools,  # Assign MCP tools to this agent
            system_message=hello_agent_prompt,
        )
        
        assistant_agent = AssistantAgent(
            name="assistant_agent",
            model_client=get_model_client(),
            system_message=assistant_agent_prompt,
        )
        
        user_proxy = UserProxyAgent("user", input_func=input)
        
        # Create termination condition
        termination = TextMentionTermination("exit")
        
        # Define selector function for conversation flow
        def selector_func(messages: Sequence[BaseAgentEvent | BaseChatMessage]) -> str | None:
            if not messages:
                return user_proxy.name
            
            last_message = messages[-1]
            
            # If user just spoke, determine which agent should respond
            if last_message.source == "user":
                # Check if the message contains hello-related keywords
                message_content = str(last_message.content).lower()
                if any(keyword in message_content for keyword in ["hello", "hi", "greet", "world"]):
                    return hello_agent.name
                else:
                    return assistant_agent.name
            
            # Return to user after any agent responds
            return user_proxy.name
        
        # Create the team
        team = SelectorGroupChat(
            [hello_agent, assistant_agent, user_proxy],
            model_client=get_model_client(),
            termination_condition=termination,
            selector_func=selector_func,
            allow_repeated_speaker=False,
        )
        
        # Start the conversation
        print("\n🤖 Multi-Agent System with MCP Server Started!")
        print("💡 Try asking: 'Hello World' or 'Say hello to John'")
        print("🚪 Type 'exit' to quit\n")
        
        initial_task = "Hello! I'm ready to help you. Try asking me to say hello world!"
        
        await Console(team.run_stream(task=initial_task))
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        print("Make sure you have:")
        print("1. Set up your .env file with Azure OpenAI credentials")
        print("2. Installed all required packages: pip install -r requirements.txt")


if __name__ == "__main__":
    asyncio.run(main())
