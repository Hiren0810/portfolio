"""Configuration package initialization."""
from .settings import SystemSettings, RiskSettings, ScannerSettings, DEFAULT_SETTINGS
from .markets import CRYPTO_50_PLUS, EQUITIES_50, FOREX_20, get_market_universe

__all__ = [
    "SystemSettings",
    "RiskSettings",
    "ScannerSettings",
    "DEFAULT_SETTINGS",
    "CRYPTO_50_PLUS",
    "EQUITIES_50",
    "FOREX_20",
    "get_market_universe",
]
