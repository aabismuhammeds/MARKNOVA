"""Student mark domain model."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class StudentMark:
    """Represents a score obtained by a student on a specific assessment."""
    student_id: str
    assessment_id: int
    marks_obtained: Optional[float] = None
    is_absent: bool = False
    remarks: Optional[str] = None
    mark_id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    # Denormalized fields from JOIN queries
    student_name: Optional[str] = None
    course_code: Optional[str] = None
    course_name: Optional[str] = None
    assessment_name: Optional[str] = None
    max_marks: Optional[float] = None
    weightage_percent: Optional[float] = None

    @property
    def percentage(self) -> Optional[float]:
        """Calculate score percentage if max_marks is available and student was present."""
        if self.is_absent:
            return 0.0
        if self.marks_obtained is not None and self.max_marks and self.max_marks > 0:
            return round((self.marks_obtained / self.max_marks) * 100.0, 2)
        return None

    def to_dict(self) -> dict:
        """Convert mark entity to dictionary."""
        return {
            "mark_id": self.mark_id,
            "student_id": self.student_id,
            "student_name": self.student_name,
            "assessment_id": self.assessment_id,
            "assessment_name": self.assessment_name,
            "course_code": self.course_code,
            "course_name": self.course_name,
            "max_marks": self.max_marks,
            "marks_obtained": self.marks_obtained,
            "is_absent": self.is_absent,
            "percentage": self.percentage,
            "weightage_percent": self.weightage_percent,
            "remarks": self.remarks,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
