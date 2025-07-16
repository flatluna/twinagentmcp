# 🌐 Azure Portal Deployment Guide

Since Azure CLI is having connectivity issues, let's deploy through the Azure Portal.

## 📋 Information You Need:
- **API Key**: `B509918774DDE22A5BF94EDB4F145CB6E06F1CBCCC49D492D27FFD4AC3667A71`
- **Resource Group**: `Agents`
- **App Name**: `TwinAgentServices`
- **Region**: `East US`

## 🚀 Steps:

### 1. Go to Azure Portal
Visit: https://portal.azure.com

### 2. Create Container App
1. Search for "Container Apps" in the top search bar
2. Click "Create" → "Container App"
3. Fill in the basics:
   - **Subscription**: Your subscription
   - **Resource Group**: `Agents` (create if doesn't exist)
   - **Container App Name**: `TwinAgentServices`
   - **Region**: `East US`

### 3. Configure Container
1. **Container Image**: `mcr.microsoft.com/hello-world` (we'll update this)
2. **Environment Variables**:
   - Name: `API_KEYS`
   - Value: `B509918774DDE22A5BF94EDB4F145CB6E06F1CBCCC49D492D27FFD4AC3667A71`

### 4. Configure Ingress
1. Enable **Ingress**: Yes
2. **Ingress Type**: HTTP
3. **Target Port**: `8000`

### 5. Deploy
Click "Review + Create" → "Create"

## 🔄 Update with Your Code
After deployment, you'll need to update the container with your actual code. We can use GitHub Actions for this.

## 🧪 Test
Once deployed, test with:
```
https://twinagentservices.eastus.azurecontainerapps.io/health
```

## 📝 Alternative: GitHub Actions
Would you like me to create a GitHub Actions workflow instead? This might be easier and more reliable.
