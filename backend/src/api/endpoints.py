from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from loguru import logger
from pydantic import BaseModel

from ..data_fetchers.coingecko import CoinGeckoFetcher
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