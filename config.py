"""
Enterprise AI/ML Trading Platform - Unified Configuration System
Singleton pattern for centralized API credential and service management.
"""

import os
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import json


@dataclass
class OpenAIConfig:
    """OpenAI API Configuration"""
    api_key: Optional[str] = None
    
    def is_configured(self) -> bool:
        return bool(self.api_key)


@dataclass
class GitHubConfig:
    """GitHub API Configuration"""
    api_token: Optional[str] = None
    owner: Optional[str] = None
    repo: Optional[str] = None
    
    def is_configured(self) -> bool:
        return bool(self.api_token and self.owner and self.repo)


@dataclass
class Office365Config:
    """Office 365 / Microsoft 365 Configuration (Service Account)"""
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    tenant_id: Optional[str] = None
    
    def is_configured(self) -> bool:
        return bool(self.client_id and self.client_secret and self.tenant_id)


@dataclass
class AzureLoginConfig:
    """Azure AD Login Configuration (User Authentication via OAuth 2.0)"""
    tenant_id: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    redirect_uri: Optional[str] = None
    
    def is_configured(self) -> bool:
        return bool(self.tenant_id and self.client_id and self.client_secret and self.redirect_uri)


@dataclass
class PineconeConfig:
    """Pinecone Vector Database Configuration"""
    api_key: Optional[str] = None
    environment: Optional[str] = None
    index_name: Optional[str] = None
    
    def is_configured(self) -> bool:
        return bool(self.api_key and self.environment and self.index_name)


@dataclass
class BinanceConfig:
    """Binance Cryptocurrency Exchange Configuration"""
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    testnet: bool = False
    
    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_secret)


@dataclass
class CoinbaseConfig:
    """Coinbase Advanced Trade API Configuration"""
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    api_passphrase: Optional[str] = None
    sandbox_mode: bool = False
    sandbox_api_key: Optional[str] = None
    sandbox_api_secret: Optional[str] = None
    sandbox_api_passphrase: Optional[str] = None
    
    def is_configured(self) -> bool:
        if self.sandbox_mode:
            return bool(self.sandbox_api_key and self.sandbox_api_secret and self.sandbox_api_passphrase)
        return bool(self.api_key and self.api_secret and self.api_passphrase)
    
    def get_active_credentials(self) -> tuple:
        """Returns (api_key, api_secret, api_passphrase) based on current mode"""
        if self.sandbox_mode:
            return (self.sandbox_api_key, self.sandbox_api_secret, self.sandbox_api_passphrase)
        return (self.api_key, self.api_secret, self.api_passphrase)


@dataclass
class TradingViewConfig:
    """TradingView API Configuration"""
    api_key: Optional[str] = None
    
    def is_configured(self) -> bool:
        return bool(self.api_key)


@dataclass
class SlackConfig:
    """Slack Bot Configuration"""
    webhook_url: Optional[str] = None
    bot_token: Optional[str] = None
    
    def is_configured(self) -> bool:
        return bool(self.webhook_url or self.bot_token)


@dataclass
class DiscordConfig:
    """Discord Bot Configuration"""
    bot_token: Optional[str] = None
    webhook_url: Optional[str] = None
    
    def is_configured(self) -> bool:
        return bool(self.bot_token or self.webhook_url)


@dataclass
class ApplicationConfig:
    """Master Application Configuration - Singleton"""
    openai: OpenAIConfig = field(default_factory=OpenAIConfig)
    github: GitHubConfig = field(default_factory=GitHubConfig)
    office365: Office365Config = field(default_factory=Office365Config)
    azure_login: AzureLoginConfig = field(default_factory=AzureLoginConfig)
    pinecone: PineconeConfig = field(default_factory=PineconeConfig)
    binance: BinanceConfig = field(default_factory=BinanceConfig)
    coinbase: CoinbaseConfig = field(default_factory=CoinbaseConfig)
    tradingview: TradingViewConfig = field(default_factory=TradingViewConfig)
    slack: SlackConfig = field(default_factory=SlackConfig)
    discord: DiscordConfig = field(default_factory=DiscordConfig)
    
    def __post_init__(self):
        """Initialize all services from environment variables"""
        self._load_all_services()
    
    def _load_all_services(self):
        """Load configuration for all services"""
        self.openai = OpenAIConfig(
            api_key=os.getenv('OPENAI_API_KEY')
        )
        
        self.github = GitHubConfig(
            api_token=os.getenv('GITHUB_API_TOKEN'),
            owner=os.getenv('GITHUB_OWNER'),
            repo=os.getenv('GITHUB_REPO')
        )
        
        self.office365 = Office365Config(
            client_id=os.getenv('OFFICE365_CLIENT_ID'),
            client_secret=os.getenv('OFFICE365_CLIENT_SECRET'),
            tenant_id=os.getenv('OFFICE365_TENANT_ID')
        )
        
        self.azure_login = AzureLoginConfig(
            tenant_id=os.getenv('AZURE_LOGIN_TENANT_ID'),
            client_id=os.getenv('AZURE_LOGIN_CLIENT_ID'),
            client_secret=os.getenv('AZURE_LOGIN_CLIENT_SECRET'),
            redirect_uri=os.getenv('AZURE_LOGIN_REDIRECT_URI')
        )
        
        self.pinecone = PineconeConfig(
            api_key=os.getenv('PINECONE_API_KEY'),
            environment=os.getenv('PINECONE_ENVIRONMENT'),
            index_name=os.getenv('PINECONE_INDEX_NAME')
        )
        
        self.binance = BinanceConfig(
            api_key=os.getenv('BINANCE_API_KEY'),
            api_secret=os.getenv('BINANCE_API_SECRET'),
            testnet=os.getenv('BINANCE_TESTNET', 'false').lower() == 'true'
        )
        
        self.coinbase = CoinbaseConfig(
            api_key=os.getenv('COINBASE_API_KEY'),
            api_secret=os.getenv('COINBASE_API_SECRET'),
            api_passphrase=os.getenv('COINBASE_API_PASSPHRASE'),
            sandbox_mode=os.getenv('COINBASE_SANDBOX_MODE', 'false').lower() == 'true',
            sandbox_api_key=os.getenv('COINBASE_SANDBOX_API_KEY'),
            sandbox_api_secret=os.getenv('COINBASE_SANDBOX_API_SECRET'),
            sandbox_api_passphrase=os.getenv('COINBASE_SANDBOX_API_PASSPHRASE')
        )
        
        self.tradingview = TradingViewConfig(
            api_key=os.getenv('TRADINGVIEW_API_KEY')
        )
        
        self.slack = SlackConfig(
            webhook_url=os.getenv('SLACK_WEBHOOK_URL'),
            bot_token=os.getenv('SLACK_BOT_TOKEN')
        )
        
        self.discord = DiscordConfig(
            bot_token=os.getenv('DISCORD_BOT_TOKEN'),
            webhook_url=os.getenv('DISCORD_WEBHOOK_URL')
        )
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all configured services"""
        return {
            'openai': self.openai.is_configured(),
            'github': self.github.is_configured(),
            'office365': self.office365.is_configured(),
            'azure_login': self.azure_login.is_configured(),
            'pinecone': self.pinecone.is_configured(),
            'binance': self.binance.is_configured(),
            'coinbase': self.coinbase.is_configured(),
            'tradingview': self.tradingview.is_configured(),
            'slack': self.slack.is_configured(),
            'discord': self.discord.is_configured(),
        }
    
    def validate(self, required_services: list = None) -> bool:
        """Validate that required services are configured"""
        if required_services is None:
            required_services = []
        
        status = self.get_status()
        
        if not required_services:
            return all(status.values())
        
        # Allow either Binance OR Coinbase for trading
        if 'trading' in required_services:
            trading_available = status.get('binance', False) or status.get('coinbase', False)
            required_services.remove('trading')
            required_services.append('trading_impl')
            status['trading_impl'] = trading_available
        
        return all(status.get(service, False) for service in required_services)


class ConfigManager:
    """Singleton Configuration Manager"""
    _instance: Optional[ApplicationConfig] = None
    
    @classmethod
    def get_config(cls) -> ApplicationConfig:
        """Get or create singleton configuration instance"""
        if cls._instance is None:
            cls._instance = ApplicationConfig()
        return cls._instance
    
    @classmethod
    def reload(cls) -> ApplicationConfig:
        """Reload configuration from environment"""
        cls._instance = ApplicationConfig()
        return cls._instance


def get_config() -> ApplicationConfig:
    """Convenience function to get configuration singleton"""
    return ConfigManager.get_config()


if __name__ == '__main__':
    # Example usage
    config = get_config()
    print("Service Configuration Status:")
    print(json.dumps(config.get_status(), indent=2))
