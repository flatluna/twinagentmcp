# 🚀 Azure Deployment Guide for TwinAgent MCP

This guide explains how to deploy your TwinAgent MCP Server to Azure Container Apps using GitHub Actions.

## 📋 Current Deployment Status

✅ **Working Deployment**: https://twinagentservices.politepond-2f6f686d.eastus.azurecontainerapps.io  
✅ **CI/CD Pipeline**: Automated GitHub Actions deployment  
✅ **API Authentication**: Secured with API key authentication  

## 🏗️ Deployment Architecture

```
GitHub Repository → GitHub Actions → Azure Container Registry → Azure Container Apps
```

## 🔧 Deployment Files

The following files are essential for deployment:

- `start_server.py`: FastAPI wrapper with JSON-RPC support for Azure deployment
- `api_key_auth.py`: API key authentication middleware  
- `Dockerfile`: Container configuration
- `.github/workflows/deploy.yml`: GitHub Actions CI/CD pipeline
- `requirements.txt`: Python dependencies

## 🚀 How to Deploy

### Method 1: Automatic GitHub Actions (Recommended)

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Deploy to Azure"
   git push
   ```

2. **Monitor Deployment**:
   - Go to your GitHub repository
   - Click "Actions" tab
   - Watch the deployment progress

3. **Get Your URL**:
   - After successful deployment, your MCP server will be available at:
   - `https://twinagentservices.politepond-2f6f686d.eastus.azurecontainerapps.io`

### Method 2: Manual Azure CLI

If you need to deploy manually:

```bash
# Login to Azure
az login

# Deploy to Container Apps
az containerapp up \
  --name twinagentservices \
  --source . \
  --resource-group twinagent-rg \
  --environment twinagent-env \
  --ingress external \
  --target-port 8000
```

## 🔑 Environment Variables

The following environment variables are configured in GitHub Secrets:

```env
AZURE_CREDENTIALS="{...}"  # Service Principal credentials
MCP_API_KEY="B509918774DDE22A5BF94EDB4F145CB6E06F1CBCCC49D492D27FFD4AC3667A71"
```

## 🧪 Testing Your Deployment

### Health Check
```bash
curl https://twinagentservices.politepond-2f6f686d.eastus.azurecontainerapps.io/health
```

### Call MCP Functions
```bash
# Test hello_world
curl -X POST https://twinagentservices.politepond-2f6f686d.eastus.azurecontainerapps.io/mcp \
  -H "x-api-key: B509918774DDE22A5BF94EDB4F145CB6E06F1CBCCC49D492D27FFD4AC3667A71" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"hello_world","arguments":{}}}'

# Test add_numbers
curl -X POST https://twinagentservices.politepond-2f6f686d.eastus.azurecontainerapps.io/mcp \
  -H "x-api-key: B509918774DDE22A5BF94EDB4F145CB6E06F1CBCCC49D492D27FFD4AC3667A71" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"add_numbers","arguments":{"a":944,"b":444}}}'
```

## 🔧 Client Integration

To use your deployed MCP server with AutoGen clients:

```python
import httpx

# MCP Server Configuration
MCP_SERVER_URL = "https://twinagentservices.politepond-2f6f686d.eastus.azurecontainerapps.io"
MCP_API_KEY = "B509918774DDE22A5BF94EDB4F145CB6E06F1CBCCC49D492D27FFD4AC3667A71"

headers = {
    "x-api-key": MCP_API_KEY,
    "Content-Type": "application/json"
}

# Call MCP functions
async def call_mcp_function(function_name, arguments={}):
    async with httpx.AsyncClient() as client:
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call", 
            "params": {
                "name": function_name,
                "arguments": arguments
            }
        }
        
        response = await client.post(
            f"{MCP_SERVER_URL}/mcp",
            json=request,
            headers=headers
        )
        
        return response.json()
```

## 📊 Monitoring & Logs

### Azure Portal
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your Container App: `twinagentservices`
3. View logs and metrics in the "Monitoring" section

### GitHub Actions
1. Check deployment history in your repository's "Actions" tab
2. View build logs and deployment status

## 🔒 Security Features

- ✅ **API Key Authentication**: All endpoints protected with `x-api-key` header
- ✅ **CORS Enabled**: Configured for web access
- ✅ **HTTPS Only**: All traffic encrypted
- ✅ **Environment Variables**: Sensitive data stored in GitHub Secrets

## 🛠️ Troubleshooting

### Common Issues

1. **Deployment Fails**
   - Check GitHub Actions logs
   - Verify Azure credentials in secrets
   - Ensure Dockerfile builds locally

2. **Server Not Responding**
   - Check Azure Container Apps logs
   - Verify API key is correct
   - Test health endpoint first

3. **Tools Not Working**
   - Verify JSON-RPC request format
   - Check function names match exactly
   - Ensure authentication headers are included

### Quick Fixes

```bash
# Redeploy if needed
git add . && git commit -m "Fix deployment" && git push

# Check logs
az containerapp logs show --name twinagentservices --resource-group twinagent-rg

# Test locally first
python start_server.py
```

## 📈 Scaling & Performance

Your Azure Container Apps deployment automatically:
- ✅ Scales based on HTTP traffic
- ✅ Handles SSL/TLS termination
- ✅ Provides load balancing
- ✅ Includes health monitoring

## 🎯 Next Steps

1. **Add More Tools**: Extend your MCP server with additional functions
2. **Enhanced Monitoring**: Add Application Insights for detailed telemetry
3. **AutoGen Integration**: Build full agent workflows using your cloud MCP server
4. **Custom Domain**: Configure a custom domain for your deployment

---

**Your MCP Server is Live**: https://twinagentservices.politepond-2f6f686d.eastus.azurecontainerapps.io 🎉
