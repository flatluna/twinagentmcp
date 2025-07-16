# Azure Deployment Guide for Simple MCP Server

This guide explains how to deploy your Simple MCP Server to Azure Container Apps.

## Deployment Files Created

- `start_server.py`: FastAPI wrapper with SSE support for Azure deployment
- `simple_mcp_server_wrapper.py`: MCP server wrapper using official MCP framework
- `api_key_auth.py`: API key authentication middleware
- `Dockerfile`: Container configuration
- `sample.env`: Environment configuration template
- `deploy_server_aca.sh`: Linux/Mac deployment script
- `deploy_server_aca.ps1`: Windows PowerShell deployment script

## Quick Deployment

### 1. Prerequisites
- Azure CLI installed and logged in: `az login`
- Docker installed (for container building)

### 2. Deploy to Azure

**Windows (PowerShell):**
```powershell
.\deploy_server_aca.ps1
```

**Linux/Mac/WSL:**
```bash
chmod +x deploy_server_aca.sh
./deploy_server_aca.sh
```

The script will prompt for:
- Azure Region (e.g., eastus)
- Resource Group name
- Container App name  
- Container App Environment name

### 3. Get Connection Details

After deployment, you'll see output like:
```
========================================
Add the following to your MCP client .env file:

MCP_API_KEYS="your-generated-api-key"
MCP_URL="https://your-app.eastus.azurecontainerapps.io/sse"
========================================
```

### 4. Update Your Client

Add these values to your client's `.env` file and use the AutoGen SSE pattern:

```python
from autogen_ext.tools.mcp import SseServerParams, mcp_server_tools

server_params = SseServerParams(
    url=os.getenv("MCP_URL"),
    headers={"x-api-key": os.getenv("MCP_API_KEYS")}
)

mcp_tools = await mcp_server_tools(server_params)
```

## Architecture

```
AutoGen Client → HTTPS/SSE → Azure Container Apps → MCP Server → Tools
```

Your MCP server is now deployed and accessible from anywhere with proper authentication!
