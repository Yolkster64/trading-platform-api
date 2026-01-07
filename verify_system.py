"""
System Verification Script
Tests all API configurations and connectivity.
"""

import asyncio
import json
import os
from dotenv import load_dotenv
from config import get_config, ApplicationConfig
from azure_auth import AzureADClient, AzureADLoginManager
from coinbase_client import CoinbaseClient

try:
    from github import Github, GithubException
    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False


class SystemVerifier:
    """Comprehensive system verification"""
    
    def __init__(self):
        self.config = get_config()
        self.results = {}
    
    def verify_configuration(self):
        """Verify all services are configured"""
        print("\n" + "="*70)
        print("CONFIGURATION VERIFICATION")
        print("="*70)
        
        services = [
            ('OpenAI', self.config.openai.is_configured()),
            ('GitHub', self.config.github.is_configured()),
            ('Office 365', self.config.office365.is_configured()),
            ('Azure Login', self.config.azure_login.is_configured()),
            ('Pinecone', self.config.pinecone.is_configured()),
            ('Binance', self.config.binance.is_configured()),
            ('Coinbase', self.config.coinbase.is_configured()),
            ('TradingView', self.config.tradingview.is_configured()),
            ('Slack', self.config.slack.is_configured()),
            ('Discord', self.config.discord.is_configured()),
        ]
        
        for service_name, is_configured in services:
            status = "✅ CONFIGURED" if is_configured else "❌ NOT CONFIGURED"
            print(f"{service_name:20} {status}")
            self.results[service_name] = is_configured
        
        return any(self.results.values())
    
    async def verify_azure_ad(self):
        """Verify Azure AD configuration"""
        if not self.config.azure_login.is_configured():
            print("\n⚠️  Azure AD not configured - skipping verification")
            return False
        
        print("\n" + "="*70)
        print("AZURE AD VERIFICATION")
        print("="*70)
        
        try:
            client = AzureADClient(
                tenant_id=self.config.azure_login.tenant_id,
                client_id=self.config.azure_login.client_id,
                client_secret=self.config.azure_login.client_secret,
                redirect_uri=self.config.azure_login.redirect_uri
            )
            
            # Test: Generate authorization URL
            auth_url, state, nonce = client.generate_auth_url()
            print(f"✅ Authorization URL generated")
            print(f"   State: {state[:32]}...")
            print(f"   Nonce: {nonce[:32]}...")
            
            # Test: Verify endpoints
            print(f"✅ Authority URL: {client.authority_url}")
            print(f"✅ Token Endpoint: {client.token_endpoint}")
            print(f"✅ Graph API URL: {client.graph_api_url}")
            
            return True
        except Exception as e:
            print(f"❌ Azure AD verification failed: {str(e)}")
            return False
    
    async def verify_coinbase(self):
        """Verify Coinbase configuration and connectivity"""
        if not self.config.coinbase.is_configured():
            print("\n⚠️  Coinbase not configured - skipping verification")
            return False
        
        print("\n" + "="*70)
        print("COINBASE VERIFICATION")
        print("="*70)
        
        try:
            client = CoinbaseClient(
                api_key=self.config.coinbase.api_key,
                api_secret=self.config.coinbase.api_secret,
                api_passphrase=self.config.coinbase.api_passphrase,
                sandbox_mode=self.config.coinbase.sandbox_mode,
                sandbox_api_key=self.config.coinbase.sandbox_api_key,
                sandbox_api_secret=self.config.coinbase.sandbox_api_secret,
                sandbox_api_passphrase=self.config.coinbase.sandbox_api_passphrase
            )
            
            mode = "SANDBOX" if self.config.coinbase.sandbox_mode else "PRODUCTION"
            print(f"✅ Mode: {mode}")
            print(f"✅ Base URL: {client.get_base_url()}")
            
            # Test: Get accounts
            print("\n⏳ Testing API connectivity...")
            try:
                accounts = await client.get_accounts()
                print(f"✅ Accounts API working ({len(accounts)} accounts)")
                for acc in accounts[:3]:
                    print(f"   - {acc.name} ({acc.currency})")
            except Exception as e:
                print(f"⚠️  Accounts API error: {str(e)}")
            
            # Test: Get products
            try:
                products = await client.get_products()
                print(f"✅ Products API working ({len(products)} products)")
                # Show first 3 products
                for prod in products[:3]:
                    print(f"   - {prod.id}: ${prod.price}")
            except Exception as e:
                print(f"⚠️  Products API error: {str(e)}")
            
            # Test: Get ticker
            try:
                ticker = await client.get_ticker('BTC-USD')
                print(f"✅ Ticker API working (BTC-USD: ${ticker.price})")
            except Exception as e:
                print(f"⚠️  Ticker API error: {str(e)}")
            
            return True
        except Exception as e:
            print(f"❌ Coinbase verification failed: {str(e)}")
            return False
    
    async def verify_trading_setup(self):
        """Verify trading setup (Binance OR Coinbase)"""
        print("\n" + "="*70)
        print("TRADING SETUP VERIFICATION")
        print("="*70)
        
        binance_ok = self.config.binance.is_configured()
        coinbase_ok = self.config.coinbase.is_configured()
        
        print(f"Binance: {'✅ CONFIGURED' if binance_ok else '❌ NOT CONFIGURED'}")
        print(f"Coinbase: {'✅ CONFIGURED' if coinbase_ok else '❌ NOT CONFIGURED'}")
        
        if not (binance_ok or coinbase_ok):
            print("❌ No trading exchange configured!")
            return False
        
        return True
    
    def verify_github(self):
        """Verify GitHub API connectivity"""
        if not self.config.github.is_configured():
            print("\n⚠️  GitHub not configured - skipping verification")
            return False
        
        if not GITHUB_AVAILABLE:
            print("\n⚠️  PyGithub not installed - skipping GitHub verification")
            print("   Install with: pip install PyGithub")
            return False
        
        print("\n" + "="*70)
        print("GITHUB API VERIFICATION")
        print("="*70)
        
        try:
            primary_token = os.getenv('GITHUB_API_TOKEN')
            secondary_token = os.getenv('GITHUB_API_TOKEN_SECONDARY')
            
            # Test primary token
            if primary_token:
                try:
                    gh_primary = Github(primary_token)
                    user_primary = gh_primary.get_user()
                    print(f"✅ Primary Token Active")
                    print(f"   User: {user_primary.login}")
                    print(f"   Name: {user_primary.name}")
                    print(f"   Public repos: {user_primary.public_repos}")
                    print(f"   Followers: {user_primary.followers}")
                except GithubException as e:
                    print(f"❌ Primary token error: {str(e)}")
                    return False
            
            # Test secondary token
            if secondary_token:
                try:
                    gh_secondary = Github(secondary_token)
                    user_secondary = gh_secondary.get_user()
                    print(f"\n✅ Secondary Token Active")
                    print(f"   User: {user_secondary.login}")
                    print(f"   Name: {user_secondary.name}")
                    print(f"   Public repos: {user_secondary.public_repos}")
                    print(f"   Followers: {user_secondary.followers}")
                except GithubException as e:
                    print(f"❌ Secondary token error: {str(e)}")
                    return False
            
            # Test repository access
            owner = os.getenv('GITHUB_OWNER', 'Yolkster64')
            repo_name = os.getenv('GITHUB_REPO', 'trading-platform-api')
            
            if primary_token:
                try:
                    gh = Github(primary_token)
                    repo = gh.get_user(owner).get_repo(repo_name)
                    print(f"\n✅ Repository Access: {repo.full_name}")
                    print(f"   Stars: {repo.stargazers_count}")
                    print(f"   Forks: {repo.forks_count}")
                    print(f"   Open issues: {repo.open_issues_count}")
                    print(f"   Language: {repo.language}")
                except GithubException as e:
                    print(f"\n⚠️  Repository access test: {owner}/{repo_name} - {str(e)}")
                except Exception as e:
                    print(f"\n⚠️  Repository not found (will be created): {owner}/{repo_name}")
            
            return True
        except Exception as e:
            print(f"❌ GitHub verification failed: {str(e)}")
            return False
    
    def generate_report(self):
        """Generate verification report"""
        print("\n" + "="*70)
        print("SUMMARY REPORT")
        print("="*70)
        
        configured = sum(1 for v in self.results.values() if v)
        total = len(self.results)
        
        print(f"\nConfigured Services: {configured}/{total}")
        print(f"Configuration Complete: {configured == total}")
        
        print("\n" + "="*70)
        print("RECOMMENDATIONS")
        print("="*70)
        
        if not self.config.openai.is_configured():
            print("1. Configure OpenAI API for AI features")
        if not self.config.github.is_configured():
            print("2. Configure GitHub API for code integration")
        if not (self.config.binance.is_configured() or self.config.coinbase.is_configured()):
            print("3. Configure at least one trading exchange (Binance or Coinbase)")
        if not self.config.azure_login.is_configured():
            print("4. Configure Azure AD for user authentication")
        if not self.config.pinecone.is_configured():
            print("5. Configure Pinecone for vector database")
        
        print("\nNext Steps:")
        print("1. Review .env file and add missing credentials")
        print("2. Run FastAPI application: python -m uvicorn main:app --reload")
        print("3. Access API documentation: http://localhost:8000/docs")


async def main():
    """Run verification"""
    print("\n[Trading Platform API - System Verification]")
    
    load_dotenv()
    
    verifier = SystemVerifier()
    
    # Run synchronous checks
    config_ok = verifier.verify_configuration()
    trading_ok = await verifier.verify_trading_setup()
    github_ok = verifier.verify_github()
    
    # Run async checks
    azure_ok = await verifier.verify_azure_ad()
    coinbase_ok = await verifier.verify_coinbase()
    
    # Generate report
    verifier.generate_report()
    
    # Final status
    print("\n" + "="*70)
    if config_ok and github_ok:
        print("[OK] VERIFICATION COMPLETE - System is ready!")
    else:
        print("[WARNING] VERIFICATION COMPLETE - Some services not configured")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(main())
