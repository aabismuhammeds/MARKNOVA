"""Base repository providing database access utilities."""
from __future__ import annotations

from typing import Any, List, Optional
import sqlite3

from app.core.database import DatabaseManager


class BaseRepository:
    """Base class for SQL repositories."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a query within a transactional connection context."""
        with self.db.get_connection() as conn:
            return conn.execute(query, params)

    def fetch_one(self, query: str, params: tuple = ()) -> Optional[sqlite3.Row]:
        """Fetch a single row matching the query."""
        with self.db.get_connection() as conn:
            cursor = conn.execute(query, params)
            return cursor.fetchone()

    def fetch_all(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """Fetch all rows matching the query."""
        with self.db.get_connection() as conn:
            cursor = conn.execute(query, params)
            return cursor.fetchall()
