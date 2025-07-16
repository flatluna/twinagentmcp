#!/usr/bin/env python3
"""
MCP Server wrapper for the Simple MCP Server.
This adapts the SimpleMCPServer to work with the official MCP server framework.
"""

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
import asyncio


# Create MCP server instance
server = Server("simple-hello-mcp-server")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="hello_world",
            description="A simple tool that responds with a hello world message",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name to greet (optional)",
                        "default": "World"
                    }
                }
            },
        ),
        types.Tool(
            name="add_numbers",
            description="Add two numbers together and return the result",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "The first number to add"
                    },
                    "b": {
                        "type": "number", 
                        "description": "The second number to add"
                    }
                },
                "required": ["a", "b"]
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls."""
    if name == "hello_world":
        user_name = arguments.get("name", "World")
        response_text = f"Hello, {user_name}! This is a response from the MCP server."
        return [types.TextContent(type="text", text=response_text)]
    
    elif name == "add_numbers":
        a = arguments.get("a", 0)
        b = arguments.get("b", 0)
        result = a + b
        response_text = f"The sum of {a} + {b} = {result}"
        return [types.TextContent(type="text", text=response_text)]
    
    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """Main entry point for the MCP server."""
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            NotificationOptions(
                prompts_changed=False,
                resources_changed=False,
                tools_changed=False,
            ),
        )


# Global server instance for SSE transport
mcp_simple_server = server


if __name__ == "__main__":
    asyncio.run(main())
