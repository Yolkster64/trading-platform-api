"""
Coinbase Advanced Trade API Client
Handles cryptocurrency trading operations and account management.
"""

import json
import hashlib
import hmac
import time
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from enum import Enum
import aiohttp
import base64


class OrderType(str, Enum):
    """Supported Coinbase order types"""
    MARKET = 'MARKET'
    LIMIT = 'LIMIT'
    STOP = 'STOP'


class OrderSide(str, Enum):
    """Order side: BUY or SELL"""
    BUY = 'BUY'
    SELL = 'SELL'


@dataclass
class CoinbaseAccount:
    """Coinbase account information"""
    uuid: str
    name: str
    currency: str
    available_balance: dict
    default: bool
    active: bool
    created_at: str
    updated_at: str


@dataclass
class CoinbaseProduct:
    """Coinbase product (trading pair) information"""
    id: str
    base_currency: str
    quote_currency: str
    base_display_symbol: str
    quote_display_symbol: str
    base_increment: str
    quote_increment: str
    display_name: str
    status: str
    price: str
    price_percentage_change_24h: str
    volume_24h: str
    volume_percentage_change_24h: str
    base_max_size: str
    base_min_size: str
    quote_max_size: str
    quote_min_size: str


@dataclass
class CoinbaseTicker:
    """Current ticker data"""
    product_id: str
    price: str
    time: str
    trade_id: str
    ask: str
    bid: str
    volume: str


@dataclass
class CoinbaseOrder:
    """Coinbase order details"""
    order_id: str
    product_id: str
    user_id: str
    order_configuration: dict
    side: str
    type: str
    time_in_force: str
    post_only: bool
    creation_time: str
    completion_time: Optional[str]
    order_type: str
    filled_size: str
    average_filled_price: str
    fee: str
    number_of_fills: int
    filled_value: str
    pending_cancel_reason: Optional[str]
    reject_reason: Optional[str]
    settled: bool
    status: str


class CoinbaseClient:
    """Coinbase Advanced Trade API Client"""
    
    BASE_URL_PRODUCTION = 'https://api.coinbase.com'
    BASE_URL_SANDBOX = 'https://api-sandbox.coinbase.com'
    
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        api_passphrase: str,
        sandbox_mode: bool = False,
        sandbox_api_key: Optional[str] = None,
        sandbox_api_secret: Optional[str] = None,
        sandbox_api_passphrase: Optional[str] = None
    ):
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_passphrase = api_passphrase
        self.sandbox_mode = sandbox_mode
        self.sandbox_api_key = sandbox_api_key
        self.sandbox_api_secret = sandbox_api_secret
        self.sandbox_api_passphrase = sandbox_api_passphrase
    
    def get_active_credentials(self) -> tuple:
        """Get currently active credentials based on mode"""
        if self.sandbox_mode:
            return (self.sandbox_api_key, self.sandbox_api_secret, self.sandbox_api_passphrase)
        return (self.api_key, self.api_secret, self.api_passphrase)
    
    def get_base_url(self) -> str:
        """Get API base URL based on mode"""
        return self.BASE_URL_SANDBOX if self.sandbox_mode else self.BASE_URL_PRODUCTION
    
    def _generate_signature(
        self,
        timestamp: str,
        method: str,
        path: str,
        body: str = ''
    ) -> tuple:
        """
        Generate HMAC-SHA256 signature for Coinbase API
        Returns: (signature, api_key)
        """
        api_key, api_secret, api_passphrase = self.get_active_credentials()
        
        # Create signature message: timestamp + method + path + body
        message = timestamp + method + path + body
        
        # HMAC-SHA256 signature
        signature = hmac.new(
            api_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        
        # Base64 encode the signature
        signature_b64 = base64.b64encode(signature).decode()
        
        return signature_b64, api_key, api_passphrase
    
    def _get_headers(self, method: str, path: str, body: str = '') -> dict:
        """Generate request headers with authentication"""
        timestamp = str(time.time())
        signature, api_key, api_passphrase = self._generate_signature(timestamp, method, path, body)
        
        return {
            'Authorization': f'Bearer {signature}',
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': api_key,
            'CB-ACCESS-PASSPHRASE': api_passphrase,
            'Content-Type': 'application/json'
        }
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict] = None
    ) -> dict:
        """Make authenticated API request"""
        url = f'{self.get_base_url()}{endpoint}'
        body = json.dumps(data) if data else ''
        headers = self._get_headers(method, endpoint, body)
        
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method,
                url,
                headers=headers,
                data=body
            ) as resp:
                response_data = await resp.json()
                
                if resp.status >= 400:
                    raise Exception(f"API Error {resp.status}: {response_data}")
                
                return response_data
    
    async def get_accounts(self) -> List[CoinbaseAccount]:
        """Get all accounts"""
        response = await self._request('GET', '/api/v1/accounts')
        
        accounts = []
        for account_data in response.get('accounts', []):
            accounts.append(CoinbaseAccount(
                uuid=account_data['uuid'],
                name=account_data['name'],
                currency=account_data['currency'],
                available_balance=account_data['available_balance'],
                default=account_data['default'],
                active=account_data['active'],
                created_at=account_data['created_at'],
                updated_at=account_data['updated_at']
            ))
        
        return accounts
    
    async def get_account(self, account_id: str) -> CoinbaseAccount:
        """Get specific account details"""
        response = await self._request('GET', f'/api/v1/accounts/{account_id}')
        
        return CoinbaseAccount(
            uuid=response['uuid'],
            name=response['name'],
            currency=response['currency'],
            available_balance=response['available_balance'],
            default=response['default'],
            active=response['active'],
            created_at=response['created_at'],
            updated_at=response['updated_at']
        )
    
    async def get_products(self) -> List[CoinbaseProduct]:
        """Get all available products (trading pairs)"""
        response = await self._request('GET', '/api/v1/products')
        
        products = []
        for product_data in response.get('products', []):
            products.append(CoinbaseProduct(
                id=product_data['id'],
                base_currency=product_data['base_currency'],
                quote_currency=product_data['quote_currency'],
                base_display_symbol=product_data['base_display_symbol'],
                quote_display_symbol=product_data['quote_display_symbol'],
                base_increment=product_data['base_increment'],
                quote_increment=product_data['quote_increment'],
                display_name=product_data['display_name'],
                status=product_data['status'],
                price=product_data['price'],
                price_percentage_change_24h=product_data['price_percentage_change_24h'],
                volume_24h=product_data['volume_24h'],
                volume_percentage_change_24h=product_data['volume_percentage_change_24h'],
                base_max_size=product_data['base_max_size'],
                base_min_size=product_data['base_min_size'],
                quote_max_size=product_data['quote_max_size'],
                quote_min_size=product_data['quote_min_size']
            ))
        
        return products
    
    async def get_product(self, product_id: str) -> CoinbaseProduct:
        """Get specific product details"""
        response = await self._request('GET', f'/api/v1/products/{product_id}')
        
        return CoinbaseProduct(
            id=response['id'],
            base_currency=response['base_currency'],
            quote_currency=response['quote_currency'],
            base_display_symbol=response['base_display_symbol'],
            quote_display_symbol=response['quote_display_symbol'],
            base_increment=response['base_increment'],
            quote_increment=response['quote_increment'],
            display_name=response['display_name'],
            status=response['status'],
            price=response['price'],
            price_percentage_change_24h=response['price_percentage_change_24h'],
            volume_24h=response['volume_24h'],
            volume_percentage_change_24h=response['volume_percentage_change_24h'],
            base_max_size=response['base_max_size'],
            base_min_size=response['base_min_size'],
            quote_max_size=response['quote_max_size'],
            quote_min_size=response['quote_min_size']
        )
    
    async def place_market_order(
        self,
        product_id: str,
        side: OrderSide,
        quote_size: str
    ) -> CoinbaseOrder:
        """Place market order (quote_size = amount in USD)"""
        order_config = {
            'market_market_ioc': {
                'quote_size': quote_size
            }
        }
        
        data = {
            'client_order_id': f'market_{product_id}_{int(time.time())}',
            'product_id': product_id,
            'side': side.value,
            'order_configuration': order_config
        }
        
        response = await self._request('POST', '/api/v1/brokerage/orders', data)
        return self._parse_order_response(response)
    
    async def place_limit_order(
        self,
        product_id: str,
        side: OrderSide,
        base_size: str,
        limit_price: str
    ) -> CoinbaseOrder:
        """Place limit order (base_size = amount of crypto)"""
        order_config = {
            'limit_limit_gtc': {
                'base_size': base_size,
                'limit_price': limit_price
            }
        }
        
        data = {
            'client_order_id': f'limit_{product_id}_{int(time.time())}',
            'product_id': product_id,
            'side': side.value,
            'order_configuration': order_config
        }
        
        response = await self._request('POST', '/api/v1/brokerage/orders', data)
        return self._parse_order_response(response)
    
    async def place_stop_order(
        self,
        product_id: str,
        side: OrderSide,
        base_size: str,
        limit_price: str,
        stop_price: str
    ) -> CoinbaseOrder:
        """Place stop order"""
        order_config = {
            'stop_limit_stop_limit_gtc': {
                'base_size': base_size,
                'limit_price': limit_price,
                'stop_price': stop_price
            }
        }
        
        data = {
            'client_order_id': f'stop_{product_id}_{int(time.time())}',
            'product_id': product_id,
            'side': side.value,
            'order_configuration': order_config
        }
        
        response = await self._request('POST', '/api/v1/brokerage/orders', data)
        return self._parse_order_response(response)
    
    async def get_orders(
        self,
        product_id: Optional[str] = None,
        order_status: str = 'OPEN'
    ) -> List[CoinbaseOrder]:
        """Get orders (default: open orders)"""
        params = f'?order_status={order_status}'
        if product_id:
            params += f'&product_id={product_id}'
        
        response = await self._request('GET', f'/api/v1/brokerage/orders/batch{params}')
        
        orders = []
        for order_data in response.get('orders', []):
            orders.append(self._parse_order_data(order_data))
        
        return orders
    
    async def get_order(self, order_id: str) -> CoinbaseOrder:
        """Get specific order details"""
        response = await self._request('GET', f'/api/v1/brokerage/orders/{order_id}')
        return self._parse_order_data(response['order'])
    
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        await self._request('POST', f'/api/v1/brokerage/orders/{order_id}/cancel', {})
        return True
    
    async def get_fills(
        self,
        product_id: Optional[str] = None,
        limit: int = 100
    ) -> list:
        """Get trade fills/history"""
        params = f'?limit={limit}'
        if product_id:
            params += f'&product_id={product_id}'
        
        response = await self._request('GET', f'/api/v1/brokerage/orders/historical/fills{params}')
        return response.get('fills', [])
    
    async def get_ticker(self, product_id: str) -> CoinbaseTicker:
        """Get current ticker data"""
        response = await self._request('GET', f'/api/v1/products/{product_id}/ticker')
        
        return CoinbaseTicker(
            product_id=product_id,
            price=response.get('price', '0'),
            time=response.get('time', ''),
            trade_id=response.get('trade_id', ''),
            ask=response.get('ask', '0'),
            bid=response.get('bid', '0'),
            volume=response.get('volume', '0')
        )
    
    def _parse_order_response(self, response: dict) -> CoinbaseOrder:
        """Parse order response"""
        order_data = response.get('order', response)
        return self._parse_order_data(order_data)
    
    def _parse_order_data(self, order_data: dict) -> CoinbaseOrder:
        """Parse order data dict into CoinbaseOrder"""
        return CoinbaseOrder(
            order_id=order_data.get('order_id', ''),
            product_id=order_data.get('product_id', ''),
            user_id=order_data.get('user_id', ''),
            order_configuration=order_data.get('order_configuration', {}),
            side=order_data.get('side', ''),
            type=order_data.get('type', ''),
            time_in_force=order_data.get('time_in_force', ''),
            post_only=order_data.get('post_only', False),
            creation_time=order_data.get('creation_time', ''),
            completion_time=order_data.get('completion_time'),
            order_type=order_data.get('order_type', ''),
            filled_size=order_data.get('filled_size', '0'),
            average_filled_price=order_data.get('average_filled_price', '0'),
            fee=order_data.get('fee', '0'),
            number_of_fills=order_data.get('number_of_fills', 0),
            filled_value=order_data.get('filled_value', '0'),
            pending_cancel_reason=order_data.get('pending_cancel_reason'),
            reject_reason=order_data.get('reject_reason'),
            settled=order_data.get('settled', False),
            status=order_data.get('status', '')
        )


# Example usage
if __name__ == '__main__':
    import asyncio
    
    async def example():
        client = CoinbaseClient(
            api_key='your-api-key',
            api_secret='your-api-secret',
            api_passphrase='your-api-passphrase',
            sandbox_mode=True,
            sandbox_api_key='your-sandbox-api-key',
            sandbox_api_secret='your-sandbox-api-secret',
            sandbox_api_passphrase='your-sandbox-api-passphrase'
        )
        
        try:
            # Get accounts
            accounts = await client.get_accounts()
            print(f"Accounts: {len(accounts)}")
            
            # Get products
            products = await client.get_products()
            print(f"Products: {len(products)}")
            
            # Get ticker
            ticker = await client.get_ticker('BTC-USD')
            print(f"BTC-USD Price: {ticker.price}")
        except Exception as e:
            print(f"Error: {e}")
    
    asyncio.run(example())
