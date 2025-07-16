"""
Interactive demo of the MCP Hello World server.
This script provides a command-line interface to interact with the MCP server.
"""

import asyncio
import json
from test_mcp_client import SimpleMCPClient


async def interactive_demo():
    """Run an interactive demo of the MCP server."""
    print("🎯 Interactive MCP Hello World Demo")
    print("=" * 50)
    
    # Create and start client
    client = SimpleMCPClient(["python", "simple_mcp_server.py"])
    
    try:
        await client.start_server()
        await client.initialize()
        tools = await client.list_tools()
        
        print(f"\n🛠️  Available tools: {[tool['name'] for tool in tools]}")
        print("\n💬 Interactive Mode - Enter names to greet (or 'quit' to exit)")
        print("=" * 50)
        
        while True:
            try:
                name = input("\n👤 Enter a name to greet (or 'quit'): ").strip()
                
                if name.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if not name:
                    name = "World"
                
                # Call the hello_world tool
                result = await client.call_hello_world(name)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except EOFError:
                print("\n\n👋 Goodbye!")
                break
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        await client.stop_server()


async def batch_demo():
    """Run a batch demo with predefined names."""
    print("🔄 Batch Demo - Testing with multiple names")
    print("=" * 50)
    
    names = ["World", "Alice", "Bob", "Charlie", "Diana", "MCP Server", "AutoGen"]
    
    client = SimpleMCPClient(["python", "simple_mcp_server.py"])
    
    try:
        await client.start_server()
        await client.initialize()
        await client.list_tools()
        
        print(f"\n🧪 Testing with {len(names)} different names:")
        print("-" * 30)
        
        for name in names:
            await client.call_hello_world(name)
            await asyncio.sleep(0.5)  # Small delay for readability
        
        print("\n✅ Batch demo completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        await client.stop_server()


def main():
    """Main entry point for the demo."""
    print("🚀 MCP Hello World Demo")
    print("Choose a demo mode:")
    print("1. Interactive Demo (you enter names)")
    print("2. Batch Demo (predefined names)")
    print("3. Exit")
    
    try:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            asyncio.run(interactive_demo())
        elif choice == "2":
            asyncio.run(batch_demo())
        elif choice == "3":
            print("👋 Goodbye!")
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except EOFError:
        print("\n👋 Goodbye!")


if __name__ == "__main__":
    main()
