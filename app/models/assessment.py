"""Assessment domain model."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Assessment:
    """Represents an evaluation component for a course (e.g. Midterm, Final, Quiz)."""
    course_code: str
    name: str
    max_marks: float
    weightage_percent: float
    academic_year: str
    semester: int
    assessment_id: Optional[int] = None
    created_at: Optional[str] = None
    
    # Optional field populated from JOIN queries
    course_name: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert assessment entity to dictionary."""
        return {
            "assessment_id": self.assessment_id,
            "course_code": self.course_code,
            "course_name": self.course_name,
            "name": self.name,
            "max_marks": self.max_marks,
            "weightage_percent": self.weightage_percent,
            "academic_year": self.academic_year,
            "semester": self.semester,
            "created_at": self.created_at,
        }
