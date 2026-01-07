"""
FastAPI Application - OAuth 2.0 with Azure AD and Coinbase Trading
Example of integrating Azure authentication and cryptocurrency trading.
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from config import get_config, ApplicationConfig
from azure_auth import AzureADClient, AzureADLoginManager, TokenResponse
from coinbase_client import CoinbaseClient, OrderSide

# Load environment variables
load_dotenv()

# Global instances
config: ApplicationConfig = None
azure_client: AzureADClient = None
azure_manager: AzureADLoginManager = None
coinbase_client: CoinbaseClient = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown"""
    global config, azure_client, azure_manager, coinbase_client
    
    # Startup
    config = get_config()
    
    # Initialize Azure AD
    if config.azure_login.is_configured():
        azure_client = AzureADClient(
            tenant_id=config.azure_login.tenant_id,
            client_id=config.azure_login.client_id,
            client_secret=config.azure_login.client_secret,
            redirect_uri=config.azure_login.redirect_uri
        )
        azure_manager = AzureADLoginManager(azure_client)
    
    # Initialize Coinbase
    if config.coinbase.is_configured():
        coinbase_client = CoinbaseClient(
            api_key=config.coinbase.api_key,
            api_secret=config.coinbase.api_secret,
            api_passphrase=config.coinbase.api_passphrase,
            sandbox_mode=config.coinbase.sandbox_mode,
            sandbox_api_key=config.coinbase.sandbox_api_key,
            sandbox_api_secret=config.coinbase.sandbox_api_secret,
            sandbox_api_passphrase=config.coinbase.sandbox_api_passphrase
        )
    
    print("✅ Application initialized")
    yield
    
    # Shutdown
    print("🛑 Application shutting down")


# Create FastAPI application
app = FastAPI(
    title="Trading Platform API",
    description="Enterprise AI/ML Trading Platform with OAuth 2.0 and Cryptocurrency Trading",
    version="1.0.0",
    lifespan=lifespan
)


# ============================================================================
# Health & Status Endpoints
# ============================================================================

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": config.get_status()
    }


@app.get("/status", tags=["Status"])
async def status():
    """Get current service configuration status"""
    return {
        "openai": config.openai.is_configured(),
        "github": config.github.is_configured(),
        "office365": config.office365.is_configured(),
        "azure_login": config.azure_login.is_configured(),
        "pinecone": config.pinecone.is_configured(),
        "binance": config.binance.is_configured(),
        "coinbase": config.coinbase.is_configured(),
        "tradingview": config.tradingview.is_configured(),
        "slack": config.slack.is_configured(),
        "discord": config.discord.is_configured()
    }


# ============================================================================
# Azure AD OAuth 2.0 Authentication Endpoints
# ============================================================================

@app.get("/auth/login", tags=["Authentication"])
async def login():
    """
    Initiate Azure AD login flow
    Redirects user to Microsoft login page
    """
    if not config.azure_login.is_configured():
        raise HTTPException(status_code=400, detail="Azure AD not configured")
    
    session = azure_manager.create_login_session()
    return {"auth_url": session['auth_url'], "state": session['state']}


@app.get("/auth/callback", tags=["Authentication"])
async def auth_callback(code: str = None, state: str = None, error: str = None):
    """
    OAuth 2.0 callback endpoint
    Receives authorization code from Azure AD
    """
    if error:
        raise HTTPException(status_code=400, detail=f"Auth error: {error}")
    
    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing code or state parameter")
    
    try:
        session = await azure_manager.complete_login(state, code)
        return {
            "success": True,
            "user": session['user_info'],
            "access_token": session['tokens'].access_token,
            "expires_at": session['tokens'].expires_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Login failed: {str(e)}")


@app.get("/auth/user", tags=["Authentication"])
async def get_current_user(authorization: str = None):
    """Get current user info from access token"""
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    access_token = authorization.replace('Bearer ', '')
    
    try:
        user_info = await azure_client.get_user_info(access_token)
        return user_info
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


@app.get("/auth/calendar", tags=["Authentication"])
async def get_calendar(authorization: str = None):
    """Get user's calendar events"""
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    access_token = authorization.replace('Bearer ', '')
    
    try:
        events = await azure_client.get_user_calendar(access_token)
        return {"events": events}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/auth/mail", tags=["Authentication"])
async def get_mail(authorization: str = None, top: int = 10):
    """Get user's recent emails"""
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    access_token = authorization.replace('Bearer ', '')
    
    try:
        messages = await azure_client.get_user_mail(access_token, top=top)
        return {"messages": messages}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Coinbase Trading Endpoints
# ============================================================================

@app.get("/trading/accounts", tags=["Trading"])
async def get_accounts():
    """Get all trading accounts"""
    if not config.coinbase.is_configured():
        raise HTTPException(status_code=400, detail="Coinbase not configured")
    
    try:
        accounts = await coinbase_client.get_accounts()
        return {
            "accounts": [
                {
                    "uuid": acc.uuid,
                    "name": acc.name,
                    "currency": acc.currency,
                    "available_balance": acc.available_balance,
                    "active": acc.active
                }
                for acc in accounts
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/trading/products", tags=["Trading"])
async def get_products():
    """Get available trading products (pairs)"""
    if not config.coinbase.is_configured():
        raise HTTPException(status_code=400, detail="Coinbase not configured")
    
    try:
        products = await coinbase_client.get_products()
        return {
            "products": [
                {
                    "id": prod.id,
                    "display_name": prod.display_name,
                    "price": prod.price,
                    "volume_24h": prod.volume_24h,
                    "status": prod.status
                }
                for prod in products
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/trading/ticker/{product_id}", tags=["Trading"])
async def get_ticker(product_id: str):
    """Get current ticker for a product"""
    if not config.coinbase.is_configured():
        raise HTTPException(status_code=400, detail="Coinbase not configured")
    
    try:
        ticker = await coinbase_client.get_ticker(product_id)
        return {
            "product_id": ticker.product_id,
            "price": ticker.price,
            "ask": ticker.ask,
            "bid": ticker.bid,
            "volume": ticker.volume
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/trading/orders", tags=["Trading"])
async def get_orders(product_id: str = None, status: str = "OPEN"):
    """Get open orders"""
    if not config.coinbase.is_configured():
        raise HTTPException(status_code=400, detail="Coinbase not configured")
    
    try:
        orders = await coinbase_client.get_orders(
            product_id=product_id,
            order_status=status
        )
        return {
            "orders": [
                {
                    "order_id": order.order_id,
                    "product_id": order.product_id,
                    "side": order.side,
                    "status": order.status,
                    "filled_size": order.filled_size,
                    "average_filled_price": order.average_filled_price
                }
                for order in orders
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/trading/orders/market", tags=["Trading"])
async def place_market_order(
    product_id: str,
    side: str,  # BUY or SELL
    quote_size: str
):
    """Place a market order"""
    if not config.coinbase.is_configured():
        raise HTTPException(status_code=400, detail="Coinbase not configured")
    
    try:
        order_side = OrderSide[side.upper()]
        order = await coinbase_client.place_market_order(
            product_id=product_id,
            side=order_side,
            quote_size=quote_size
        )
        return {
            "order_id": order.order_id,
            "product_id": order.product_id,
            "side": order.side,
            "status": order.status,
            "creation_time": order.creation_time
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/trading/orders/limit", tags=["Trading"])
async def place_limit_order(
    product_id: str,
    side: str,  # BUY or SELL
    base_size: str,
    limit_price: str
):
    """Place a limit order"""
    if not config.coinbase.is_configured():
        raise HTTPException(status_code=400, detail="Coinbase not configured")
    
    try:
        order_side = OrderSide[side.upper()]
        order = await coinbase_client.place_limit_order(
            product_id=product_id,
            side=order_side,
            base_size=base_size,
            limit_price=limit_price
        )
        return {
            "order_id": order.order_id,
            "product_id": order.product_id,
            "side": order.side,
            "status": order.status,
            "creation_time": order.creation_time
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/trading/orders/{order_id}", tags=["Trading"])
async def cancel_order(order_id: str):
    """Cancel an order"""
    if not config.coinbase.is_configured():
        raise HTTPException(status_code=400, detail="Coinbase not configured")
    
    try:
        success = await coinbase_client.cancel_order(order_id)
        return {"success": success, "order_id": order_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Trading Fills / History
# ============================================================================

@app.get("/trading/fills", tags=["Trading"])
async def get_fills(product_id: str = None, limit: int = 100):
    """Get trading fills (execution history)"""
    if not config.coinbase.is_configured():
        raise HTTPException(status_code=400, detail="Coinbase not configured")
    
    try:
        fills = await coinbase_client.get_fills(
            product_id=product_id,
            limit=limit
        )
        return {"fills": fills}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Root Endpoints
# ============================================================================

@app.get("/", tags=["Root"])
async def root():
    """API root - returns API information"""
    return {
        "name": "Trading Platform API",
        "version": "1.0.0",
        "description": "Enterprise AI/ML Trading Platform with OAuth 2.0 and Cryptocurrency Trading",
        "docs": "/docs",
        "redoc": "/redoc"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
