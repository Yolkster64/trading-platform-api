# Trading Platform API - Endpoint Reference

## Quick Copy-Paste Examples

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. Get Service Status
```bash
curl http://localhost:8000/status
```

### 3. Get Trading Accounts
```bash
curl http://localhost:8000/trading/accounts
```

### 4. Get Available Products (Trading Pairs)
```bash
curl http://localhost:8000/trading/products
```

### 5. Get Current Price (Ticker)
```bash
curl http://localhost:8000/trading/ticker/BTC-USD
curl http://localhost:8000/trading/ticker/ETH-USD
```

### 6. Get Open Orders
```bash
curl http://localhost:8000/trading/orders
curl "http://localhost:8000/trading/orders?product_id=BTC-USD"
```

### 7. Place Market Order (Buy $100 of Bitcoin)
```bash
curl -X POST http://localhost:8000/trading/orders/market \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "BTC-USD",
    "side": "BUY",
    "quote_size": "100"
  }'
```

### 8. Place Limit Order (Buy 1.5 ETH at $2200)
```bash
curl -X POST http://localhost:8000/trading/orders/limit \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "ETH-USD",
    "side": "BUY",
    "base_size": "1.5",
    "limit_price": "2200"
  }'
```

### 9. Cancel Order
```bash
curl -X DELETE http://localhost:8000/trading/orders/{order_id}
```

### 10. Get Trade History
```bash
curl http://localhost:8000/trading/fills
curl "http://localhost:8000/trading/fills?product_id=BTC-USD"
```

### 11. Azure AD Login (Get Auth URL)
```bash
curl http://localhost:8000/auth/login
```

### 12. Get Current User Info (After Login)
```bash
curl -H "Authorization: Bearer {access_token}" \
  http://localhost:8000/auth/user
```

### 13. Get User Calendar
```bash
curl -H "Authorization: Bearer {access_token}" \
  http://localhost:8000/auth/calendar
```

### 14. Get User Emails
```bash
curl -H "Authorization: Bearer {access_token}" \
  http://localhost:8000/auth/mail
```

---

## Complete Endpoint List

### Health & Status
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | System health check |
| GET | `/status` | Service configuration status |
| GET | `/` | API information |

### Authentication (Azure AD)
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/auth/login` | Initiate OAuth flow |
| GET | `/auth/callback` | OAuth callback handler |
| GET | `/auth/user` | Get current user info |
| GET | `/auth/calendar` | Get user calendar events |
| GET | `/auth/mail` | Get user emails |

### Trading - Accounts & Products
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/trading/accounts` | List all accounts |
| GET | `/trading/products` | List all products |
| GET | `/trading/ticker/{product_id}` | Get ticker data |

### Trading - Orders
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/trading/orders` | Get open orders |
| POST | `/trading/orders/market` | Place market order |
| POST | `/trading/orders/limit` | Place limit order |
| DELETE | `/trading/orders/{order_id}` | Cancel order |

### Trading - History
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/trading/fills` | Get trade history |

---

## Python Examples

### Get Accounts
```python
import requests

response = requests.get('http://localhost:8000/trading/accounts')
accounts = response.json()
print(f"You have {len(accounts['accounts'])} accounts")
```

### Get BTC Price
```python
response = requests.get('http://localhost:8000/trading/ticker/BTC-USD')
ticker = response.json()
print(f"BTC Price: ${ticker['price']}")
```

### Place Order
```python
import requests

order_data = {
    'product_id': 'BTC-USD',
    'side': 'BUY',
    'quote_size': '100'
}

response = requests.post(
    'http://localhost:8000/trading/orders/market',
    json=order_data
)

order = response.json()
print(f"Order placed: {order['order_id']}")
```

---

## JavaScript Examples

### Get Accounts
```javascript
fetch('http://localhost:8000/trading/accounts')
  .then(r => r.json())
  .then(data => {
    console.log(`You have ${data.accounts.length} accounts`);
    data.accounts.forEach(acc => {
      console.log(`${acc.name}: ${acc.currency}`);
    });
  });
```

### Get BTC Price
```javascript
fetch('http://localhost:8000/trading/ticker/BTC-USD')
  .then(r => r.json())
  .then(ticker => {
    console.log(`BTC: $${ticker.price}`);
    console.log(`Bid: $${ticker.bid}`);
    console.log(`Ask: $${ticker.ask}`);
  });
```

### Place Order
```javascript
const orderData = {
  product_id: 'ETH-USD',
  side: 'BUY',
  base_size: '1.0',
  limit_price: '2200'
};

fetch('http://localhost:8000/trading/orders/limit', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify(orderData)
})
.then(r => r.json())
.then(order => {
  console.log(`Order placed: ${order.order_id}`);
  console.log(`Status: ${order.status}`);
});
```

---

## Important Notes

### Required Credentials
- `COINBASE_API_KEY`
- `COINBASE_API_SECRET`
- `COINBASE_API_PASSPHRASE`

### Product IDs (Trading Pairs)
- `BTC-USD` - Bitcoin
- `ETH-USD` - Ethereum
- `SOL-USD` - Solana
- And 150+ other trading pairs

### Order Side
- `BUY` - Purchase
- `SELL` - Sell

### Sandbox Mode
Set `COINBASE_SANDBOX_MODE=true` in .env to use sandbox (testing) credentials.

### Common Errors

**Error: "Coinbase not configured"**
- Solution: Add credentials to .env file

**Error: "Invalid signature"**
- Solution: Check API key, secret, and timestamp

**Error: "Product not found"**
- Solution: Use correct product ID (e.g., BTC-USD, not BTCUSD)

---

## Testing Tools

### Browser
Open http://localhost:8000/docs for interactive API testing

### Postman
1. Import endpoints to Postman
2. Set collection variables for credentials
3. Test each endpoint

### Command Line
Use provided curl examples above, or:
```bash
http POST http://localhost:8000/trading/orders/market \
  product_id=BTC-USD \
  side=BUY \
  quote_size=100
```

---

## Rate Limiting

Coinbase API limits:
- 30 requests per second for most endpoints
- 5 requests per second for order placement
- Implement backoff strategy for retries

---

## Response Formats

### Success (200)
```json
{
  "field": "value",
  "nested": {
    "data": "here"
  }
}
```

### Error (400+)
```json
{
  "detail": "Error message explaining what went wrong"
}
```

---

## Documentation Links

- **Full API Docs** (interactive): http://localhost:8000/docs
- **Alternative Docs** (ReDoc): http://localhost:8000/redoc
- **Coinbase API**: https://docs.cdp.coinbase.com
- **FastAPI**: https://fastapi.tiangolo.com

---

**Ready to trade?** Start with the examples above!

