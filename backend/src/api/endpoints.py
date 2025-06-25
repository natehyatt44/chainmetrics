from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from loguru import logger
from pydantic import BaseModel

from ..data_fetchers.coingecko import CoinGeckoFetcher
from ..data_fetchers.hedera import hedera_token_fetcher
from ..database.connection import db_manager

router = APIRouter()


class HBARResponse(BaseModel):
    """HBAR metrics response model."""
    timestamp: datetime
    price_usd: float
    market_cap: float
    volume_24h: float
    price_change_24h: float
    circulating_supply: float
    market_cap_rank: int


class PriceHistoryResponse(BaseModel):
    """Price history response model."""
    timestamp: datetime
    price_usd: float
    volume_24h: float


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: datetime
    database_connected: bool
    version: str = "1.0.0"


class TokenResponse(BaseModel):
    """Token data response model."""
    token_id: str
    name: str
    symbol: str
    price_usd: Optional[float]
    market_cap: Optional[float]
    volume_24h: Optional[float]
    price_change_24h: Optional[float]
    decimals: int
    total_supply: int
    holders_count: Optional[int]
    transfers_24h: Optional[int]
    token_type: str
    memo: str
    timestamp: datetime


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        # Test database connection
        db_manager.execute("SELECT 1")
        db_connected = True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_connected = False
    
    return HealthResponse(
        status="healthy" if db_connected else "unhealthy",
        timestamp=datetime.utcnow(),
        database_connected=db_connected,
    )


@router.get("/hbar/current", response_model=Optional[HBARResponse])
async def get_current_hbar_data():
    """Get current HBAR market data."""
    try:
        async with CoinGeckoFetcher() as fetcher:
            latest_data = await fetcher.get_latest_hbar_data()
            
            if latest_data:
                return HBARResponse(**latest_data)
            
            # If no data in database, fetch from API
            hbar_data = await fetcher.fetch_hbar_data()
            if hbar_data:
                await fetcher.save_hbar_data(hbar_data)
                return HBARResponse(
                    timestamp=hbar_data.timestamp,
                    price_usd=hbar_data.price_usd,
                    market_cap=hbar_data.market_cap,
                    volume_24h=hbar_data.volume_24h,
                    price_change_24h=hbar_data.price_change_24h,
                    circulating_supply=hbar_data.circulating_supply,
                    market_cap_rank=hbar_data.market_cap_rank,
                )
            
            return None
            
    except Exception as e:
        logger.error(f"Failed to get current HBAR data: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch HBAR data")


@router.get("/hbar/history", response_model=List[PriceHistoryResponse])
async def get_hbar_price_history(
    days: int = Query(default=7, ge=1, le=365, description="Number of days of history to fetch")
):
    """Get HBAR price history."""
    try:
        async with CoinGeckoFetcher() as fetcher:
            history = await fetcher.get_hbar_price_history(days)
            return [PriceHistoryResponse(**item) for item in history]
            
    except Exception as e:
        logger.error(f"Failed to get HBAR price history: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch price history")


@router.get("/hbar/stats")
async def get_hbar_stats():
    """Get HBAR statistics and analytics."""
    try:
        query = """
            SELECT 
                COUNT(*) as total_records,
                MIN(price_usd) as min_price,
                MAX(price_usd) as max_price,
                AVG(price_usd) as avg_price,
                MIN(timestamp) as first_record,
                MAX(timestamp) as last_record
            FROM hbar_metrics
            WHERE timestamp >= (current_timestamp - interval '30 days')
        """
        
        result = db_manager.fetchone(query)
        if result:
            return {
                "total_records": result[0],
                "price_stats": {
                    "min_price_30d": result[1],
                    "max_price_30d": result[2],
                    "avg_price_30d": result[3],
                },
                "data_range": {
                    "first_record": result[4],
                    "last_record": result[5],
                },
                "timestamp": datetime.utcnow(),
            }
        
        return {"message": "No data available", "timestamp": datetime.utcnow()}
        
    except Exception as e:
        logger.error(f"Failed to get HBAR stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch statistics")


@router.post("/hbar/refresh")
async def refresh_hbar_data():
    """Manually refresh HBAR data from API."""
    try:
        async with CoinGeckoFetcher() as fetcher:
            hbar_data = await fetcher.fetch_hbar_data()
            if hbar_data:
                success = await fetcher.save_hbar_data(hbar_data)
                if success:
                    return {
                        "message": "HBAR data refreshed successfully",
                        "timestamp": datetime.utcnow(),
                        "data": {
                            "price_usd": hbar_data.price_usd,
                            "market_cap": hbar_data.market_cap,
                            "market_cap_rank": hbar_data.market_cap_rank,
                        },
                    }
            
            raise HTTPException(status_code=500, detail="Failed to refresh data")
            
    except Exception as e:
        logger.error(f"Failed to refresh HBAR data: {e}")
        raise HTTPException(status_code=500, detail="Failed to refresh HBAR data")


@router.get("/metrics/summary")
async def get_metrics_summary():
    """Get comprehensive metrics summary."""
    try:
        # Get latest HBAR data
        hbar_query = """
            SELECT price_usd, market_cap, volume_24h, price_change_24h, 
                   circulating_supply, market_cap_rank, timestamp
            FROM hbar_metrics
            ORDER BY timestamp DESC
            LIMIT 1
        """
        
        hbar_result = db_manager.fetchone(hbar_query)
        
        summary = {
            "timestamp": datetime.utcnow(),
            "hbar": None,
            "network": {
                "status": "coming_soon",
                "tps": None,
                "transactions_24h": None,
            },
            "tokens": {
                "status": "coming_soon",
                "top_tokens": [],
            },
        }
        
        if hbar_result:
            summary["hbar"] = {
                "price_usd": hbar_result[0],
                "market_cap": hbar_result[1],
                "volume_24h": hbar_result[2],
                "price_change_24h": hbar_result[3],
                "circulating_supply": hbar_result[4],
                "market_cap_rank": hbar_result[5],
                "last_updated": hbar_result[6],
            }
        
        return summary
        
    except Exception as e:
        logger.error(f"Failed to get metrics summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch metrics summary")


@router.get("/tokens/top", response_model=List[TokenResponse])
async def get_top_tokens(
    limit: int = Query(default=10, ge=1, le=50, description="Number of top tokens to return")
):
    """Get top Hedera DeFi tokens."""
    try:
        async with hedera_token_fetcher:
            tokens = await hedera_token_fetcher.get_top_tokens(limit)
            return [TokenResponse(**token) for token in tokens]
            
    except Exception as e:
        logger.error(f"Failed to get top tokens: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch top tokens")


@router.post("/tokens/refresh")
async def refresh_token_data():
    """Manually refresh token data from Hedera mirror node."""
    try:
        async with hedera_token_fetcher:
            tokens_data = await hedera_token_fetcher.fetch_data()
            if tokens_data:
                success = await hedera_token_fetcher.save_token_data(tokens_data)
                if success:
                    return {
                        "message": "Token data refreshed successfully",
                        "timestamp": datetime.utcnow(),
                        "tokens_count": len(tokens_data),
                    }
            
            raise HTTPException(status_code=500, detail="Failed to refresh token data")
            
    except Exception as e:
        logger.error(f"Failed to refresh token data: {e}")
        raise HTTPException(status_code=500, detail="Failed to refresh token data")


@router.get("/tokens/{token_id}", response_model=Optional[TokenResponse])
async def get_token_by_id(token_id: str):
    """Get specific token data by token ID."""
    try:
        query = """
            SELECT token_id, name, symbol, price_usd, market_cap, volume_24h,
                   price_change_24h, decimals, total_supply, holders_count,
                   transfers_24h, token_type, memo, timestamp
            FROM hedera_tokens 
            WHERE token_id = ?
            ORDER BY timestamp DESC
            LIMIT 1
        """
        
        result = db_manager.fetchone(query, (token_id,))
        
        if result:
            return TokenResponse(
                token_id=result[0],
                name=result[1],
                symbol=result[2],
                price_usd=result[3],
                market_cap=result[4],
                volume_24h=result[5],
                price_change_24h=result[6],
                decimals=result[7],
                total_supply=result[8],
                holders_count=result[9],
                transfers_24h=result[10],
                token_type=result[11],
                memo=result[12],
                timestamp=result[13],
            )
        
        return None
        
    except Exception as e:
        logger.error(f"Failed to get token {token_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch token data")