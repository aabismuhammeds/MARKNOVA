"""Unit tests for CourseRepository and enrollments."""
from __future__ import annotations

import unittest
from app.core.database import DatabaseManager
from app.core.exceptions import DuplicateRecordError, RecordNotFoundError
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.student import Student
from app.repositories.course_repository import CourseRepository
from app.repositories.student_repository import StudentRepository


class TestCourseRepository(unittest.TestCase):
    """Test course and enrollment operations."""

    def setUp(self):
        """Initialize in-memory database and repositories."""
        self.db = DatabaseManager(":memory:")
        self.db.initialize_database()
        self.course_repo = CourseRepository(self.db)
        self.student_repo = StudentRepository(self.db)

        # Create sample student for enrollment testing
        self.student_repo.add(
            Student("STU-001", "John", "Doe", "john@test.org", "CS", 1, "2024-2025")
        )
        self.student_repo.add(
            Student("STU-002", "Jane", "Doe", "jane@test.org", "CS", 1, "2024-2025")
        )

    def test_add_and_get_course(self):
        """Test adding and retrieving a course."""
        course = Course(
            course_code="CS101",
            course_name="Introduction to Computer Science",
            department="Computer Science",
            credits=4.0,
            semester=1,
            description="Foundations of computing",
        )
        saved = self.course_repo.add(course)
        self.assertEqual(saved.course_code, "CS101")

        fetched = self.course_repo.get_by_code("CS101")
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.course_name, "Introduction to Computer Science")
        self.assertEqual(fetched.credits, 4.0)

    def test_update_course(self):
        """Test updating an existing course."""
        course = Course("CS102", "Data Structures", "CS", 3.0, 2)
        self.course_repo.add(course)

        course.credits = 4.0
        course.description = "Advanced trees and graphs"
        updated = self.course_repo.update(course)
        self.assertEqual(updated.credits, 4.0)
        self.assertEqual(updated.description, "Advanced trees and graphs")

    def test_delete_course(self):
        """Test deleting a course."""
        course = Course("CS103", "Algorithms", "CS", 4.0, 3)
        self.course_repo.add(course)
        self.assertTrue(self.course_repo.delete("CS103"))
        self.assertIsNone(self.course_repo.get_by_code("CS103"))

        with self.assertRaises(RecordNotFoundError):
            self.course_repo.delete("CS103")

    def test_enrollment_lifecycle(self):
        """Test enrolling, listing enrollments, and dropping a student."""
        self.course_repo.add(Course("CS101", "Intro to CS", "CS", 4.0, 1))

        enrollment = Enrollment(
            student_id="STU-001",
            course_code="CS101",
            academic_year="2024-2025",
            semester=1,
        )
        saved_enr = self.course_repo.enroll_student(enrollment)
        self.assertIsNotNone(saved_enr.enrollment_id)

        # Check is_enrolled
        self.assertTrue(
            self.course_repo.is_enrolled("STU-001", "CS101", "2024-2025", 1)
        )
        self.assertFalse(
            self.course_repo.is_enrolled("STU-002", "CS101", "2024-2025", 1)
        )

        # List enrollments for student
        student_enrs = self.course_repo.get_enrollments_for_student("STU-001")
        self.assertEqual(len(student_enrs), 1)
        self.assertEqual(student_enrs[0].course_code, "CS101")
        self.assertEqual(student_enrs[0].course_name, "Intro to CS")

        # List enrollments for course
        course_enrs = self.course_repo.get_enrollments_for_course("CS101")
        self.assertEqual(len(course_enrs), 1)
        self.assertEqual(course_enrs[0].student_id, "STU-001")
        self.assertEqual(course_enrs[0].student_name, "John Doe")

        # Drop student
        self.assertTrue(
            self.course_repo.drop_student("STU-001", "CS101", "2024-2025", 1)
        )
        self.assertFalse(
            self.course_repo.is_enrolled("STU-001", "CS101", "2024-2025", 1)
        )

    def test_duplicate_enrollment_prevention(self):
        """Attempting to enroll same student twice in same term offering raises DuplicateRecordError."""
        self.course_repo.add(Course("CS101", "Intro to CS", "CS", 4.0, 1))
        e1 = Enrollment("STU-001", "CS101", "2024-2025", 1)
        e2 = Enrollment("STU-001", "CS101", "2024-2025", 1)

        self.course_repo.enroll_student(e1)
        with self.assertRaises(DuplicateRecordError):
            self.course_repo.enroll_student(e2)

    def test_bulk_enroll(self):
        """Test enrolling multiple students in batch."""
        self.course_repo.add(Course("CS101", "Intro to CS", "CS", 4.0, 1))
        enrollments = [
            Enrollment("STU-001", "CS101", "2024-2025", 1),
            Enrollment("STU-002", "CS101", "2024-2025", 1),
        ]
        count = self.course_repo.bulk_enroll(enrollments)
        self.assertEqual(count, 2)
        course_enrs = self.course_repo.get_enrollments_for_course("CS101")
        self.assertEqual(len(course_enrs), 2)


if __name__ == "__main__":
    unittest.main()
