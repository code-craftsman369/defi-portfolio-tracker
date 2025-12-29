"""
DeFi Portfolio Tracker
Aggregates cryptocurrency balances across multiple wallets
"""

import os
from web3 import Web3
import requests
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from dotenv import load_dotenv
from config import TOKEN_CONTRACTS, ERC20_ABI, COINGECKO_API, COINGECKO_IDS

# Load environment variables
load_dotenv()

class DeFiPortfolioTracker:
    def __init__(self, provider_url):
        """Initialize Web3 connection"""
        self.w3 = Web3(Web3.HTTPProvider(provider_url))
        if not self.w3.is_connected():
            raise Exception("Failed to connect to Ethereum node")
        print(f"✅ Connected to Ethereum Mainnet")
        
    def get_eth_balance(self, address):
        """Get ETH balance for an address"""
        balance_wei = self.w3.eth.get_balance(address)
        balance_eth = self.w3.from_wei(balance_wei, 'ether')
        return float(balance_eth)
    
    def get_token_balance(self, token_address, wallet_address):
        """Get ERC-20 token balance"""
        contract = self.w3.eth.contract(address=token_address, abi=ERC20_ABI)
        balance = contract.functions.balanceOf(wallet_address).call()
        decimals = contract.functions.decimals().call()
        return balance / (10 ** decimals)
    
    def get_prices(self):
        """Fetch current prices from CoinGecko"""
        ids = ','.join(COINGECKO_IDS.values())
        url = f"{COINGECKO_API}/simple/price"
        params = {
            'ids': ids,
            'vs_currencies': 'usd'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            prices = {}
            for token, gecko_id in COINGECKO_IDS.items():
                prices[token] = data.get(gecko_id, {}).get('usd', 0)
            
            return prices
        except Exception as e:
            print(f"⚠️  Error fetching prices: {e}")
            return {token: 0 for token in COINGECKO_IDS.keys()}
    
    def track_portfolio(self, wallet_addresses):
        """Track portfolio across multiple wallets"""
        print(f"\n📊 Tracking {len(wallet_addresses)} wallet(s)...\n")
        
        # Get current prices
        prices = self.get_prices()
        print("💰 Current Prices (USD):")
        for token, price in prices.items():
            print(f"   {token}: ${price:,.2f}")
        print()
        
        # Aggregate balances
        total_balances = {
            'ETH': 0,
            'USDC': 0,
            'DAI': 0,
            'USDT': 0
        }
        
        for i, address in enumerate(wallet_addresses, 1):
            print(f"Wallet {i}: {address}")
            
            # ETH balance
            eth_balance = self.get_eth_balance(address)
            total_balances['ETH'] += eth_balance
            print(f"  ETH: {eth_balance:.4f}")
            
            # Token balances
            for token, contract_address in TOKEN_CONTRACTS.items():
                balance = self.get_token_balance(contract_address, address)
                total_balances[token] += balance
                print(f"  {token}: {balance:.2f}")
            print()
        
        # Calculate USD values
        portfolio_data = []
        total_usd = 0
        
        for token, balance in total_balances.items():
            usd_value = balance * prices.get(token, 0)
            total_usd += usd_value
            portfolio_data.append({
                'Token': token,
                'Balance': balance,
                'Price (USD)': prices.get(token, 0),
                'Value (USD)': usd_value
            })
        
        df = pd.DataFrame(portfolio_data)
        
        print("\n" + "="*60)
        print("📈 PORTFOLIO SUMMARY")
        print("="*60)
        print(df.to_string(index=False))
        print("="*60)
        print(f"💵 TOTAL PORTFOLIO VALUE: ${total_usd:,.2f} USD")
        print("="*60 + "\n")
        
        return df, total_usd
    
    def visualize_portfolio(self, df, total_usd):
        """Create visualization of portfolio distribution"""
        # Filter out zero balances
        df_filtered = df[df['Value (USD)'] > 0].copy()
        
        if df_filtered.empty:
            print("⚠️  No assets to visualize")
            return
        
        # Calculate percentages
        df_filtered['Percentage'] = (df_filtered['Value (USD)'] / total_usd * 100)
        
        # Create output directory
        os.makedirs('../output', exist_ok=True)
        
        # 1. Matplotlib Pie Chart
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = plt.cm.Set3(range(len(df_filtered)))
        
        wedges, texts, autotexts = ax.pie(
            df_filtered['Value (USD)'],
            labels=df_filtered['Token'],
            autopct='%1.1f%%',
            startangle=90,
            colors=colors
        )
        
        ax.set_title(f'DeFi Portfolio Distribution\nTotal: ${total_usd:,.2f} USD', 
                     fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('../output/portfolio_pie_chart.png', dpi=300, bbox_inches='tight')
        print("✅ Saved: output/portfolio_pie_chart.png")
        
        # 2. Plotly Interactive Bar Chart
        fig = go.Figure(data=[
            go.Bar(
                x=df_filtered['Token'],
                y=df_filtered['Value (USD)'],
                text=df_filtered['Value (USD)'].apply(lambda x: f'${x:,.2f}'),
                textposition='auto',
                marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'][:len(df_filtered)]
            )
        ])
        
        fig.update_layout(
            title=f'DeFi Portfolio Value by Asset (Total: ${total_usd:,.2f} USD)',
            xaxis_title='Token',
            yaxis_title='Value (USD)',
            template='plotly_white',
            height=500
        )
        
        fig.write_html('../output/portfolio_interactive.html')
        print("✅ Saved: output/portfolio_interactive.html")
        
        # 3. Save data to CSV
        df.to_csv('../output/portfolio_data.csv', index=False)
        print("✅ Saved: output/portfolio_data.csv\n")


def main():
    """Main execution function"""
    
    # Get Infura/Alchemy URL from environment
    provider_url = os.getenv('INFURA_URL') or os.getenv('ALCHEMY_URL')
    
    if not provider_url:
        print("⚠️  No provider URL found in .env file")
        print("Using public Ethereum node (may be slower)...")
        provider_url = "https://eth.llamarpc.com"  # Public fallback
    
    # Example wallet addresses (Vitalik's address + random examples)
    wallet_addresses = [
        '0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045',  # Vitalik Buterin
        # Add more addresses here if needed
    ]
    
    try:
        tracker = DeFiPortfolioTracker(provider_url)
        df, total_usd = tracker.track_portfolio(wallet_addresses)
        tracker.visualize_portfolio(df, total_usd)
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()