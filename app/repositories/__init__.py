"""Repositories for Student Marks Management System."""
from __future__ import annotations

from app.repositories.base_repository import BaseRepository
from app.repositories.student_repository import StudentRepository
from app.repositories.course_repository import CourseRepository
from app.repositories.assessment_repository import AssessmentRepository
from app.repositories.marks_repository import MarksRepository
from app.repositories.config_repository import ConfigRepository

__all__ = [
    "BaseRepository",
    "StudentRepository",
    "CourseRepository",
    "AssessmentRepository",
    "MarksRepository",
    "ConfigRepository",
]
