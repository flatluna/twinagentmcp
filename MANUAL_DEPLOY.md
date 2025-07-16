# 🚀 Azure Deployment Guide - Step by Step

## ✅ What We Have Ready:
- API Key: `B509918774DDE22A5BF94EDB4F145CB6E06F1CBCCC49D492D27FFD4AC3667A71`
- Resource Group: `Agents`
- Container App Name: `TwinAgentServices`
- Environment: `TwinagentEnv`
- Region: `eastus`

## 📋 Manual Deployment Steps:

### 1. Login to Azure (if needed):
```bash
az login
```

### 2. Deploy the Container App:
```bash
az containerapp up \
  -g Agents \
  -n TwinAgentServices \
  --environment TwinagentEnv \
  -l eastus \
  --env-vars "API_KEYS=B509918774DDE22A5BF94EDB4F145CB6E06F1CBCCC49D492D27FFD4AC3667A71" \
  --source .
```

### 3. Enable External Ingress:
```bash
az containerapp ingress enable \
  -n TwinAgentServices \
  -g Agents \
  --type external \
  --target-port 8000 \
  --transport auto
```

### 4. Get the URL:
```bash
az containerapp show -n TwinAgentServices -g Agents --query "properties.configuration.ingress.fqdn" -o tsv
```

## 🎯 Expected Result:
You should get a URL like: `twinagentservices.eastus.azurecontainerapps.io`

## 📝 Client Configuration:
Add to your client's `.env` file:
```
MCP_API_KEYS="B509918774DDE22A5BF94EDB4F145CB6E06F1CBCCC49D492D27FFD4AC3667A71"
MCP_URL="https://YOUR_URL_HERE/sse"
```

## 🧪 Test Your Deployment:
```bash
curl -H "x-api-key: B509918774DDE22A5BF94EDB4F145CB6E06F1CBCCC49D492D27FFD4AC3667A71" https://YOUR_URL_HERE/health
```

Should return: `{"status":"healthy"}`

## 🔧 Troubleshooting:
If deployment fails:
1. Check Azure CLI is logged in: `az account show`
2. Verify resource group exists: `az group show --name Agents`
3. Try creating environment first: `az containerapp env create -n TwinagentEnv -g Agents -l eastus`
