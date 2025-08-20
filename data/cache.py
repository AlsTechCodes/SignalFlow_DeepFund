import time
from typing import Optional, Dict, Any, List
from collections import OrderedDict

class Cache:
    """A memory cache with size limits and automatic cleanup."""
    
    def __init__(self, max_items: int = 1000, max_age_seconds: int = 3600):
        self._prices: Dict[str, List[Dict[str, Any]]] = OrderedDict()
        self._financial_metrics: Dict[str, List[Dict[str, Any]]] = OrderedDict()
        self._insider_trades: Dict[str, List[Dict[str, Any]]] = OrderedDict()
        self._company_news: Dict[str, List[Dict[str, Any]]] = OrderedDict()
        self._timestamps: Dict[str, float] = {}
        self.max_items = max_items
        self.max_age_seconds = max_age_seconds

    def _cleanup_expired(self, cache_dict: OrderedDict) -> None:
        """Remove expired items from cache."""
        current_time = time.time()
        expired_keys = [
            key for key, _ in cache_dict.items()
            if current_time - self._timestamps.get(key, 0) > self.max_age_seconds
        ]
        for key in expired_keys:
            del cache_dict[key]
            self._timestamps.pop(key, None)

    def _enforce_size_limit(self, cache_dict: OrderedDict) -> None:
        """Remove oldest items if cache exceeds size limit."""
        while len(cache_dict) > self.max_items:
            oldest_key, _ = next(iter(cache_dict.items()))
            del cache_dict[oldest_key]
            self._timestamps.pop(oldest_key, None)

    def _update_cache(self, cache_dict: OrderedDict, key: str, value: Any) -> None:
        """Update cache with new value and manage size/expiry."""
        self._cleanup_expired(cache_dict)
        cache_dict[key] = value
        self._timestamps[key] = time.time()
        self._enforce_size_limit(cache_dict)
        # Move to end to mark as recently used
        cache_dict.move_to_end(key)

    def _get_from_cache(self, cache_dict: OrderedDict, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        if key not in cache_dict:
            return None
            
        current_time = time.time()
        if current_time - self._timestamps.get(key, 0) > self.max_age_seconds:
            del cache_dict[key]
            self._timestamps.pop(key, None)
            return None
            
        # Move to end to mark as recently used
        cache_dict.move_to_end(key)
        return cache_dict[key]

    def get_prices(self, ticker: str) -> Optional[List[Dict[str, Any]]]:
        """Get price data from cache."""
        return self._get_from_cache(self._prices, ticker)

    def set_prices(self, ticker: str, prices: List[Dict[str, Any]]) -> None:
        """Set price data in cache."""
        self._update_cache(self._prices, ticker, prices)

    def get_financial_metrics(self, ticker: str) -> Optional[List[Dict[str, Any]]]:
        """Get financial metrics from cache."""
        return self._get_from_cache(self._financial_metrics, ticker)

    def set_financial_metrics(self, ticker: str, metrics: List[Dict[str, Any]]) -> None:
        """Set financial metrics in cache."""
        self._update_cache(self._financial_metrics, ticker, metrics)

    def get_insider_trades(self, ticker: str) -> Optional[List[Dict[str, Any]]]:
        """Get insider trades from cache."""
        return self._get_from_cache(self._insider_trades, ticker)

    def set_insider_trades(self, ticker: str, trades: List[Dict[str, Any]]) -> None:
        """Set insider trades in cache."""
        self._update_cache(self._insider_trades, ticker, trades)

    def get_company_news(self, ticker: str) -> Optional[List[Dict[str, Any]]]:
        """Get company news from cache."""
        return self._get_from_cache(self._company_news, ticker)

    def set_company_news(self, ticker: str, news: List[Dict[str, Any]]) -> None:
        """Set company news in cache."""
        self._update_cache(self._company_news, ticker, news)

    def clear(self) -> None:
        """Clear all cache data."""
        self._prices.clear()
        self._financial_metrics.clear()
        self._insider_trades.clear()
        self._company_news.clear()
        self._timestamps.clear()

# Global cache instance with 1000 items limit and 1-hour expiry
_cache = Cache(max_items=1000, max_age_seconds=3600)

def get_cache() -> Cache:
    """Get the global cache instance."""
    return _cache
