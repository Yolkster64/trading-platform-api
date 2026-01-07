# 🚀 Trading Platform API

Enterprise AI/ML Trading Platform with OAuth 2.0 Authentication and Cryptocurrency Trading

## Features

- ✅ **Unified Configuration System** - Centralized API credential management
- ✅ **Azure AD OAuth 2.0** - Secure user authentication with Microsoft
- ✅ **Coinbase Advanced Trade API** - Cryptocurrency trading (orders, accounts, products)
- ✅ **Multi-Exchange Support** - Binance and Coinbase trading
- ✅ **FastAPI Integration** - Production-ready REST API with async support
- ✅ **Comprehensive Documentation** - Setup guides and examples
- ✅ **Security Best Practices** - Environment variables, .gitignore, credential protection

## Project Structure

```
trading-platform-api/
├── config.py                 # Unified configuration system (singleton)
├── azure_auth.py             # Azure AD OAuth 2.0 authentication
├── coinbase_client.py        # Coinbase Advanced Trade API client
├── main.py                   # FastAPI application
├── verify_system.py          # System verification script
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (DO NOT COMMIT)
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## Quick Start

### 1. Installation

```bash
# Clone repository
cd trading-platform-api

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy .env template and add your credentials
cp .env .env.local

# Edit .env with your API keys
# - OpenAI: https://platform.openai.com/api-keys
# - GitHub: https://github.com/settings/tokens
# - Azure: https://portal.azure.com
# - Coinbase: https://coinbase.com/settings/api
```

### 3. Verify System

```bash
python verify_system.py
```

Expected output:
```
✅ Configuration Verification
OpenAI               ❌ NOT CONFIGURED
GitHub              ❌ NOT CONFIGURED
Azure Login         ✅ CONFIGURED
Coinbase            ✅ CONFIGURED

✅ VERIFICATION COMPLETE - System is ready!
```

### 4. Run FastAPI Server

```bash
# Development
python -m uvicorn main:app --reload

# Production
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Access API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Health & Status

```http
GET /health          # System health check
GET /status          # Service configuration status
```

### Azure AD Authentication

```http
GET /auth/login                    # Initiate OAuth flow
GET /auth/callback?code=...        # OAuth callback handler
GET /auth/user                     # Get current user info
GET /auth/calendar                 # Get user calendar events
GET /auth/mail                     # Get user emails
```

### Trading - Accounts & Products

```http
GET /trading/accounts              # Get all accounts
GET /trading/products              # Get available trading pairs
GET /trading/ticker/{product_id}   # Get current price
```

### Trading - Orders

```http
GET /trading/orders                # Get open orders
POST /trading/orders/market         # Place market order
POST /trading/orders/limit          # Place limit order
DELETE /trading/orders/{order_id}   # Cancel order
GET /trading/fills                 # Get trade history
```

## Configuration Reference

### Services

| Service | Type | Config File | Required |
|---------|------|-------------|----------|
| OpenAI | LLM | OPENAI_API_KEY | Optional |
| GitHub | Source Control | GITHUB_* | Optional |
| Office 365 | Service Account | OFFICE365_* | Optional |
| Azure Login | User Auth | AZURE_LOGIN_* | Optional |
| Pinecone | Vector DB | PINECONE_* | Optional |
| Binance | Trading | BINANCE_* | Optional |
| Coinbase | Trading | COINBASE_* | Optional |
| TradingView | Data | TRADINGVIEW_API_KEY | Optional |
| Slack | Notifications | SLACK_* | Optional |
| Discord | Notifications | DISCORD_* | Optional |

### Coinbase Setup

1. Go to https://coinbase.com/settings/api
2. Create new API key with scopes: `account:read`, `order:write`, `order:read`
3. Copy API Key, API Secret, API Passphrase
4. Add to .env file:

```env
COINBASE_API_KEY=your-key
COINBASE_API_SECRET=your-secret
COINBASE_API_PASSPHRASE=your-passphrase
COINBASE_SANDBOX_MODE=false
```

### Azure AD Setup

1. Go to https://portal.azure.com
2. Create or select Azure AD tenant
3. Register new application
4. Add API permissions: `User.Read`, `Calendars.Read`, `Mail.Read`, `offline_access`
5. Create client secret
6. Add to .env file:

```env
AZURE_LOGIN_TENANT_ID=your-tenant-id
AZURE_LOGIN_CLIENT_ID=your-client-id
AZURE_LOGIN_CLIENT_SECRET=your-client-secret
AZURE_LOGIN_REDIRECT_URI=http://localhost:8000/auth/callback
```

## Security Considerations

### ⚠️ Never Commit Credentials

1. **Always add `.env` to `.gitignore`** (already included)
2. **Use environment variables** for production
3. **Rotate API keys regularly**
4. **Use API key restrictions** (IP whitelist, scopes)
5. **Store secrets in secure vaults** (Azure Key Vault, HashiCorp Vault)

### Production Recommendations

```python
# Use Azure Key Vault in production
from azure.keyvault.secrets import SecretClient

client = SecretClient(vault_url=vault_url, credential=credential)
api_key = client.get_secret("coinbase-api-key").value
```

## Examples

### Python - Get Account Balance

```python
import asyncio
from config import get_config
from coinbase_client import CoinbaseClient

async def main():
    config = get_config()
    client = CoinbaseClient(
        api_key=config.coinbase.api_key,
        api_secret=config.coinbase.api_secret,
        api_passphrase=config.coinbase.api_passphrase,
        sandbox_mode=config.coinbase.sandbox_mode,
    )
    
    accounts = await client.get_accounts()
    for account in accounts:
        print(f"{account.name}: {account.available_balance}")

asyncio.run(main())
```

### Python - Place Market Order

```python
from coinbase_client import OrderSide

# Buy $100 of Bitcoin
order = await client.place_market_order(
    product_id='BTC-USD',
    side=OrderSide.BUY,
    quote_size='100'
)
print(f"Order {order.order_id} created: {order.status}")
```

### cURL - Get Ticker

```bash
curl -X GET "http://localhost:8000/trading/ticker/BTC-USD" \
  -H "accept: application/json"

# Response
{
  "product_id": "BTC-USD",
  "price": "42500.50",
  "bid": "42500.00",
  "ask": "42501.00",
  "volume": "1234.56"
}
```

### cURL - Place Limit Order

```bash
curl -X POST "http://localhost:8000/trading/orders/limit" \
  -H "Content-Type: application/json" \
  -d {
    "product_id": "ETH-USD",
    "side": "BUY",
    "base_size": "1.5",
    "limit_price": "2200.00"
  }

# Response
{
  "order_id": "550e8400-e29b-41d4-a716-446655440000",
  "product_id": "ETH-USD",
  "side": "BUY",
  "status": "PENDING",
  "creation_time": "2024-01-06T12:00:00Z"
}
```

## Troubleshooting

### "Coinbase not configured" Error

Solution: Ensure COINBASE_API_KEY, COINBASE_API_SECRET, and COINBASE_API_PASSPHRASE are set in .env

```bash
# Verify configuration
python -c "from config import get_config; c = get_config(); print(c.get_status())"
```

### "Invalid signature" Error

Common causes:
1. Wrong API secret
2. Timestamp mismatch (check system clock)
3. Incorrect request path or body

### "Auth failed" Error

Solution: Verify Azure AD credentials in .env:
```bash
python verify_system.py
```

## Development

### Run Tests

```bash
pytest tests/ -v
```

### Code Quality

```bash
# Format code
black .

# Lint
flake8 .

# Type checking
mypy .
```

## Dependencies

- **aiohttp** - Async HTTP client
- **fastapi** - Web framework
- **pydantic** - Data validation
- **PyJWT** - JWT token handling
- **python-binance** - Binance API
- **requests** - HTTP client

See `requirements.txt` for complete list and versions.

## License

MIT License - See LICENSE file

## Support

For issues and questions:
1. Check troubleshooting section above
2. Review API documentation: http://localhost:8000/docs
3. Check environment variables: `python verify_system.py`

## Roadmap

- [ ] Database persistence for trades/orders
- [ ] Webhook support for order notifications
- [ ] Multi-account trading strategies
- [ ] Real-time price streaming (WebSocket)
- [ ] Backtesting engine
- [ ] Machine learning signal generation
- [ ] Advanced authentication (MFA, SAML)
- [ ] Rate limiting and retry logic

