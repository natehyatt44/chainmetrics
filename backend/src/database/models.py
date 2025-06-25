from datetime import datetime
from typing import Optional

import duckdb


class HBARMetrics:
    """HBAR price and market data model."""
    
    def __init__(
        self,
        timestamp: datetime,
        price_usd: float,
        market_cap: float,
        volume_24h: float,
        price_change_24h: float,
        circulating_supply: float,
        market_cap_rank: int,
    ):
        self.timestamp = timestamp
        self.price_usd = price_usd
        self.market_cap = market_cap
        self.volume_24h = volume_24h
        self.price_change_24h = price_change_24h
        self.circulating_supply = circulating_supply
        self.market_cap_rank = market_cap_rank


class HederaNetworkMetrics:
    """Hedera network performance metrics."""
    
    def __init__(
        self,
        timestamp: datetime,
        tps: float,
        transactions_24h: int,
        average_fee: float,
        consensus_nodes: int,
    ):
        self.timestamp = timestamp
        self.tps = tps
        self.transactions_24h = transactions_24h
        self.average_fee = average_fee
        self.consensus_nodes = consensus_nodes


class HederaTokenMetrics:
    """Hedera token data model."""
    
    def __init__(
        self,
        timestamp: datetime,
        token_id: str,
        name: str,
        symbol: str,
        price_usd: Optional[float],
        market_cap: Optional[float],
        volume_24h: Optional[float],
        price_change_24h: Optional[float],
    ):
        self.timestamp = timestamp
        self.token_id = token_id
        self.name = name
        self.symbol = symbol
        self.price_usd = price_usd
        self.market_cap = market_cap
        self.volume_24h = volume_24h
        self.price_change_24h = price_change_24h


def create_tables(conn: duckdb.DuckDBPyConnection) -> None:
    """Create all database tables."""
    
    # HBAR metrics table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS hbar_metrics (
            timestamp TIMESTAMP NOT NULL,
            price_usd DOUBLE NOT NULL,
            market_cap DOUBLE NOT NULL,
            volume_24h DOUBLE NOT NULL,
            price_change_24h DOUBLE NOT NULL,
            circulating_supply DOUBLE NOT NULL,
            market_cap_rank INTEGER NOT NULL,
            PRIMARY KEY (timestamp)
        )
    """)
    
    # Hedera network metrics table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS hedera_network_metrics (
            id INTEGER PRIMARY KEY,
            timestamp TIMESTAMP NOT NULL,
            tps DOUBLE NOT NULL,
            transactions_24h INTEGER NOT NULL,
            average_fee DOUBLE NOT NULL,
            consensus_nodes INTEGER NOT NULL
        )
    """)
    
    # Hedera tokens table  
    conn.execute("""
        CREATE TABLE IF NOT EXISTS hedera_tokens (
            timestamp TIMESTAMP NOT NULL,
            token_id VARCHAR NOT NULL,
            name VARCHAR NOT NULL,
            symbol VARCHAR NOT NULL,
            price_usd DOUBLE,
            market_cap DOUBLE,
            volume_24h DOUBLE,
            price_change_24h DOUBLE,
            decimals INTEGER DEFAULT 0,
            total_supply BIGINT DEFAULT 0,
            holders_count INTEGER,
            transfers_24h INTEGER,
            token_type VARCHAR DEFAULT 'FUNGIBLE_COMMON',
            memo VARCHAR DEFAULT '',
            PRIMARY KEY (timestamp, token_id)
        )
    """)
    
    # Create indexes for performance
    conn.execute("CREATE INDEX IF NOT EXISTS idx_hbar_timestamp ON hbar_metrics(timestamp)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_network_timestamp ON hedera_network_metrics(timestamp)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tokens_timestamp ON hedera_tokens(timestamp)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tokens_symbol ON hedera_tokens(symbol)")