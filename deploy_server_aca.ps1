# Deploy the Azure MCP server as an Azure Container App
# PowerShell version for Windows

# Ask for deployment parameters
$REGION = Read-Host "Enter Azure Region (e.g., eastus)"
$RESOURCE_GROUP = Read-Host "Enter Azure Resource Group"
$APP_NAME = Read-Host "Enter Container App Name"
$ENV_NAME = Read-Host "Enter Container App Environment Name"

# Generate a random API key (PowerShell equivalent)
$API_KEY = -join ((1..64) | ForEach {'{0:X}' -f (Get-Random -Max 16)})
Write-Host "Generated API Key: $API_KEY"

# Create resource group if it doesn't exist
try {
    az group show --name $RESOURCE_GROUP | Out-Null
    Write-Host "Resource group $RESOURCE_GROUP already exists."
} catch {
    Write-Host "Resource group $RESOURCE_GROUP does not exist. Creating..."
    az group create --name $RESOURCE_GROUP --location $REGION
}

# Deploy the container app
az containerapp up `
  -g $RESOURCE_GROUP `
  -n $APP_NAME `
  --environment $ENV_NAME `
  -l $REGION `
  --env-vars "API_KEYS=$API_KEY" `
  --source .

# Enable external ingress
az containerapp ingress enable `
  -n $APP_NAME `
  -g $RESOURCE_GROUP `
  --type external `
  --target-port 8000 `
  --transport auto

# Get the FQDN (URL) of the deployed container app
$MCP_URL = az containerapp show -n $APP_NAME -g $RESOURCE_GROUP --query "properties.configuration.ingress.fqdn" -o tsv
$MCP_URL_FULL = "https://$MCP_URL/sse"

# Print the values for the user to add to their client .env
Write-Host ""
Write-Host "========================================"
Write-Host "Add the following to your MCP client .env file:"
Write-Host ""
Write-Host "MCP_API_KEYS=`"$API_KEY`""
Write-Host "MCP_URL=`"$MCP_URL_FULL`""
Write-Host "========================================"
