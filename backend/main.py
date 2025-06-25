import asyncio
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from src.api.endpoints import router
from src.api.middleware import CacheControlMiddleware, LoggingMiddleware, SecurityMiddleware
from src.config import settings
from src.database.connection import db_manager
from src.schedulers.tasks import start_schedulers, stop_schedulers


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting ChainMetrics API server...")
    
    # Initialize database
    try:
        db_manager.connect()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        sys.exit(1)
    
    # Start background schedulers
    try:
        await start_schedulers()
        logger.info("Background schedulers started")
    except Exception as e:
        logger.error(f"Failed to start schedulers: {e}")
    
    logger.info("API server startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down ChainMetrics API server...")
    
    # Stop schedulers
    try:
        await stop_schedulers()
        logger.info("Background schedulers stopped")
    except Exception as e:
        logger.error(f"Error stopping schedulers: {e}")
    
    # Close database connection
    try:
        db_manager.close()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Error closing database: {e}")
    
    logger.info("API server shutdown complete")


def configure_logging():
    """Configure application logging."""
    logger.remove()  # Remove default handler
    
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    if settings.logging.format == "json":
        logger.add(
            sys.stdout,
            format="{time} | {level} | {name}:{function}:{line} | {message}",
            level=settings.logging.level,
            serialize=True,
        )
    else:
        logger.add(
            sys.stdout,
            format=log_format,
            level=settings.logging.level,
            colorize=True,
        )


def create_app() -> FastAPI:
    """Create FastAPI application."""
    configure_logging()
    
    app = FastAPI(
        title="ChainMetrics API",
        description="Hedera cryptocurrency metrics and analytics API",
        version="1.0.0",
        lifespan=lifespan,
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.api.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )
    
    # Add custom middleware
    app.add_middleware(SecurityMiddleware)
    app.add_middleware(CacheControlMiddleware, cache_max_age=300)
    app.add_middleware(LoggingMiddleware)
    
    # Include API routes
    app.include_router(router, prefix="/api/v1")
    
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "name": "ChainMetrics API",
            "version": "1.0.0",
            "description": "Hedera cryptocurrency metrics and analytics",
            "docs": "/docs",
        }
    
    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=True,
        log_config=None,  # Use our custom logging
    )