# 🚀 Quick Reference - AutoGen + MCP

## 📁 Key Files
| File | Purpose |
|------|---------|
| `simple_mcp_server.py` | Core MCP server with tools |
| `simple_autogen_client.py` | AutoGen client with Azure OpenAI |
| `start_server.py` | FastAPI web wrapper |
| `test_mcp_client.py` | Direct MCP testing |
| `test_mcp_connection.py` | Web MCP testing |
| `deploy.yml` | GitHub Actions workflow |

## 🔑 Important Values
| Item | Value |
|------|-------|
| **API Key** | `B509918774DDE22A5BF94EDB4F145CB6E06F1CBCCC49D492D27FFD4AC3667A71` |
| **Azure OpenAI Endpoint** | `https://flatbitai.openai.azure.com/` |
| **Deployment Name** | `gpt4mini` |
| **Local Port** | `8000` |
| **Target Azure URL** | `https://twinagentservices.eastus.azurecontainerapps.io` |

## 🧪 Test Commands
```bash
# Test MCP server directly
python test_mcp_client.py

# Test web wrapper locally
python start_server.py
# (in another terminal)
python test_mcp_connection.py

# Test AutoGen integration
python simple_autogen_client.py

# Health check (after deployment)
curl -H "x-api-key: B509918774DDE22A5BF94EDB4F145CB6E06F1CBCCC49D492D27FFD4AC3667A71" \
     https://twinagentservices.eastus.azurecontainerapps.io/health
```

## 🛠️ Available MCP Tools
1. **hello_world** - Basic greeting with name parameter
2. **add_numbers** - Mathematical addition (a, b parameters)

## 🚀 Deployment Steps
1. **Create GitHub repo** and push code
2. **Set up Azure credentials** (see GITHUB_ACTIONS_SETUP.md)
3. **Add GitHub secrets**: `AZURE_CREDENTIALS`, `MCP_API_KEY`
4. **Push to main branch** - automatic deployment!

## 🔧 Environment Variables
```env
AZURE_OPENAI_ENDPOINT=https://flatbitai.openai.azure.com/
AZURE_OPENAI_API_KEY=6d2ef19219dd49689b0444b3f0babe1c
AZURE_OPENAI_DEPLOYMENT_NAME=gpt4mini
AZURE_OPENAI_API_VERSION=2024-02-01
MCP_API_KEYS=B509918774DDE22A5BF94EDB4F145CB6E06F1CBCCC49D492D27FFD4AC3667A71
```

## 📚 Documentation
- `README.md` - Complete project overview
- `GITHUB_ACTIONS_SETUP.md` - Step-by-step deployment guide
- `DEPLOYMENT_SUMMARY.md` - Success summary and next steps

---
*All systems tested and ready for Azure deployment! 🌟*
