# 🚀 GitHub Actions Deployment Setup

This guide will help you set up automatic deployment of your MCP server using GitHub Actions.

## 📋 Prerequisites

1. **GitHub Repository**: Your code needs to be in a GitHub repository
2. **Azure Subscription**: You need access to an Azure subscription

## 🔑 Setup Azure Credentials

### Step 1: Create Azure Service Principal

Run this command in Azure CLI (or Cloud Shell):

```bash
az ad sp create-for-rbac \
  --name "GitHubActions-TwinAgent" \
  --role contributor \
  --scopes /subscriptions/YOUR_SUBSCRIPTION_ID \
  --sdk-auth
```

**Replace `YOUR_SUBSCRIPTION_ID`** with your actual Azure subscription ID.

This will output JSON like:
```json
{
  "clientId": "...",
  "clientSecret": "...",
  "subscriptionId": "...",
  "tenantId": "...",
  "activeDirectoryEndpointUrl": "...",
  "resourceManagerEndpointUrl": "...",
  "activeDirectoryGraphResourceId": "...",
  "sqlManagementEndpointUrl": "...",
  "galleryEndpointUrl": "...",
  "managementEndpointUrl": "..."
}
```

### Step 2: Add GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add these secrets:

1. **AZURE_CREDENTIALS**
   - Value: The entire JSON output from Step 1

2. **MCP_API_KEY**
   - Value: `B509918774DDE22A5BF94EDB4F145CB6E06F1CBCCC49D492D27FFD4AC3667A71`
   - (Or generate a new one: `openssl rand -hex 32`)

## 🚀 Deploy Your Code

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Add MCP server deployment"
git push origin main
```

### Step 2: Watch the Deployment
1. Go to your GitHub repository
2. Click "Actions" tab
3. Watch the "Deploy MCP Server to Azure Container Apps" workflow

### Step 3: Get Your URL
After successful deployment, the workflow will output your server URL:
```
https://twinagentservices.eastus.azurecontainerapps.io
```

## 🧪 Test Your Deployment

```bash
# Health check
curl -H "x-api-key: YOUR_API_KEY" https://twinagentservices.eastus.azurecontainerapps.io/health

# Should return: {"status":"healthy"}
```

## 📝 Update Your Client

Add to your AutoGen client's `.env` file:
```env
MCP_API_KEYS="B509918774DDE22A5BF94EDB4F145CB6E06F1CBCCC49D492D27FFD4AC3667A71"
MCP_URL="https://twinagentservices.eastus.azurecontainerapps.io/sse"
```

## 🔄 Automatic Updates

Every time you push code to the `main` branch, GitHub Actions will automatically rebuild and redeploy your MCP server!

## 🛠️ Troubleshooting

### If deployment fails:
1. Check the "Actions" tab for error details
2. Verify your Azure credentials are correct
3. Make sure your Azure subscription has Container Apps enabled

### If you need to manually trigger deployment:
1. Go to Actions → "Deploy MCP Server to Azure Container Apps"
2. Click "Run workflow" → "Run workflow"

## 🎯 What's Next?

Once deployed, you can:
1. Test your MCP server from any AutoGen client
2. Add more tools to your MCP server
3. Scale your deployment as needed
4. Monitor usage in Azure Portal
