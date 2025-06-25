import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

from loguru import logger

from ..config import settings
from ..database.connection import db_manager
from .base_fetcher import BaseFetcher


class HederaTokenFetcher(BaseFetcher):
    """Fetcher for Hedera token data from mirror node API."""
    
    # Curated list of popular and active Hedera tokens
    POPULAR_TOKENS = [
        "0.0.456858",   # USDC - USD Coin (verified stablecoin)
        "0.0.1456986",  # WHBAR - Wrapped Hbar (liquid staking)  
        "0.0.731861",   # SAUCE - SaucerSwap DEX token
        "0.0.9295288",  # CLAW - Silver to $PAWS
        "0.0.9296430",  # paws - Paws Coin  
        "0.0.9284323",  # HDANO - Hedera Notes
        "0.0.9289584",  # APUP - AstroPup Coin
        "0.0.9295368",  # PAWS - Paws token
        "0.0.9290018",  # Rico - Rico token
        "0.0.9297325",  # Tuca - Tuca token
    ]
    
    def __init__(self):
        super().__init__(
            base_url=settings.hedera.mirror_node_url,
            api_key=None,  # Mirror node doesn't require API key
            timeout=30
        )
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Mirror node doesn't require authentication."""
        return {}
    
    async def fetch_data(self) -> List[Dict[str, Any]]:
        """Fetch data for popular Hedera tokens."""
        logger.info("Fetching Hedera token data...")
        
        tokens_data = []
        
        # Fetch data for each popular token
        for token_id in self.POPULAR_TOKENS:
            try:
                token_info = await self._fetch_token_info(token_id)
                if token_info:
                    # Get additional market data if available
                    token_stats = await self._fetch_token_stats(token_id)
                    
                    # Combine token info with stats
                    token_data = {
                        "token_id": token_id,
                        "name": token_info.get("name", "Unknown"),
                        "symbol": token_info.get("symbol", "UNK"),
                        "decimals": token_info.get("decimals", 0),
                        "total_supply": self._safe_int(token_info.get("total_supply", 0)),
                        "treasury_account": token_info.get("treasury_account_id"),
                        "created_timestamp": token_info.get("created_timestamp"),
                        "type": token_info.get("type", "FUNGIBLE_COMMON"),
                        "deleted": token_info.get("deleted", False),
                        "memo": token_info.get("memo", ""),
                        # Market data (placeholder for now, can be enhanced with DEX data)
                        "price_usd": None,
                        "market_cap": None,
                        "volume_24h": None,
                        "price_change_24h": None,
                        "holders_count": token_stats.get("holders_count") if token_stats else None,
                        "transfers_24h": token_stats.get("transfers_24h") if token_stats else None,
                    }
                    
                    tokens_data.append(token_data)
                    logger.debug(f"Fetched data for token {token_id}: {token_data['symbol']}")
                    
            except Exception as e:
                logger.warning(f"Failed to fetch data for token {token_id}: {e}")
                continue
        
        logger.info(f"Successfully fetched data for {len(tokens_data)} tokens")
        return tokens_data
    
    async def _fetch_token_info(self, token_id: str) -> Optional[Dict[str, Any]]:
        """Fetch basic token information."""
        try:
            endpoint = f"/api/v1/tokens/{token_id}"
            data = await self._make_request(endpoint)
            return data
        except Exception as e:
            logger.error(f"Failed to fetch token info for {token_id}: {e}")
            return None
    
    async def _fetch_token_stats(self, token_id: str) -> Optional[Dict[str, Any]]:
        """Fetch token statistics like holder count and recent activity."""
        try:
            # Get recent token transfers to estimate activity
            endpoint = f"/api/v1/tokens/{token_id}/balances"
            params = {"limit": 1000}  # Get top holders
            
            balances_data = await self._make_request(endpoint, params)
            
            if balances_data and "balances" in balances_data:
                balances = balances_data["balances"]
                holders_count = len([b for b in balances if self._safe_int(b.get("balance", 0)) > 0])
                
                return {
                    "holders_count": holders_count,
                    "transfers_24h": None,  # Would need transaction history analysis
                }
        except Exception as e:
            logger.warning(f"Failed to fetch token stats for {token_id}: {e}")
        
        return None
    
    async def save_token_data(self, tokens_data: List[Dict[str, Any]]) -> bool:
        """Save token data to database."""
        if not tokens_data:
            logger.warning("No token data to save")
            return False
        
        try:
            current_time = self._get_current_timestamp()
            
            # Prepare data for batch insertion
            values = []
            for token in tokens_data:
                # Skip deleted tokens
                if token.get("deleted", False):
                    continue
                
                values.append((
                    current_time,
                    token["token_id"],
                    token["name"],
                    token["symbol"],
                    token.get("price_usd"),
                    token.get("market_cap"),
                    token.get("volume_24h"),
                    token.get("price_change_24h"),
                    token.get("decimals", 0),
                    token.get("total_supply", 0),
                    token.get("holders_count"),
                    token.get("transfers_24h"),
                    token.get("type", "FUNGIBLE_COMMON"),
                    token.get("memo", ""),
                ))
            
            if not values:
                logger.warning("No valid tokens to save after filtering")
                return False
            
            # Insert data
            query = """
                INSERT INTO hedera_tokens 
                (timestamp, token_id, name, symbol, price_usd, market_cap, volume_24h, 
                 price_change_24h, decimals, total_supply, holders_count, transfers_24h, 
                 token_type, memo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            # Execute batch insert
            db_manager.execute_many(query, values)
            
            logger.info(f"Successfully saved {len(values)} token records to database")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save token data: {e}")
            return False
    
    async def get_top_tokens(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top tokens from database, ordered by holders count or other metrics."""
        try:
            query = """
                SELECT DISTINCT ON (token_id)
                    token_id, name, symbol, price_usd, market_cap, volume_24h,
                    price_change_24h, decimals, total_supply, holders_count,
                    transfers_24h, token_type, memo, timestamp
                FROM hedera_tokens 
                WHERE timestamp >= (SELECT MAX(timestamp) FROM hedera_tokens) - INTERVAL '1 hour'
                ORDER BY token_id, timestamp DESC
                LIMIT ?
            """
            
            results = db_manager.fetchall(query, (limit,))
            
            tokens = []
            if results:
                for row in results:
                    tokens.append({
                        "token_id": row[0],
                        "name": row[1],
                        "symbol": row[2],
                        "price_usd": row[3],
                        "market_cap": row[4],
                        "volume_24h": row[5],
                        "price_change_24h": row[6],
                        "decimals": row[7],
                        "total_supply": row[8],
                        "holders_count": row[9],
                        "transfers_24h": row[10],
                        "token_type": row[11],
                        "memo": row[12],
                        "timestamp": row[13],
                    })
            
            # Sort by holders count if available, otherwise by total supply
            tokens.sort(key=lambda x: (x.get("holders_count") or 0, x.get("total_supply") or 0), reverse=True)
            
            return tokens[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get top tokens: {e}")
            return []


# Global instance
hedera_token_fetcher = HederaTokenFetcher()