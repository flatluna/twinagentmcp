"""
Setup and installation script for the MCP Hello World project.
This script helps users get started quickly.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {description}: {e}")
        print(f"Error output: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required. Current version: {version.major}.{version.minor}")
        return False
    print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True


def install_dependencies():
    """Install required Python packages."""
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    return run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing dependencies"
    )


def create_env_file():
    """Create .env file if it doesn't exist."""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if not env_example.exists():
        print("❌ .env.example not found")
        return False
    
    try:
        env_example_content = env_example.read_text()
        env_file.write_text(env_example_content)
        print("✅ Created .env file from template")
        print("💡 Edit .env file to add your API keys")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False


def test_mcp_server():
    """Test the MCP server."""
    return run_command(
        f"{sys.executable} test_mcp_client.py",
        "Testing MCP server"
    )


def main():
    """Main setup function."""
    print("🚀 MCP Hello World Project Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies. Setup incomplete.")
        return
    
    # Create .env file
    create_env_file()
    
    # Test the basic MCP server
    print("\n🧪 Testing the MCP server...")
    if test_mcp_server():
        print("\n🎉 Setup completed successfully!")
        print("\n📋 What you can do now:")
        print("1. Run the interactive demo: python demo.py")
        print("2. Test the basic client: python test_mcp_client.py")
        print("3. (Optional) Set up AutoGen:")
        print("   - Edit .env file with your API keys")
        print("   - Run: python simple_autogen_client.py (for OpenAI)")
        print("   - Run: python autogen_mcp_client.py (for Azure OpenAI)")
    else:
        print("❌ MCP server test failed. Please check the error messages above.")


if __name__ == "__main__":
    main()
