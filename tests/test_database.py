"""Unit tests for SQLite database manager, migrations, and constraints."""
from __future__ import annotations

import unittest
from app.core.database import DatabaseManager
from app.core.exceptions import (
    DatabaseError,
    DuplicateRecordError,
    ForeignKeyViolationError,
)


class TestDatabaseManager(unittest.TestCase):
    """Test database initialization, migrations, and relational integrity constraints."""

    def setUp(self):
        """Create an in-memory database for isolated testing."""
        self.db = DatabaseManager(":memory:")
        self.db.initialize_database()

    def test_schema_initialization_and_migrations(self):
        """Verify schema migrations table is populated and all tables are created."""
        applied = self.db.get_applied_migrations()
        self.assertIn(1, applied)

        with self.db.get_connection() as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name ASC;"
            )
            tables = [row["name"] for row in cursor.fetchall()]

        expected_tables = [
            "assessments",
            "courses",
            "enrollments",
            "grading_scales",
            "schema_migrations",
            "student_marks",
            "students",
            "system_settings",
        ]
        for tbl in expected_tables:
            self.assertIn(tbl, tables, f"Expected table '{tbl}' was not created.")

    def test_foreign_key_enforcement(self):
        """Verify foreign key violations raise ForeignKeyViolationError."""
        with self.assertRaises(ForeignKeyViolationError):
            with self.db.get_connection() as conn:
                # Inserting an enrollment for a non-existent student must fail
                conn.execute(
                    """
                    INSERT INTO enrollments (student_id, course_code, academic_year, semester)
                    VALUES ('NONEXISTENT', 'CS101', '2024-2025', 1);
                    """
                )

    def test_unique_constraint_enforcement(self):
        """Verify duplicate keys raise DuplicateRecordError."""
        with self.db.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO students (
                    student_id, first_name, last_name, email, department, semester, academic_year
                ) VALUES ('STU-001', 'John', 'Doe', 'john@test.edu', 'CS', 1, '2024-2025');
                """
            )

        # Attempt duplicate primary key
        with self.assertRaises(DuplicateRecordError):
            with self.db.get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO students (
                        student_id, first_name, last_name, email, department, semester, academic_year
                    ) VALUES ('STU-001', 'Jane', 'Smith', 'jane@test.edu', 'CS', 1, '2024-2025');
                    """
                )

        # Attempt duplicate email
        with self.assertRaises(DuplicateRecordError):
            with self.db.get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO students (
                        student_id, first_name, last_name, email, department, semester, academic_year
                    ) VALUES ('STU-002', 'Jane', 'Smith', 'john@test.edu', 'CS', 1, '2024-2025');
                    """
                )

    def test_check_constraints(self):
        """Verify check constraints prevent invalid values."""
        # Invalid semester (> 12)
        with self.assertRaises(DatabaseError):
            with self.db.get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO students (
                        student_id, first_name, last_name, email, department, semester, academic_year
                    ) VALUES ('STU-003', 'Bob', 'Ross', 'bob@test.edu', 'CS', 15, '2024-2025');
                    """
                )

        # Negative credits on course
        with self.assertRaises(DatabaseError):
            with self.db.get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO courses (
                        course_code, course_name, department, credits, semester
                    ) VALUES ('CS999', 'Invalid Course', 'CS', -3.0, 1);
                    """
                )

    def test_cascade_delete(self):
        """Verify deleting a student cascades and deletes their enrollments and marks."""
        with self.db.get_connection() as conn:
            # Insert student
            conn.execute(
                """
                INSERT INTO students (
                    student_id, first_name, last_name, email, department, semester, academic_year
                ) VALUES ('STU-100', 'Alice', 'Walker', 'alice@test.edu', 'CS', 1, '2024-2025');
                """
            )
            # Insert course
            conn.execute(
                """
                INSERT INTO courses (
                    course_code, course_name, department, credits, semester
                ) VALUES ('CS101', 'Intro to Programming', 'CS', 4.0, 1);
                """
            )
            # Insert enrollment
            conn.execute(
                """
                INSERT INTO enrollments (student_id, course_code, academic_year, semester)
                VALUES ('STU-100', 'CS101', '2024-2025', 1);
                """
            )
            # Insert assessment
            cursor = conn.execute(
                """
                INSERT INTO assessments (course_code, name, max_marks, weightage_percent, academic_year, semester)
                VALUES ('CS101', 'Midterm', 100.0, 30.0, '2024-2025', 1);
                """
            )
            assessment_id = cursor.lastrowid
            # Insert mark
            conn.execute(
                """
                INSERT INTO student_marks (student_id, assessment_id, marks_obtained)
                VALUES ('STU-100', ?, 88.5);
                """,
                (assessment_id,),
            )

        # Delete student
        with self.db.get_connection() as conn:
            conn.execute("DELETE FROM students WHERE student_id = 'STU-100';")

            # Verify enrollments and marks are automatically deleted
            enrollments_cnt = conn.execute("SELECT COUNT(*) as c FROM enrollments;").fetchone()["c"]
            marks_cnt = conn.execute("SELECT COUNT(*) as c FROM student_marks;").fetchone()["c"]
            self.assertEqual(enrollments_cnt, 0)
            self.assertEqual(marks_cnt, 0)


if __name__ == "__main__":
    unittest.main()
