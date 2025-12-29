"""Configuration file for DeFi Portfolio Tracker"""

# ERC-20 Token Contracts (Ethereum Mainnet)
TOKEN_CONTRACTS = {
    'USDC': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
    'DAI': '0x6B175474E89094C44Da98b954EedeAC495271d0F',
    'USDT': '0xdAC17F958D2ee523a2206206994597C13D831ec7',
}

# ERC-20 ABI (Minimal - only balanceOf function)
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function"
    }
]

# CoinGecko API endpoint
COINGECKO_API = "https://api.coingecko.com/api/v3"

# Token ID mapping for CoinGecko
COINGECKO_IDS = {
    'USDC': 'usd-coin',
    'DAI': 'dai',
    'USDT': 'tether',
    'ETH': 'ethereum'
}