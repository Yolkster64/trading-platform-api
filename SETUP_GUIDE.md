# Trading Platform API - Complete Setup Guide

## Overview

This guide walks you through setting up the Trading Platform API with all services configured and tested.

## System Requirements

- **Python**: 3.8 or higher
- **OS**: Windows, macOS, or Linux
- **RAM**: 2GB minimum
- **Disk**: 1GB for dependencies

## Step 1: Environment Setup

### Windows Users

```powershell
# Navigate to project directory
cd E:\trading-platform-api

# Run setup script
.\setup.ps1

# If you get execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\setup.ps1
```

### macOS/Linux Users

```bash
# Navigate to project directory
cd trading-platform-api

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

## Step 2: API Credential Setup

### 2.1 OpenAI (Optional - for AI features)

1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key
4. Add to `.env`:
```env
OPENAI_API_KEY=sk-your-actual-key-here
```

### 2.2 GitHub (Optional - for code integration)

1. Go to https://github.com/settings/tokens
2. Click "Generate new token"
3. Select scopes: `repo`, `user`
4. Copy the token
5. Add to `.env`:
```env
GITHUB_API_TOKEN=ghp_your-token-here
GITHUB_OWNER=your-username
GITHUB_REPO=your-repo-name
```

### 2.3 Office 365 (Optional - for M365 service account)

1. Go to https://portal.azure.com
2. Navigate to "Azure Active Directory" → "App registrations"
3. Click "New registration"
4. Name: "Trading Platform Office365"
5. Account types: "Accounts in this organizational directory only"
6. Register app
7. Copy Application (client) ID
8. Go to "Certificates & secrets" → "New client secret"
9. Copy the secret value
10. Get Tenant ID from "Overview"
11. Add to `.env`:
```env
OFFICE365_CLIENT_ID=your-client-id
OFFICE365_CLIENT_SECRET=your-client-secret
OFFICE365_TENANT_ID=your-tenant-id
```

### 2.4 Azure AD Login (OAuth 2.0) ⭐ IMPORTANT

This enables user login with Microsoft accounts.

1. Go to https://portal.azure.com
2. Navigate to "Azure Active Directory" → "App registrations"
3. Click "New registration"
4. Fill in details:
   - Name: "Trading Platform Login"
   - Supported account types: "Accounts in any organizational directory and personal Microsoft accounts"
   - Redirect URI: `http://localhost:8000/auth/callback`
   - Click "Register"

5. Configure API Permissions:
   - Go to "API permissions"
   - Click "Add a permission"
   - Select "Microsoft Graph"
   - Select "Delegated permissions"
   - Add:
     - `openid`
     - `profile`
     - `email`
     - `offline_access` (for refresh token)
     - `Calendars.Read` (optional)
     - `Mail.Read` (optional)
   - Click "Grant admin consent"

6. Create Client Secret:
   - Go to "Certificates & secrets"
   - Click "New client secret"
   - Expires: 24 months
   - Copy the secret value (shown once)

7. Get credentials:
   - Application (Client) ID - from "Overview"
   - Client Secret - from step above
   - Tenant ID - from "Overview"

8. Add to `.env`:
```env
AZURE_LOGIN_TENANT_ID=your-tenant-id-from-overview
AZURE_LOGIN_CLIENT_ID=your-client-id-from-overview
AZURE_LOGIN_CLIENT_SECRET=your-client-secret-value
AZURE_LOGIN_REDIRECT_URI=http://localhost:8000/auth/callback
```

### 2.5 Pinecone (Optional - for vector database)

1. Go to https://www.pinecone.io
2. Create free account
3. Create index (default settings fine)
4. Copy API key and environment name
5. Add to `.env`:
```env
PINECONE_API_KEY=your-api-key
PINECONE_ENVIRONMENT=your-environment
PINECONE_INDEX_NAME=your-index-name
```

### 2.6 Binance (Optional - for crypto trading)

1. Go to https://www.binance.com/en/account/api-management
2. Create API key:
   - Label: "Trading Platform"
   - Restrictions: IP whitelist (add your IP)
   - Permissions: Spot Trading, View
3. Create secret key
4. Copy both keys
5. Add to `.env`:
```env
BINANCE_API_KEY=your-api-key
BINANCE_API_SECRET=your-api-secret
BINANCE_TESTNET=false
```

### 2.7 Coinbase Advanced Trade API ⭐ MAIN FEATURE

1. Go to https://coinbase.com/settings/api
2. Click "Create new API key"
3. Configuration:
   - Account: Select trading account
   - Permissions:
     - ✅ View account balances and history
     - ✅ Create, edit, and cancel orders
     - ✅ View orders and trades
   - Click "Create"
4. Copy these values (shown once):
   - API Key
   - Secret Key
   - Passphrase
5. (Optional) For testing, create sandbox credentials:
   - Go to https://api-sandbox.coinbase.com
   - Repeat steps 2-4 for sandbox account
6. Add to `.env`:

```env
# Production credentials
COINBASE_API_KEY=your-production-key
COINBASE_API_SECRET=your-production-secret
COINBASE_API_PASSPHRASE=your-production-passphrase

# Sandbox credentials (for testing)
COINBASE_SANDBOX_API_KEY=your-sandbox-key
COINBASE_SANDBOX_API_SECRET=your-sandbox-secret
COINBASE_SANDBOX_API_PASSPHRASE=your-sandbox-passphrase

# Set to true to use sandbox instead of production
COINBASE_SANDBOX_MODE=false
```

### 2.8 TradingView (Optional)

1. Go to https://www.tradingview.com/pine_script_api/
2. Get API key
3. Add to `.env`:
```env
TRADINGVIEW_API_KEY=your-api-key
```

### 2.9 Slack (Optional)

1. Go to https://api.slack.com/apps
2. Create new app
3. For Webhook:
   - Go to "Incoming Webhooks"
   - Click "Add New Webhook to Workspace"
   - Select channel
   - Copy Webhook URL
4. For Bot:
   - Go to "Bot Token Scopes"
   - Add: `chat:write`, `chat:write.public`
   - Install app to workspace
   - Copy bot token
5. Add to `.env`:
```env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
SLACK_BOT_TOKEN=xoxb-your-bot-token
```

### 2.10 Discord (Optional)

1. Go to https://discord.com/developers/applications
2. Create new application
3. For Bot:
   - Go to "Bot"
   - Click "Add Bot"
   - Copy token
4. For Webhook:
   - In Discord server, right-click channel → Edit Channel
   - Go to Integrations → Webhooks
   - Create webhook
   - Copy webhook URL
5. Add to `.env`:
```env
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_WEBHOOK_URL=https://discordapp.com/api/webhooks/YOUR/WEBHOOK
```

## Step 3: Verify Configuration

Run the verification script to test all configured services:

```bash
python verify_system.py
```

Expected output:
```
======================================================================
CONFIGURATION VERIFICATION
======================================================================
OpenAI               ✅ CONFIGURED
GitHub              ❌ NOT CONFIGURED
Office 365          ❌ NOT CONFIGURED
Azure Login         ✅ CONFIGURED
Pinecone            ❌ NOT CONFIGURED
Binance             ❌ NOT CONFIGURED
Coinbase            ✅ CONFIGURED
TradingView         ❌ NOT CONFIGURED
Slack               ✅ CONFIGURED
Discord             ❌ NOT CONFIGURED

======================================================================
COINBASE VERIFICATION
======================================================================
✅ Mode: PRODUCTION
✅ Base URL: https://api.coinbase.com
⏳ Testing API connectivity...
✅ Accounts API working (2 accounts)
   - Trading Account (USD)
   - Bitcoin Wallet (BTC)
✅ Products API working (150+ products)
   - BTC-USD: $42500.50
   - ETH-USD: $2250.75
✅ Ticker API working (BTC-USD: $42500.50)

======================================================================
SUMMARY REPORT
======================================================================
Configured Services: 3/10
```

## Step 4: Run the Application

### Development Mode (with auto-reload)

```bash
python -m uvicorn main:app --reload
```

Output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
✅ Application initialized
```

### Production Mode

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Step 5: Test API Endpoints

### Using Browser

1. Open http://localhost:8000/docs
2. Try endpoints:
   - GET `/health` - Should return 200
   - GET `/status` - Shows all services
   - GET `/trading/accounts` - Lists accounts

### Using cURL

```bash
# Health check
curl http://localhost:8000/health

# Get accounts
curl http://localhost:8000/trading/accounts

# Get current BTC price
curl http://localhost:8000/trading/ticker/BTC-USD

# Place test order (limit order)
curl -X POST http://localhost:8000/trading/orders/limit \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "BTC-USD",
    "side": "BUY",
    "base_size": "0.01",
    "limit_price": "40000"
  }'
```

### Using Python

```python
import requests

# Get accounts
response = requests.get('http://localhost:8000/trading/accounts')
print(response.json())

# Get ticker
response = requests.get('http://localhost:8000/trading/ticker/BTC-USD')
print(response.json())
```

## Troubleshooting

### Port 8000 Already in Use

```bash
# Find process using port 8000
# Windows:
netstat -ano | findstr :8000

# macOS/Linux:
lsof -i :8000

# Kill the process (Windows):
taskkill /PID <PID> /F

# Use different port:
python -m uvicorn main:app --port 8001
```

### "ModuleNotFoundError: No module named 'aiohttp'"

Solution:
```bash
pip install -r requirements.txt
```

### Azure Login Not Working

Check .env values:
```bash
python -c "from config import get_config; c = get_config(); print(c.azure_login.__dict__)"
```

### Coinbase API Errors

1. Check sandbox mode is correct for your credentials
2. Verify IP is not restricted in API settings
3. Check system clock (timestamp mismatch causes errors)
4. Verify product IDs use correct format (BTC-USD, not BTCUSD)

## Security Best Practices

### ✅ DO:
- [ ] Add `.env` to `.gitignore` (already done)
- [ ] Use environment variables for all credentials
- [ ] Rotate API keys regularly (quarterly minimum)
- [ ] Use IP whitelisting on API keys
- [ ] Enable 2FA on crypto exchange accounts
- [ ] Store tokens in secure vault (production)
- [ ] Review API key permissions regularly

### ❌ DON'T:
- [ ] Commit .env file to git
- [ ] Share API keys in chat or email
- [ ] Use same key for multiple environments
- [ ] Disable IP whitelisting
- [ ] Leave old API keys active

## Production Deployment

### Using Azure App Service

```bash
# Install Azure CLI
# https://docs.microsoft.com/en-us/cli/azure/install-azure-cli

# Login
az login

# Create App Service plan
az appservice plan create \
  --name trading-platform-plan \
  --resource-group my-resource-group \
  --sku B1 \
  --is-linux

# Create web app
az webapp create \
  --resource-group my-resource-group \
  --plan trading-platform-plan \
  --name trading-platform-api \
  --runtime "PYTHON|3.11"

# Set environment variables
az webapp config appsettings set \
  --resource-group my-resource-group \
  --name trading-platform-api \
  --settings \
    COINBASE_API_KEY=... \
    COINBASE_API_SECRET=... \
    ...
```

### Using Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t trading-platform-api .
docker run -p 8000:8000 \
  -e COINBASE_API_KEY=... \
  -e COINBASE_API_SECRET=... \
  trading-platform-api
```

## Next Steps

1. ✅ Start the server: `python -m uvicorn main:app --reload`
2. ✅ Open API docs: http://localhost:8000/docs
3. ✅ Try endpoints with your credentials
4. ✅ Review code in `main.py`, `coinbase_client.py`, `azure_auth.py`
5. ✅ Customize for your use case
6. ✅ Deploy to production

## Support

- **API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **GitHub**: Add issues to repository
- **Coinbase Docs**: https://docs.cdp.coinbase.com
- **Azure Docs**: https://docs.microsoft.com/azure

