import os
from pathlib import Path
from typing import Optional

import duckdb
from loguru import logger

from .models import create_tables


class DatabaseManager:
    """Manages DuckDB database connection and operations."""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or os.getenv("DATABASE_PATH", "./data/hedera_metrics.db")
        self._connection: Optional[duckdb.DuckDBPyConnection] = None
        self._ensure_data_directory()
    
    def _ensure_data_directory(self) -> None:
        """Ensure the data directory exists."""
        data_dir = Path(self.db_path).parent
        data_dir.mkdir(parents=True, exist_ok=True)
    
    def connect(self) -> duckdb.DuckDBPyConnection:
        """Get or create database connection."""
        if self._connection is None:
            try:
                self._connection = duckdb.connect(self.db_path)
                logger.info(f"Connected to database: {self.db_path}")
                create_tables(self._connection)
                logger.info("Database tables created/verified")
            except Exception as e:
                logger.error(f"Failed to connect to database: {e}")
                raise
        
        return self._connection
    
    def close(self) -> None:
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("Database connection closed")
    
    def execute(self, query: str, parameters: Optional[tuple] = None):
        """Execute a query with optional parameters."""
        conn = self.connect()
        try:
            if parameters:
                return conn.execute(query, parameters)
            return conn.execute(query)
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            logger.error(f"Query: {query}")
            raise
    
    def fetchall(self, query: str, parameters: Optional[tuple] = None) -> list:
        """Execute query and fetch all results."""
        result = self.execute(query, parameters)
        return result.fetchall()
    
    def fetchone(self, query: str, parameters: Optional[tuple] = None) -> Optional[tuple]:
        """Execute query and fetch one result."""
        result = self.execute(query, parameters)
        return result.fetchone()
    
    def execute_many(self, query: str, parameters_list: list) -> None:
        """Execute a query with multiple parameter sets."""
        conn = self.connect()
        try:
            conn.executemany(query, parameters_list)
        except Exception as e:
            logger.error(f"Batch query execution failed: {e}")
            logger.error(f"Query: {query}")
            raise


# Global database manager instance
db_manager = DatabaseManager()