import asyncio
from datetime import datetime
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger

from ..config import settings
from ..data_fetchers.coingecko import CoinGeckoFetcher

# Global scheduler instance  
scheduler: Optional[AsyncIOScheduler] = None


async def fetch_and_save_hbar_data():
    """Scheduled task to fetch and save HBAR data."""
    try:
        logger.info("Starting scheduled HBAR data fetch")
        
        async with CoinGeckoFetcher() as fetcher:
            hbar_data = await fetcher.fetch_hbar_data()
            if hbar_data:
                success = await fetcher.save_hbar_data(hbar_data)
                if success:
                    logger.info(f"HBAR data saved: ${hbar_data.price_usd:.4f} USD")
                else:
                    logger.error("Failed to save HBAR data to database")
            else:
                logger.warning("No HBAR data received from API")
                
    except Exception as e:
        logger.error(f"Scheduled HBAR data fetch failed: {e}")


async def log_scheduler_status():
    """Scheduled task to log scheduler status."""
    logger.info(f"Scheduler status check - {datetime.utcnow()}")


async def start_schedulers():
    """Start all background schedulers."""
    global scheduler
    
    if scheduler is not None:
        logger.warning("Schedulers already running")
        return
    
    scheduler = AsyncIOScheduler()
    
    # Add HBAR data fetching job
    scheduler.add_job(
        fetch_and_save_hbar_data,
        "interval",
        seconds=settings.updates.hbar_interval,
        id="hbar_data_fetch",
        max_instances=1,
        coalesce=True,
    )
    
    # Add status logging job (every 30 minutes)
    scheduler.add_job(
        log_scheduler_status,
        "interval",
        minutes=30,
        id="scheduler_status",
        max_instances=1,
    )
    
    # Start scheduler
    scheduler.start()
    logger.info("Background schedulers started successfully")
    
    # Run initial data fetch
    try:
        await fetch_and_save_hbar_data()
    except Exception as e:
        logger.error(f"Initial data fetch failed: {e}")


async def stop_schedulers():
    """Stop all background schedulers."""
    global scheduler
    
    if scheduler is not None:
        scheduler.shutdown(wait=True)
        scheduler = None
        logger.info("Background schedulers stopped")
    else:
        logger.info("No schedulers running")


def get_scheduler_status() -> dict:
    """Get current scheduler status."""
    global scheduler
    
    if scheduler is None:
        return {"running": False, "jobs": []}
    
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run": job.next_run_time,
            "func": job.func.__name__,
        })
    
    return {
        "running": scheduler.running,
        "jobs": jobs,
        "state": scheduler.state,
    }