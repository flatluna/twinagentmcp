#!/usr/bin/env python3
"""
Quick test to verify all imports work correctly
"""
import sys
import os

print("=== IMPORT TEST STARTING ===")
print("Python version:", sys.version)
print("Current working directory:", os.getcwd())

try:
    print("Testing basic imports...")
    import fastapi
    print("✅ FastAPI imported successfully")
    
    import uvicorn 
    print("✅ Uvicorn imported successfully")
    
    import mcp
    print("✅ MCP imported successfully")
    
    print("Testing application imports...")
    
    # Test MCP server wrapper first
    try:
        from simple_mcp_server_wrapper import mcp_simple_server
        print("✅ MCP server wrapper imported successfully")
    except Exception as e:
        print(f"❌ MCP server wrapper failed: {e}")
        raise
    
    # Test API key auth (this might be causing the Pydantic issue)
    try:
        from api_key_auth import ensure_valid_api_key
        print("✅ API key auth imported successfully")
    except Exception as e:
        print(f"❌ API key auth failed: {e}")
        raise
    
    print("✅ All imports successful!")
    
    # Check environment variables
    print("\n=== ENVIRONMENT CHECK ===")
    print(f"API_KEYS: {'SET' if os.getenv('API_KEYS') else 'NOT SET'}")
    print(f"PORT: {os.getenv('PORT', 'NOT SET')}")
    print(f"WEBSITES_PORT: {os.getenv('WEBSITES_PORT', 'NOT SET')}")
    
    print("=== IMPORT TEST COMPLETED SUCCESSFULLY ===")
    
except Exception as e:
    print(f"❌ Import test failed: {e}")
    import traceback
    traceback.print_exc()
    print("=== IMPORT TEST FAILED ===")
    sys.exit(1)
