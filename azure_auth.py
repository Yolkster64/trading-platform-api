"""
Azure AD OAuth 2.0 Authentication Module
Handles user login and Microsoft Graph API integration.
"""

import json
import base64
import hashlib
import secrets
import hmac
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import aiohttp
import jwt
from urllib.parse import urlencode, parse_qs, urlparse


@dataclass
class TokenResponse:
    """Azure AD Token Response"""
    access_token: str
    refresh_token: Optional[str] = None
    expires_in: int = 3600
    token_type: str = 'Bearer'
    scope: str = ''
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    @property
    def expires_at(self) -> datetime:
        """Calculate expiration time"""
        return self.created_at + timedelta(seconds=self.expires_in)
    
    def is_expired(self) -> bool:
        """Check if token has expired"""
        return datetime.utcnow() >= self.expires_at
    
    def is_expiring_soon(self, threshold_seconds: int = 300) -> bool:
        """Check if token is expiring within threshold"""
        return (self.expires_at - datetime.utcnow()).total_seconds() < threshold_seconds


class AzureADClient:
    """Azure AD OAuth 2.0 Client"""
    
    def __init__(self, tenant_id: str, client_id: str, client_secret: str, redirect_uri: str):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        
        self.authority_url = f'https://login.microsoftonline.com/{tenant_id}'
        self.token_endpoint = f'{self.authority_url}/oauth2/v2.0/token'
        self.authorize_endpoint = f'{self.authority_url}/oauth2/v2.0/authorize'
        self.graph_api_url = 'https://graph.microsoft.com/v1.0'
    
    def generate_auth_url(self, scopes: list = None, state: str = None, nonce: str = None) -> tuple:
        """
        Generate OAuth authorization URL
        Returns: (auth_url, state, nonce)
        """
        if scopes is None:
            scopes = ['openid', 'profile', 'email', 'offline_access']
        
        if state is None:
            state = secrets.token_urlsafe(32)
        
        if nonce is None:
            nonce = secrets.token_urlsafe(32)
        
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': ' '.join(scopes),
            'state': state,
            'nonce': nonce,
            'prompt': 'select_account'
        }
        
        auth_url = f"{self.authorize_endpoint}?{urlencode(params)}"
        return auth_url, state, nonce
    
    async def get_token_from_code(self, code: str) -> TokenResponse:
        """Exchange authorization code for tokens"""
        async with aiohttp.ClientSession() as session:
            data = {
                'client_id': self.client_id,
                'scope': 'https://graph.microsoft.com/.default offline_access',
                'code': code,
                'redirect_uri': self.redirect_uri,
                'grant_type': 'authorization_code',
                'client_secret': self.client_secret
            }
            
            async with session.post(self.token_endpoint, data=data) as resp:
                if resp.status != 200:
                    raise Exception(f"Token exchange failed: {await resp.text()}")
                
                token_data = await resp.json()
                return TokenResponse(
                    access_token=token_data['access_token'],
                    refresh_token=token_data.get('refresh_token'),
                    expires_in=int(token_data.get('expires_in', 3600)),
                    token_type=token_data.get('token_type', 'Bearer')
                )
    
    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token"""
        async with aiohttp.ClientSession() as session:
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': refresh_token,
                'grant_type': 'refresh_token',
                'scope': 'https://graph.microsoft.com/.default offline_access'
            }
            
            async with session.post(self.token_endpoint, data=data) as resp:
                if resp.status != 200:
                    raise Exception(f"Token refresh failed: {await resp.text()}")
                
                token_data = await resp.json()
                return TokenResponse(
                    access_token=token_data['access_token'],
                    refresh_token=token_data.get('refresh_token', refresh_token),
                    expires_in=int(token_data.get('expires_in', 3600))
                )
    
    def decode_id_token(self, id_token: str, verify: bool = False) -> Dict[str, Any]:
        """
        Decode ID token (JWT)
        In production, verify signature against Azure's public keys.
        """
        try:
            decoded = jwt.decode(
                id_token,
                options={"verify_signature": False}
            )
            return decoded
        except jwt.DecodeError as e:
            raise Exception(f"Failed to decode ID token: {str(e)}")
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get current user information from Microsoft Graph"""
        headers = {'Authorization': f'Bearer {access_token}'}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{self.graph_api_url}/me', headers=headers) as resp:
                if resp.status != 200:
                    raise Exception(f"Failed to get user info: {await resp.text()}")
                return await resp.json()
    
    async def get_user_calendar(self, access_token: str) -> list:
        """Get user's calendar events"""
        headers = {'Authorization': f'Bearer {access_token}'}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f'{self.graph_api_url}/me/calendarview?startDateTime={datetime.utcnow().isoformat()}Z&endDateTime={(datetime.utcnow() + timedelta(days=7)).isoformat()}Z',
                headers=headers
            ) as resp:
                if resp.status != 200:
                    raise Exception(f"Failed to get calendar: {await resp.text()}")
                data = await resp.json()
                return data.get('value', [])
    
    async def get_user_mail(self, access_token: str, top: int = 10) -> list:
        """Get user's recent emails"""
        headers = {'Authorization': f'Bearer {access_token}'}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f'{self.graph_api_url}/me/messages?$top={top}',
                headers=headers
            ) as resp:
                if resp.status != 200:
                    raise Exception(f"Failed to get mail: {await resp.text()}")
                data = await resp.json()
                return data.get('value', [])


class AzureADLoginManager:
    """Session management for Azure AD logins"""
    
    def __init__(self, client: AzureADClient):
        self.client = client
        self.sessions: Dict[str, Dict[str, Any]] = {}
    
    def create_login_session(self) -> Dict[str, Any]:
        """Create new login session with state/nonce"""
        auth_url, state, nonce = self.client.generate_auth_url()
        
        session = {
            'state': state,
            'nonce': nonce,
            'auth_url': auth_url,
            'created_at': datetime.utcnow(),
            'completed': False,
            'user_info': None,
            'tokens': None
        }
        
        self.sessions[state] = session
        return session
    
    async def complete_login(self, state: str, code: str) -> Dict[str, Any]:
        """Complete login with authorization code"""
        if state not in self.sessions:
            raise ValueError("Invalid state parameter - session not found")
        
        session = self.sessions[state]
        
        try:
            # Exchange code for tokens
            tokens = await self.client.get_token_from_code(code)
            
            # Get user info
            user_info = await self.client.get_user_info(tokens.access_token)
            
            # Update session
            session['completed'] = True
            session['tokens'] = tokens
            session['user_info'] = user_info
            
            return session
        except Exception as e:
            raise Exception(f"Login completion failed: {str(e)}")
    
    def get_session(self, state: str) -> Optional[Dict[str, Any]]:
        """Retrieve session by state"""
        return self.sessions.get(state)
    
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Remove expired sessions"""
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        expired_states = [
            state for state, session in self.sessions.items()
            if session['created_at'] < cutoff_time
        ]
        
        for state in expired_states:
            del self.sessions[state]
        
        return len(expired_states)


# Example usage
if __name__ == '__main__':
    import asyncio
    
    async def example():
        client = AzureADClient(
            tenant_id='your-tenant-id',
            client_id='your-client-id',
            client_secret='your-client-secret',
            redirect_uri='http://localhost:8000/auth/callback'
        )
        
        # Generate auth URL
        auth_url, state, nonce = client.generate_auth_url()
        print(f"Auth URL: {auth_url}")
        print(f"State: {state}")
        print(f"Nonce: {nonce}")
    
    asyncio.run(example())
