import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional

import httpx
from loguru import logger
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential


class BaseFetcher(ABC):
    """Base class for all data fetchers with retry logic and error handling."""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._session: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        await self._create_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._close_session()
    
    async def _create_session(self) -> None:
        """Create HTTP session with proper headers."""
        headers = {
            "User-Agent": "ChainMetrics/1.0 (Hedera Dashboard)",
            "Accept": "application/json",
        }
        
        if self.api_key:
            headers.update(self._get_auth_headers())
        
        self._session = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout),
            headers=headers,
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
        )
    
    async def _close_session(self) -> None:
        """Close HTTP session."""
        if self._session:
            await self._session.aclose()
            self._session = None
    
    @abstractmethod
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests."""
        pass
    
    @retry(
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True,
    )
    async def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make HTTP request with retry logic."""
        if not self._session:
            await self._create_session()
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            logger.debug(f"Making request to: {url}")
            response = await self._session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.debug(f"Request successful: {url}")
            return data
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} for {url}: {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error for {url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error for {url}: {e}")
            raise
    
    @abstractmethod
    async def fetch_data(self) -> Dict[str, Any]:
        """Fetch data from the API. Must be implemented by subclasses."""
        pass
    
    async def fetch_with_fallback(self, fallback_value: Any = None) -> Any:
        """Fetch data with graceful fallback on error."""
        try:
            return await self.fetch_data()
        except Exception as e:
            logger.warning(f"Data fetch failed for {self.__class__.__name__}: {e}")
            return fallback_value
    
    def _get_current_timestamp(self) -> datetime:
        """Get current UTC timestamp."""
        return datetime.utcnow()
    
    def _safe_get(self, data: Dict[str, Any], key: str, default: Any = None) -> Any:
        """Safely get value from dictionary with optional nested key support."""
        if "." in key:
            keys = key.split(".")
            current = data
            for k in keys:
                if isinstance(current, dict) and k in current:
                    current = current[k]
                else:
                    return default
            return current
        return data.get(key, default)
    
    def _safe_float(self, value: Any, default: float = 0.0) -> float:
        """Safely convert value to float."""
        if value is None:
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def _safe_int(self, value: Any, default: int = 0) -> int:
        """Safely convert value to int."""
        if value is None:
            return default
        try:
            return int(value)
        except (ValueError, TypeError):
            return default


class RateLimitedFetcher(BaseFetcher):
    """Base fetcher with rate limiting support."""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None, 
                 timeout: int = 30, requests_per_minute: int = 60):
        super().__init__(base_url, api_key, timeout)
        self.requests_per_minute = requests_per_minute
        self._request_times: list[float] = []
    
    async def _wait_for_rate_limit(self) -> None:
        """Wait if necessary to respect rate limits."""
        now = asyncio.get_event_loop().time()
        
        # Remove requests older than 1 minute
        self._request_times = [t for t in self._request_times if now - t < 60]
        
        # If we're at the limit, wait
        if len(self._request_times) >= self.requests_per_minute:
            wait_time = 60 - (now - self._request_times[0])
            if wait_time > 0:
                logger.info(f"Rate limit reached, waiting {wait_time:.1f} seconds")
                await asyncio.sleep(wait_time)
        
        self._request_times.append(now)
    
    async def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make rate-limited HTTP request."""
        await self._wait_for_rate_limit()
        return await super()._make_request(endpoint, params)