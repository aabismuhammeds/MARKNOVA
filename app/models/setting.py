"""System setting domain model."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class SystemSetting:
    """Represents a system key-value configuration item."""
    key: str
    value: str
    category: str = "general"
    updated_at: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert system setting to dictionary."""
        return {
            "key": self.key,
            "value": self.value,
            "category": self.category,
            "updated_at": self.updated_at,
        }
