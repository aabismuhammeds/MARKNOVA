"""Course enrollment domain model."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Enrollment:
    """Represents a student's enrollment in a course."""
    student_id: str
    course_code: str
    academic_year: str
    semester: int
    status: str = "enrolled"
    enrollment_id: Optional[int] = None
    enrolled_at: Optional[str] = None
    
    # Optional denormalized fields populated from JOIN queries
    student_name: Optional[str] = None
    course_name: Optional[str] = None
    credits: Optional[float] = None

    def to_dict(self) -> dict:
        """Convert enrollment entity to dictionary."""
        return {
            "enrollment_id": self.enrollment_id,
            "student_id": self.student_id,
            "course_code": self.course_code,
            "academic_year": self.academic_year,
            "semester": self.semester,
            "status": self.status,
            "enrolled_at": self.enrolled_at,
            "student_name": self.student_name,
            "course_name": self.course_name,
            "credits": self.credits,
        }
