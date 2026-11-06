"""Domain models for Student Marks Management System."""
from __future__ import annotations

from app.models.student import Student
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.assessment import Assessment
from app.models.mark import StudentMark
from app.models.grading_scale import GradingScale
from app.models.setting import SystemSetting

__all__ = [
    "Student",
    "Course",
    "Enrollment",
    "Assessment",
    "StudentMark",
    "GradingScale",
    "SystemSetting",
]
