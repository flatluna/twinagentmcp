# 🤖 TwinAgent MCP - AutoGen + Model Context Protocol

A powerful integration of Microsoft AutoGen with Model Context Protocol (MCP) for Azure deployment.

## 🎯 What This Does

This project demonstrates how to:
- Create an MCP server with custom tools
- Integrate MCP tools with AutoGen agents
- Deploy MCP servers to Azure for remote access
- Use GitHub Actions for automated deployment

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
    │ Azure   │             │   MCP   │             │  HTTP/  │
    │ OpenAI  │             │ Server  │             │   SSE   │
    └─────────┘             └─────────┘             └─────────┘
```

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone <your-repo>
cd TwinagentMCP
python -m venv twinagentapp
.\twinagentapp\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment
Create `.env` file:
```env
AZURE_OPENAI_ENDPOINT=https://flatbitai.openai.azure.com/
AZURE_OPENAI_API_KEY=6d2ef19219dd49689b0444b3f0babe1c
AZURE_OPENAI_DEPLOYMENT_NAME=gpt4mini
AZURE_OPENAI_API_VERSION=2024-02-01
MCP_API_KEYS=B509918774DDE22A5BF94EDB4F145CB6E06F1CBCCC49D492D27FFD4AC3667A71
```

### 3. Test Locally
```bash
# Test MCP server directly
python test_mcp_client.py

# Test web wrapper
python start_server.py
# In another terminal:
python test_mcp_connection.py

# Test AutoGen integration
python simple_autogen_client.py
```

### 4. Deploy to Azure
Follow [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md) for automated deployment.

## 📁 Project Structure

```
TwinagentMCP/
├── 📄 simple_mcp_server.py        # Core MCP server with tools
├── 📄 simple_autogen_client.py    # AutoGen client with MCP integration
├── 📄 start_server.py             # FastAPI wrapper for deployment
├── 📄 api_key_auth.py             # Authentication middleware
├── 📄 test_mcp_client.py          # Direct MCP testing
├── 📄 test_mcp_connection.py      # Web MCP testing
├── 📄 requirements.txt            # Python dependencies
├── 📄 Dockerfile                  # Container configuration
├── 📄 .env                        # Environment variables
├── 📁 .github/workflows/          # GitHub Actions
│   └── 📄 deploy.yml              # Deployment workflow
├── 📄 GITHUB_ACTIONS_SETUP.md     # Deployment guide
└── 📄 README.md                   # This file
```

## 🛠️ Available MCP Tools

### 1. Hello World
- **Function**: `hello_world`
- **Purpose**: Basic greeting with personalization
- **Example**: `Hello, World! Welcome to the MCP server, Alice!`

### 2. Add Numbers
- **Function**: `add_numbers`
- **Purpose**: Mathematical addition
- **Parameters**: `a` (number), `b` (number)
- **Example**: `add_numbers(5, 3)` → `8`

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

2. **Implement the function**:
```python
async def handle_call_tool(self, request):
    # ... existing code ...
    elif tool_name == "your_tool_name":
        param1 = arguments.get("param1")
        result = your_function_logic(param1)
        return create_call_tool_result([{"type": "text", "text": result}])
```

3. **Test locally**, then deploy!

## 🚀 Deployment Options

### Option 1: GitHub Actions (Recommended)
- Automatic deployment on code push
- Follows [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md)
- Handles Azure Container Apps setup

### Option 2: Manual Azure CLI
```bash
az containerapp up \
  --name twinagentservices \
  --source . \
  --resource-group twinagent-rg \
  --environment twinagent-env \
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
