"""Student domain model."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Student:
    """Represents a student entity."""
    student_id: str
    first_name: str
    last_name: str
    email: str
    department: str
    semester: int
    academic_year: str
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None
    status: str = "active"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @property
    def full_name(self) -> str:
        """Return student's full name."""
        return f"{self.first_name} {self.last_name}".strip()

    def to_dict(self) -> dict:
        """Convert student entity to dictionary."""
        return {
            "student_id": self.student_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "date_of_birth": self.date_of_birth,
            "department": self.department,
            "semester": self.semester,
            "academic_year": self.academic_year,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
