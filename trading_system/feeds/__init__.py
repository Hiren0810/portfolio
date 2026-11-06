"""Feeds package initialization."""
from .base_feed import BaseFeed
from .mock_feed import MockFeed
from .crypto_feed import CryptoFeed
from .equities_feed import EquitiesFeed

def get_feed(feed_type: str = "crypto", fallback_mock: bool = True) -> BaseFeed:
    """Factory helper to obtain market feed instance."""
    ft = feed_type.lower()
    if "crypto" in ft:
        return CryptoFeed(fallback_mock=fallback_mock)
    elif "equit" in ft or "stock" in ft:
        return EquitiesFeed(fallback_mock=fallback_mock)
    else:
        return MockFeed()

__all__ = [
    "BaseFeed",
    "MockFeed",
    "CryptoFeed",
    "EquitiesFeed",
    "get_feed"
]
