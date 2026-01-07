# 🚀 Trading Platform API - Quick Reference

## Installation (2 minutes)

```bash
cd E:\trading-platform-api
.\setup.ps1                    # Windows
# OR
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
```

## Configuration (5 minutes)

```bash
# Edit .env with your credentials
# Required: COINBASE_API_KEY, COINBASE_API_SECRET, COINBASE_API_PASSPHRASE
# Optional: AZURE_LOGIN_*, OPENAI_API_KEY, etc.

python verify_system.py        # Test connections
```

## Run Application (10 seconds)

```bash
python -m uvicorn main:app --reload
# Open http://localhost:8000/docs
```

---

## API Endpoints - Quick Reference

### Health
```
GET /health              → System health status
GET /status              → All service configuration status
```

### Authentication (Azure AD)
```
GET /auth/login          → Start OAuth 2.0 flow → Returns auth URL
GET /auth/callback       → OAuth callback (redirected from Azure)
GET /auth/user           → Get current user info (pass token in header)
  Header: Authorization: Bearer <access_token>
GET /auth/calendar       → Get calendar events
GET /auth/mail           → Get emails
```

### Trading - Accounts & Products
```
GET /trading/accounts    → List all trading accounts
GET /trading/products    → List all trading pairs (BTC-USD, ETH-USD, etc.)
GET /trading/ticker/{id} → Get current price (e.g., /trading/ticker/BTC-USD)
```

### Trading - Orders
```
GET /trading/orders?product_id=BTC-USD&status=OPEN
POST /trading/orders/market
  {
    "product_id": "BTC-USD",
    "side": "BUY",           # BUY or SELL
    "quote_size": "100"      # Amount in USD
  }
POST /trading/orders/limit
  {
    "product_id": "ETH-USD",
    "side": "BUY",
    "base_size": "1.5",      # Amount of crypto
    "limit_price": "2200"    # Price per unit
  }
DELETE /trading/orders/{order_id}
GET /trading/fills?product_id=BTC-USD  → Trade history
```

---

## Configuration File Reference

### Required (for trading)
```env
COINBASE_API_KEY=...
COINBASE_API_SECRET=...
COINBASE_API_PASSPHRASE=...
COINBASE_SANDBOX_MODE=false     # Set true for testing
```

### Optional (for authentication)
```env
AZURE_LOGIN_TENANT_ID=...
AZURE_LOGIN_CLIENT_ID=...
AZURE_LOGIN_CLIENT_SECRET=...
AZURE_LOGIN_REDIRECT_URI=http://localhost:8000/auth/callback
```

### Optional (other services)
```env
OPENAI_API_KEY=...
GITHUB_API_TOKEN=...
PINECONE_API_KEY=...
BINANCE_API_KEY=...
SLACK_WEBHOOK_URL=...
DISCORD_BOT_TOKEN=...
```

---

## Common Commands

```bash
# Verify system
python verify_system.py

# Run tests
pytest tests/ -v

# Format code
black .

# Check types
mypy .

# Start server (development)
python -m uvicorn main:app --reload

# Start server (production)
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# Get help
python -c "from config import get_config; help(get_config())"
```

---

## API Examples

### Python
```python
import asyncio
from coinbase_client import CoinbaseClient, OrderSide
from config import get_config

config = get_config()
client = CoinbaseClient(
    api_key=config.coinbase.api_key,
    api_secret=config.coinbase.api_secret,
    api_passphrase=config.coinbase.api_passphrase,
    sandbox_mode=config.coinbase.sandbox_mode
)

async def main():
    # Get accounts
    accounts = await client.get_accounts()
    print(f"Accounts: {len(accounts)}")
    
    # Get BTC price
    ticker = await client.get_ticker('BTC-USD')
    print(f"BTC: ${ticker.price}")
    
    # Place order
    order = await client.place_limit_order(
        product_id='BTC-USD',
        side=OrderSide.BUY,
        base_size='0.01',
        limit_price='40000'
    )
    print(f"Order: {order.order_id}")

asyncio.run(main())
```

### cURL
```bash
# Get accounts
curl http://localhost:8000/trading/accounts

# Get ticker
curl http://localhost:8000/trading/ticker/BTC-USD

# Place order
curl -X POST http://localhost:8000/trading/orders/limit \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "ETH-USD",
    "side": "BUY",
    "base_size": "1.0",
    "limit_price": "2200"
  }'
```

### JavaScript/Fetch
```javascript
// Get accounts
fetch('http://localhost:8000/trading/accounts')
  .then(r => r.json())
  .then(data => console.log(data.accounts));

// Place order
fetch('http://localhost:8000/trading/orders/market', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    product_id: 'BTC-USD',
    side: 'BUY',
    quote_size: '100'
  })
}).then(r => r.json()).then(data => console.log(data));
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| `Port 8000 in use` | Use different port: `--port 8001` or kill process |
| `Coinbase API error` | Check credentials, verify IP whitelist, check system clock |
| `.env not loading` | Verify file is in project root, run `python verify_system.py` |
| `Auth callback fails` | Check AZURE_LOGIN_REDIRECT_URI matches registered app |
| `Signature error` | Verify API secret, check timestamp sync, verify request format |

---

## File Locations

| File | Purpose |
|------|---------|
| `config.py` | Configuration singleton |
| `azure_auth.py` | OAuth 2.0 implementation |
| `coinbase_client.py` | Trading API client |
| `main.py` | FastAPI server |
| `verify_system.py` | System test script |
| `.env` | Credentials (git-ignored) |
| `README.md` | Full documentation |
| `SETUP_GUIDE.md` | Detailed setup steps |
| `PROJECT_STATUS.md` | Project overview |

---

## Environment Info

```bash
# Check Python version
python --version          # Should be 3.8+

# Check virtual environment
which python              # Should show venv path

# Check dependencies
pip list

# Check FastAPI
python -c "import fastapi; print(fastapi.__version__)"

# Check Coinbase client
python -c "from coinbase_client import CoinbaseClient; print('OK')"
```

---

## Documentation Links

- **API Docs**: http://localhost:8000/docs (when running)
- **README**: README.md
- **Setup Guide**: SETUP_GUIDE.md
- **Project Status**: PROJECT_STATUS.md
- **Coinbase Docs**: https://docs.cdp.coinbase.com
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Azure Docs**: https://docs.microsoft.com/azure

---

## Security Checklist

- [ ] .env file is in .gitignore
- [ ] Never commit .env file
- [ ] Rotate API keys regularly
- [ ] Use IP whitelist on crypto exchange
- [ ] Enable 2FA on all accounts
- [ ] Review API permissions monthly
- [ ] Use sandbox for testing
- [ ] Keep Python/dependencies updated

---

**Status**: ✅ Ready to Use
**Version**: 1.0.0
**Last Updated**: 2026-01-06

