#!/usr/bin/env python3
"""
Quick test to verify all imports work correctly
"""
import sys
import os

print("Python version:", sys.version)
print("Current working directory:", os.getcwd())
print("Python path:", sys.path)

try:
    print("Testing basic imports...")
    import fastapi
    print("✅ FastAPI imported successfully")
    
    import uvicorn 
    print("✅ Uvicorn imported successfully")
    
    import mcp
    print("✅ MCP imported successfully")
    
    print("Testing application imports...")
    from simple_mcp_server_wrapper import mcp_simple_server
    print("✅ MCP server wrapper imported successfully")
    
    from api_key_auth import ensure_valid_api_key
    print("✅ API key auth imported successfully")
    
    print("All imports successful!")
    
    # Check environment variables
    print("\nEnvironment variables:")
    print(f"API_KEYS: {'SET' if os.getenv('API_KEYS') else 'NOT SET'}")
    print(f"PORT: {os.getenv('PORT', 'NOT SET')}")
    print(f"WEBSITES_PORT: {os.getenv('WEBSITES_PORT', 'NOT SET')}")
    
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
