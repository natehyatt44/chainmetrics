import os
from typing import List

from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables
load_dotenv()


class APIConfig(BaseModel):
    """API server configuration."""
    host: str = os.getenv("API_HOST", "0.0.0.0")
    port: int = int(os.getenv("API_PORT", "8000"))
    cors_origins: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")


class DatabaseConfig(BaseModel):
    """Database configuration."""
    path: str = os.getenv("DATABASE_PATH", "./data/hedera_metrics.db")


class CoinGeckoConfig(BaseModel):
    """CoinGecko API configuration."""
    api_key: str = os.getenv("COINGECKO_API_KEY", "")
    requests_per_minute: int = int(os.getenv("COINGECKO_REQUESTS_PER_MINUTE", "25"))
    base_url: str = "https://api.coingecko.com/api/v3"


class HederaConfig(BaseModel):
    """Hedera network configuration."""
    mirror_node_url: str = os.getenv("HEDERA_MIRROR_NODE_URL", "https://mainnet-public.mirrornode.hedera.com")


class UpdateConfig(BaseModel):
    """Data update intervals configuration."""
    hbar_interval: int = int(os.getenv("HBAR_UPDATE_INTERVAL", "300"))  # 5 minutes
    network_interval: int = int(os.getenv("NETWORK_UPDATE_INTERVAL", "60"))  # 1 minute
    tokens_interval: int = int(os.getenv("TOKENS_UPDATE_INTERVAL", "600"))  # 10 minutes


class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str = os.getenv("LOG_LEVEL", "INFO")
    format: str = os.getenv("LOG_FORMAT", "json")


class Settings(BaseModel):
    """Application settings."""
    api: APIConfig = APIConfig()
    database: DatabaseConfig = DatabaseConfig()
    coingecko: CoinGeckoConfig = CoinGeckoConfig()
    hedera: HederaConfig = HederaConfig()
    updates: UpdateConfig = UpdateConfig()
    logging: LoggingConfig = LoggingConfig()


# Global settings instance
settings = Settings()