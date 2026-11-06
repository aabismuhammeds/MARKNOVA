"""Unit tests for StudentRepository."""
from __future__ import annotations

import unittest
from app.core.database import DatabaseManager
from app.core.exceptions import DuplicateRecordError, RecordNotFoundError
from app.models.student import Student
from app.repositories.student_repository import StudentRepository


class TestStudentRepository(unittest.TestCase):
    """Test student repository operations."""

    def setUp(self):
        """Initialize in-memory database and repository."""
        self.db = DatabaseManager(":memory:")
        self.db.initialize_database()
        self.repo = StudentRepository(self.db)

    def test_add_and_get_student(self):
        """Test adding and retrieving a student."""
        student = Student(
            student_id="STU-001",
            first_name="Alan",
            last_name="Turing",
            email="alan@turing.org",
            department="Computer Science",
            semester=1,
            academic_year="2024-2025",
            phone="1234567890",
        )
        saved = self.repo.add(student)
        self.assertEqual(saved.student_id, "STU-001")
        self.assertEqual(saved.full_name, "Alan Turing")

        fetched = self.repo.get_by_id("STU-001")
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.first_name, "Alan")
        self.assertEqual(fetched.email, "alan@turing.org")

        fetched_by_email = self.repo.get_by_email("alan@turing.org")
        self.assertIsNotNone(fetched_by_email)
        self.assertEqual(fetched_by_email.student_id, "STU-001")

    def test_update_student(self):
        """Test updating an existing student."""
        student = Student(
            student_id="STU-002",
            first_name="Grace",
            last_name="Hopper",
            email="grace@navy.mil",
            department="Computer Science",
            semester=2,
            academic_year="2024-2025",
        )
        self.repo.add(student)

        student.first_name = "Rear Admiral Grace"
        student.status = "graduated"
        updated = self.repo.update(student)

        self.assertEqual(updated.first_name, "Rear Admiral Grace")
        self.assertEqual(updated.status, "graduated")

    def test_update_nonexistent_student_raises_error(self):
        """Updating a non-existent student should raise RecordNotFoundError."""
        student = Student(
            student_id="STU-NONEXISTENT",
            first_name="Ghost",
            last_name="User",
            email="ghost@test.org",
            department="CS",
            semester=1,
            academic_year="2024-2025",
        )
        with self.assertRaises(RecordNotFoundError):
            self.repo.update(student)

    def test_delete_student(self):
        """Test deleting a student."""
        student = Student(
            student_id="STU-003",
            first_name="Ada",
            last_name="Lovelace",
            email="ada@analytical.org",
            department="Mathematics",
            semester=1,
            academic_year="2024-2025",
        )
        self.repo.add(student)
        self.assertTrue(self.repo.delete("STU-003"))
        self.assertIsNone(self.repo.get_by_id("STU-003"))

        # Deleting again should raise RecordNotFoundError
        with self.assertRaises(RecordNotFoundError):
            self.repo.delete("STU-003")

    def test_list_and_search_filtering(self):
        """Test listing with department, semester, and search filters."""
        students = [
            Student("STU-101", "Alice", "Smith", "alice@test.org", "CS", 1, "2024-2025"),
            Student("STU-102", "Bob", "Jones", "bob@test.org", "CS", 2, "2024-2025"),
            Student("STU-103", "Charlie", "Brown", "charlie@test.org", "EE", 1, "2024-2025"),
            Student("STU-104", "Alice", "Wonderland", "wonder@test.org", "EE", 2, "2024-2025"),
        ]
        for s in students:
            self.repo.add(s)

        # Filter by department
        cs_students = self.repo.list_all(department="CS")
        self.assertEqual(len(cs_students), 2)

        # Filter by semester
        sem1_students = self.repo.list_all(semester=1)
        self.assertEqual(len(sem1_students), 2)

        # Search by name
        alices = self.repo.list_all(search="Alice")
        self.assertEqual(len(alices), 2)

        # Search by ID
        found_id = self.repo.list_all(search="103")
        self.assertEqual(len(found_id), 1)
        self.assertEqual(found_id[0].first_name, "Charlie")

        # Count
        self.assertEqual(self.repo.count(), 4)
        self.assertEqual(self.repo.count(department="EE"), 2)

    def test_duplicate_email_raises_error(self):
        """Attempting to add two students with same email must raise DuplicateRecordError."""
        s1 = Student("STU-201", "User1", "One", "dup@test.org", "CS", 1, "2024-2025")
        s2 = Student("STU-202", "User2", "Two", "dup@test.org", "CS", 1, "2024-2025")
        self.repo.add(s1)
        with self.assertRaises(DuplicateRecordError):
            self.repo.add(s2)


if __name__ == "__main__":
    unittest.main()
