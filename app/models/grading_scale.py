"""Grading scale domain model."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class GradingScale:
    """Represents a grade boundary tier (e.g. A+: 90-100%, 4.0 GPA)."""
    letter_grade: str
    min_percentage: float
    max_percentage: float
    gpa_point: float
    description: Optional[str] = None
    scale_id: Optional[int] = None

    def to_dict(self) -> dict:
        """Convert grading scale entity to dictionary."""
        return {
            "scale_id": self.scale_id,
            "letter_grade": self.letter_grade,
            "min_percentage": self.min_percentage,
            "max_percentage": self.max_percentage,
            "gpa_point": self.gpa_point,
            "description": self.description,
        }
