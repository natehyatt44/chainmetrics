import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from loguru import logger

from ..database.connection import db_manager
from ..database.models import HBARMetrics
from .base_fetcher import RateLimitedFetcher


class CoinGeckoFetcher(RateLimitedFetcher):
    """Fetches HBAR data from CoinGecko API."""
    
    def __init__(self, api_key: Optional[str] = None):
        api_key = api_key or os.getenv("COINGECKO_API_KEY")
        base_url = "https://api.coingecko.com/api/v3"
        
        # CoinGecko free tier: 30 requests/minute
        super().__init__(base_url, api_key, requests_per_minute=25)
        
        self.hbar_id = "hedera-hashgraph"
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get CoinGecko authentication headers."""
        if self.api_key:
            return {"x-cg-demo-api-key": self.api_key}
        return {}
    
    async def fetch_hbar_data(self) -> Optional[HBARMetrics]:
        """Fetch current HBAR market data."""
        try:
            data = await self._make_request(
                "coins/hedera-hashgraph",
                params={
                    "localization": "false",
                    "tickers": "false",
                    "market_data": "true",
                    "community_data": "false",
                    "developer_data": "false",
                    "sparkline": "false"
                }
            )
            
            market_data = data.get("market_data", {})
            
            return HBARMetrics(
                timestamp=self._get_current_timestamp(),
                price_usd=self._safe_float(market_data.get("current_price", {}).get("usd")),
                market_cap=self._safe_float(market_data.get("market_cap", {}).get("usd")),
                volume_24h=self._safe_float(market_data.get("total_volume", {}).get("usd")),
                price_change_24h=self._safe_float(market_data.get("price_change_percentage_24h")),
                circulating_supply=self._safe_float(market_data.get("circulating_supply")),
                market_cap_rank=self._safe_int(market_data.get("market_cap_rank")),
            )
            
        except Exception as e:
            logger.error(f"Failed to fetch HBAR data from CoinGecko: {e}")
            return None
    
    async def fetch_global_crypto_data(self) -> Optional[Dict[str, Any]]:
        """Fetch global cryptocurrency market data."""
        try:
            data = await self._make_request("global")
            return data.get("data", {})
        except Exception as e:
            logger.error(f"Failed to fetch global crypto data: {e}")
            return None
    
    async def fetch_trending_coins(self) -> Optional[List[Dict[str, Any]]]:
        """Fetch trending cryptocurrencies."""
        try:
            data = await self._make_request("search/trending")
            return data.get("coins", [])
        except Exception as e:
            logger.error(f"Failed to fetch trending coins: {e}")
            return None
    
    async def fetch_data(self) -> Dict[str, Any]:
        """Fetch comprehensive HBAR and market data."""
        hbar_data = await self.fetch_hbar_data()
        global_data = await self.fetch_global_crypto_data()
        trending_data = await self.fetch_trending_coins()
        
        return {
            "hbar": hbar_data,
            "global": global_data,
            "trending": trending_data,
            "timestamp": self._get_current_timestamp(),
        }
    
    async def save_hbar_data(self, hbar_data: HBARMetrics) -> bool:
        """Save HBAR data to database."""
        try:
            query = """
                INSERT OR REPLACE INTO hbar_metrics 
                (timestamp, price_usd, market_cap, volume_24h, price_change_24h, 
                 circulating_supply, market_cap_rank)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            
            db_manager.execute(query, (
                hbar_data.timestamp,
                hbar_data.price_usd,
                hbar_data.market_cap,
                hbar_data.volume_24h,
                hbar_data.price_change_24h,
                hbar_data.circulating_supply,
                hbar_data.market_cap_rank,
            ))
            
            logger.info("HBAR data saved to database")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save HBAR data: {e}")
            return False
    
    async def get_latest_hbar_data(self) -> Optional[Dict[str, Any]]:
        """Get the latest HBAR data from database."""
        try:
            query = """
                SELECT timestamp, price_usd, market_cap, volume_24h, price_change_24h,
                       circulating_supply, market_cap_rank
                FROM hbar_metrics
                ORDER BY timestamp DESC
                LIMIT 1
            """
            
            result = db_manager.fetchone(query)
            if result:
                return {
                    "timestamp": result[0],
                    "price_usd": result[1],
                    "market_cap": result[2],
                    "volume_24h": result[3],
                    "price_change_24h": result[4],
                    "circulating_supply": result[5],
                    "market_cap_rank": result[6],
                }
            return None
            
        except Exception as e:
            logger.error(f"Failed to get latest HBAR data: {e}")
            return None
    
    async def get_hbar_price_history(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get HBAR price history from database."""
        try:
            query = """
                SELECT timestamp, price_usd, volume_24h
                FROM hbar_metrics
                WHERE timestamp >= (current_timestamp - interval '{} days')
                ORDER BY timestamp ASC
            """.format(days)
            
            results = db_manager.fetchall(query)
            return [
                {
                    "timestamp": row[0],
                    "price_usd": row[1],
                    "volume_24h": row[2],
                }
                for row in results
            ]
            
        except Exception as e:
            logger.error(f"Failed to get HBAR price history: {e}")
            return []