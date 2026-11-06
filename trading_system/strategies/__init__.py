"""Strategies package initialization."""
from .base_strategy import BaseStrategy
from .confluence import ConfluenceStrategy
from .breakout import BreakoutStrategy
from .mean_reversion import MeanReversionStrategy

def get_strategy(name: str = "confluence", **kwargs) -> BaseStrategy:
    """Factory helper to instantiate a strategy by name."""
    name_lower = name.lower()
    if "breakout" in name_lower:
        return BreakoutStrategy(**kwargs)
    elif "mean" in name_lower or "reversion" in name_lower:
        return MeanReversionStrategy(**kwargs)
    else:
        return ConfluenceStrategy(**kwargs)

__all__ = [
    "BaseStrategy",
    "ConfluenceStrategy",
    "BreakoutStrategy",
    "MeanReversionStrategy",
    "get_strategy"
]
