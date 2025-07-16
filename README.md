# 🤖 TwinAgent MCP - AutoGen + Model Context Protocol

A production-ready integration of Microsoft AutoGen with Model Context Protocol (MCP) deployed on Azure.

## 🎯 What This Does

- **MCP Server**: Custom tools (hello_world, add_numbers) accessible via JSON-RPC
- **AutoGen Integration**: AI agents can use MCP tools for enhanced capabilities  
- **Azure Deployment**: Cloud-hosted MCP server with API authentication
- **CI/CD Pipeline**: Automated GitHub Actions deployment to Azure Container Apps

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AutoGen       │    │   FastAPI       │    │   Azure         │
│   Client        │◄──►│   MCP Wrapper   │◄──►│   Container     │
│                 │    │                 │    │   Apps          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
    ┌────▼────┐             ┌────▼────┐             ┌────▼────┐
    │ Azure   │             │   MCP   │             │  JSON-  │
    │ OpenAI  │             │ Server  │             │   RPC   │
    └─────────┘             └─────────┘             └─────────┘
```

## 🚀 Quick Start

### 1. Setup Local Environment
```bash
git clone https://github.com/flatluna/twinagentmcp.git
cd TwinagentMCP
python -m venv twinagentapp
.\twinagentapp\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment
Copy `.env.example` to `.env` and update values:
```env
AZURE_OPENAI_ENDPOINT=your-endpoint
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment
AZURE_OPENAI_API_VERSION=2024-02-01
MCP_API_KEYS=your-api-key
```

### 3. Test Locally
```bash
# Test MCP server directly
python simple_mcp_server.py

# Test web wrapper locally  
python start_server.py

# Test AutoGen integration
python simple_autogen_client.py
```

## 📁 Project Structure

```
TwinagentMCP/
├── 📄 simple_mcp_server.py        # Core MCP server with tools
├── 📄 start_server.py             # FastAPI wrapper for deployment  
├── 📄 simple_autogen_client.py    # AutoGen client with MCP integration
├── 📄 api_key_auth.py             # Authentication middleware
├── 📄 requirements.txt            # Python dependencies
├── 📄 Dockerfile                  # Container configuration
├── 📄 .env                        # Environment variables
├── 📁 .github/workflows/          # CI/CD Pipeline
│   └── 📄 deploy.yml              # Deployment workflow
└── 📄 README.md                   # Documentation
```

## 🛠️ Available MCP Tools

### 1. Hello World
- **Function**: `hello_world`
- **Purpose**: Basic greeting and status check
- **Example**: `Hello, World! This is your MCP server running on Azure! 🌟`

### 2. Add Numbers  
- **Function**: `add_numbers`
- **Parameters**: `a` (number), `b` (number)
- **Purpose**: Mathematical addition
- **Example**: `add_numbers(944, 444)` → `1388`

### 3. Get DateTime  
- **Function**: `getdatetime`
- **Parameters**: `format` (string, optional) - "readable" or "iso"
- **Purpose**: Get current date and time
- **Example**: `getdatetime("readable")` → `Wednesday, July 16, 2025 at 05:13:27 PM`

## 🌐 Cloud Deployment

**Production URL**: https://twinagentservices.politepond-2f6f686d.eastus.azurecontainerapps.io

### Test Cloud MCP Server
```bash
# Health check
curl https://twinagentservices.politepond-2f6f686d.eastus.azurecontainerapps.io/health

# Call add_numbers function
curl -X POST https://twinagentservices.politepond-2f6f686d.eastus.azurecontainerapps.io/mcp \
  -H "x-api-key: B509918774DDE22A5BF94EDB4F145CB6E06F1CBCCC49D492D27FFD4AC3667A71" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"add_numbers","arguments":{"a":944,"b":444}}}'

# Call getdatetime function  
curl -X POST https://twinagentservices.politepond-2f6f686d.eastus.azurecontainerapps.io/mcp \
  -H "x-api-key: B509918774DDE22A5BF94EDB4F145CB6E06F1CBCCC49D492D27FFD4AC3667A71" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"getdatetime","arguments":{"format":"readable"}}}'
```

## 🔧 Adding New Tools

To add a new MCP tool:

1. **Define the tool** in `simple_mcp_server.py`:
```python
TOOLS.append({
    "name": "your_tool_name", 
    "description": "What your tool does",
    "inputSchema": {
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "Parameter description"}
        },
        "required": ["param1"]
    }
})
```

2. **Implement the handler** in `start_server.py`:
```python
elif tool_name == "your_tool_name":
    param1 = arguments.get("param1")
    result = f"Processed: {param1}"
    return JSONResponse({
        "jsonrpc": "2.0",
        "id": data["id"], 
        "result": {"content": [{"type": "text", "text": result}]}
    })
```

3. **Deploy automatically** via Git push (GitHub Actions handles the rest)

## ⚡ Quick Commands

```bash
# Local testing
python simple_mcp_server.py
python start_server.py  
python simple_autogen_client.py

# Deploy to Azure  
git add . && git commit -m "Update" && git push

# Test cloud deployment
curl https://twinagentservices.politepond-2f6f686d.eastus.azurecontainerapps.io/health
```

## 📊 Status

- ✅ **MCP Server**: Working with 2 tools
- ✅ **Local Testing**: Fully functional  
- ✅ **Azure Deployment**: Live and operational
- ✅ **CI/CD Pipeline**: Automated GitHub Actions
- ✅ **API Authentication**: Secured with API keys
- 🔄 **AutoGen Integration**: Ready for enhancement

---

**Live MCP Server**: https://twinagentservices.politepond-2f6f686d.eastus.azurecontainerapps.io  
**Repository**: https://github.com/flatluna/twinagentmcp.git
  --ingress external \
  --target-port 8000
```

## 🧪 Testing Your Deployment

### Health Check
```bash
curl -H "x-api-key: YOUR_API_KEY" https://your-app.azurecontainerapps.io/health
```

### Tool Testing
```python
from autogen_ext.tools.mcp import SSEMCPServerHTTP
from pydantic import BaseModel

class SseServerParams(BaseModel):
    url: str = "https://your-app.azurecontainerapps.io/sse"
    api_key: str = "YOUR_API_KEY"

# Test your tools...
```

## 🔑 Security

- **API Key Authentication**: All endpoints protected
- **Environment Variables**: Sensitive data in `.env`
- **Azure Secrets**: Stored in GitHub Actions secrets
- **CORS**: Configured for web access

## 📊 Monitoring

Once deployed, monitor your app in:
- **Azure Portal**: Container Apps logs and metrics
- **GitHub Actions**: Deployment history and logs
- **Application Insights**: Performance tracking (if enabled)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your MCP tools
4. Test locally
5. Submit a pull request

## 📚 Learn More

- [AutoGen Documentation](https://microsoft.github.io/autogen/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Azure Container Apps](https://docs.microsoft.com/en-us/azure/container-apps/)
- [GitHub Actions](https://docs.github.com/en/actions)

## 🆘 Troubleshooting

### Common Issues

1. **MCP server not responding**
   - Check API key is correct
   - Verify server URL is accessible
   - Check Azure Container Apps logs

2. **AutoGen tools not found**
   - Ensure MCP server is running
   - Check tool definitions match exactly
   - Verify HTTP/SSE connection

3. **Deployment failures**
   - Check GitHub Actions logs
   - Verify Azure credentials
   - Ensure Docker build succeeds

### Getting Help

- Check the GitHub Actions logs for deployment issues
- Use Azure Portal to view Container Apps logs
- Test locally first before deploying

---

**Happy coding with AutoGen + MCP! 🚀**
