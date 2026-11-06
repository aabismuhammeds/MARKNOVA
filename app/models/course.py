"""Course domain model."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Course:
    """Represents an academic course entity."""
    course_code: str
    course_name: str
    department: str
    credits: float
    semester: int
    description: Optional[str] = None
    is_active: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert course entity to dictionary."""
        return {
            "course_code": self.course_code,
            "course_name": self.course_name,
            "department": self.department,
            "credits": self.credits,
            "semester": self.semester,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
