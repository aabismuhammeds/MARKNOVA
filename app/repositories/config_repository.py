"""Repository for GradingScale and SystemSetting entities."""
from __future__ import annotations

from typing import List, Optional
import sqlite3

from app.models.grading_scale import GradingScale
from app.models.setting import SystemSetting
from app.repositories.base_repository import BaseRepository


class ConfigRepository(BaseRepository):
    """Repository for managing grading scale boundaries and application settings."""

    # ---------------- Grading Scale Operations ----------------

    def _row_to_scale(self, row: sqlite3.Row) -> GradingScale:
        return GradingScale(
            scale_id=row["scale_id"],
            letter_grade=row["letter_grade"],
            min_percentage=float(row["min_percentage"]),
            max_percentage=float(row["max_percentage"]),
            gpa_point=float(row["gpa_point"]),
            description=row["description"],
        )

    def get_grading_scales(self) -> List[GradingScale]:
        """Get all configured grading scale tiers ordered by percentage descending."""
        rows = self.fetch_all(
            "SELECT * FROM grading_scales ORDER BY min_percentage DESC;"
        )
        return [self._row_to_scale(row) for row in rows]

    def set_grading_scales(self, scales: List[GradingScale]) -> None:
        """Replace existing grading scale tiers with a new set."""
        with self.db.get_connection() as conn:
            conn.execute("DELETE FROM grading_scales;")
            query = """
                INSERT INTO grading_scales (
                    letter_grade, min_percentage, max_percentage, gpa_point, description
                ) VALUES (?, ?, ?, ?, ?);
            """
            data = [
                (s.letter_grade, s.min_percentage, s.max_percentage, s.gpa_point, s.description)
                for s in scales
            ]
            conn.executemany(query, data)

    # ---------------- System Settings Operations ----------------

    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Fetch setting value by key."""
        row = self.fetch_one("SELECT value FROM system_settings WHERE key = ?;", (key,))
        return row["value"] if row else default

    def set_setting(self, key: str, value: str, category: str = "general") -> None:
        """Upsert a system setting."""
        query = """
            INSERT INTO system_settings (key, value, category, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                category = excluded.category,
                updated_at = CURRENT_TIMESTAMP;
        """
        with self.db.get_connection() as conn:
            conn.execute(query, (key, value, category))
