"""
Market symbols and universe definitions for multi-market scanning.
Supports 50+ markets across Crypto, US Equities, and Forex.
"""

# Top 65 Liquid Cryptocurrency Markets (USDT quoted pairs on Binance, Bybit, OKX, etc.)
CRYPTO_50_PLUS = [
    "BTC/USDT",   # Bitcoin
    "ETH/USDT",   # Ethereum
    "SOL/USDT",   # Solana
    "BNB/USDT",   # Binance Coin
    "XRP/USDT",   # Ripple
    "DOGE/USDT",  # Dogecoin
    "ADA/USDT",   # Cardano
    "AVAX/USDT",  # Avalanche
    "LINK/USDT",  # Chainlink
    "SUI/USDT",   # Sui Network
    "NEAR/USDT",  # Near Protocol
    "APT/USDT",   # Aptos
    "INJ/USDT",   # Injective
    "DOT/USDT",   # Polkadot
    "PEPE/USDT",  # Pepe
    "SHIB/USDT",  # Shiba Inu
    "ARB/USDT",   # Arbitrum
    "OP/USDT",    # Optimism
    "TIA/USDT",   # Celestia
    "RENDER/USDT",# Render
    "FET/USDT",   # Fetch.ai
    "FIL/USDT",   # Filecoin
    "KAS/USDT",   # Kaspa
    "ATOM/USDT",  # Cosmos
    "LTC/USDT",   # Litecoin
    "BCH/USDT",   # Bitcoin Cash
    "UNI/USDT",   # Uniswap
    "ICP/USDT",   # Internet Computer
    "STX/USDT",   # Stacks
    "SEI/USDT",   # Sei
    "BONK/USDT",  # Bonk
    "WIF/USDT",   # Dogwifhat
    "FLOKI/USDT", # Floki
    "JUP/USDT",   # Jupiter
    "PYTH/USDT",  # Pyth Network
    "AAVE/USDT",  # Aave
    "MKR/USDT",   # Maker
    "RUNE/USDT",  # THORChain
    "GRT/USDT",   # The Graph
    "IMX/USDT",   # ImmutableX
    "THETA/USDT", # Theta
    "FTM/USDT",   # Fantom / Sonic
    "ALGO/USDT",  # Algorand
    "SAND/USDT",  # The Sandbox
    "MANA/USDT",  # Decentraland
    "AXS/USDT",   # Axie Infinity
    "GALA/USDT",  # Gala Games
    "CHZ/USDT",   # Chiliz
    "EOS/USDT",   # EOS
    "CRV/USDT",   # Curve DAO
    "LDO/USDT",   # Lido DAO
    "DYDX/USDT",  # dYdX
    "PENDLE/USDT",# Pendle
    "ENA/USDT",   # Ethena
    "ONDO/USDT",  # Ondo Finance
    "WLD/USDT",   # Worldcoin
    "NOT/USDT",   # Notcoin
    "BLUR/USDT",  # Blur
    "STRK/USDT",  # Starknet
    "TON/USDT",   # Toncoin
    "MATIC/USDT", # Polygon
    "ENS/USDT",   # Ethereum Name Service
    "NEO/USDT",   # Neo
    "QNT/USDT",   # Quant
    "FLOW/USDT",  # Flow
]

# Top 50 Liquid US Equities & Tech Leaders (S&P 500 / Nasdaq 100)
EQUITIES_50 = [
    "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "BRK.B", "LLY", "AVGO",
    "JPM", "V", "UNH", "XOM", "MA", "JNJ", "PG", "HD", "COST", "ABBV",
    "MRK", "NFLX", "CRM", "AMD", "BAC", "CVX", "PEP", "KO", "WMT", "TMO",
    "LIN", "QCOM", "ADBE", "MCD", "CSCO", "ACN", "ABT", "DIS", "WFC", "GE",
    "INTU", "CAT", "AMAT", "TXN", "VZ", "PM", "IBM", "MS", "NOW", "ISRG"
]

# Forex Major & Minor Pairs
FOREX_20 = [
    "EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD", "USD/CAD", "NZD/USD",
    "EUR/GBP", "EUR/JPY", "GBP/JPY", "EUR/AUD", "EUR/CAD", "GBP/AUD", "AUD/JPY",
    "CAD/JPY", "NZD/JPY", "GBP/CAD", "AUD/NZD", "USD/SGD", "USD/MXN"
]

def get_market_universe(name: str = "crypto", limit: int = 50):
    """Retrieve market universe list trimmed to requested limit."""
    name_lower = name.lower()
    if "crypto" in name_lower:
        universe = CRYPTO_50_PLUS
    elif "equit" in name_lower or "stock" in name_lower:
        universe = EQUITIES_50
    elif "forex" in name_lower or "fx" in name_lower:
        universe = FOREX_20
    else:
        universe = CRYPTO_50_PLUS

    return universe[:limit] if limit and limit > 0 else universe
