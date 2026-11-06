"""Repository for Course and Enrollment entities."""
from __future__ import annotations

from typing import List, Optional
import sqlite3

from app.core.exceptions import RecordNotFoundError
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.repositories.base_repository import BaseRepository


class CourseRepository(BaseRepository):
    """Data access repository for courses and student enrollments."""

    def _row_to_course(self, row: sqlite3.Row) -> Course:
        return Course(
            course_code=row["course_code"],
            course_name=row["course_name"],
            department=row["department"],
            credits=float(row["credits"]),
            semester=int(row["semester"]),
            description=row["description"],
            is_active=bool(row["is_active"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def _row_to_enrollment(self, row: sqlite3.Row) -> Enrollment:
        keys = row.keys()
        return Enrollment(
            enrollment_id=row["enrollment_id"],
            student_id=row["student_id"],
            course_code=row["course_code"],
            academic_year=row["academic_year"],
            semester=int(row["semester"]),
            status=row["status"],
            enrolled_at=row["enrolled_at"],
            student_name=f"{row['first_name']} {row['last_name']}".strip() if "first_name" in keys and "last_name" in keys else None,
            course_name=row["course_name"] if "course_name" in keys else None,
            credits=float(row["credits"]) if "credits" in keys and row["credits"] is not None else None,
        )

    # ---------------- Course CRUD ----------------

    def add(self, course: Course) -> Course:
        """Insert a new course into the database."""
        query = """
            INSERT INTO courses (
                course_code, course_name, department, credits, semester, description, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?);
        """
        with self.db.get_connection() as conn:
            conn.execute(
                query,
                (
                    course.course_code,
                    course.course_name,
                    course.department,
                    course.credits,
                    course.semester,
                    course.description,
                    1 if course.is_active else 0,
                ),
            )
        return self.get_by_code(course.course_code) or course

    def update(self, course: Course) -> Course:
        """Update an existing course."""
        query = """
            UPDATE courses SET
                course_name = ?,
                department = ?,
                credits = ?,
                semester = ?,
                description = ?,
                is_active = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE course_code = ?;
        """
        with self.db.get_connection() as conn:
            cursor = conn.execute(
                query,
                (
                    course.course_name,
                    course.department,
                    course.credits,
                    course.semester,
                    course.description,
                    1 if course.is_active else 0,
                    course.course_code,
                ),
            )
            if cursor.rowcount == 0:
                raise RecordNotFoundError(f"Course '{course.course_code}' not found.")
        return self.get_by_code(course.course_code) or course

    def delete(self, course_code: str) -> bool:
        """Delete a course. Cascades to enrollments, assessments, and marks."""
        with self.db.get_connection() as conn:
            cursor = conn.execute("DELETE FROM courses WHERE course_code = ?;", (course_code,))
            if cursor.rowcount == 0:
                raise RecordNotFoundError(f"Course '{course_code}' not found.")
            return True

    def get_by_code(self, course_code: str) -> Optional[Course]:
        """Retrieve course by unique course code."""
        row = self.fetch_one("SELECT * FROM courses WHERE course_code = ?;", (course_code,))
        return self._row_to_course(row) if row else None

    def list_all(
        self,
        department: Optional[str] = None,
        semester: Optional[int] = None,
        is_active: Optional[bool] = None,
    ) -> List[Course]:
        """List all courses with optional filtering."""
        clauses = []
        params: List[object] = []

        if department:
            clauses.append("department = ?")
            params.append(department)
        if semester is not None:
            clauses.append("semester = ?")
            params.append(semester)
        if is_active is not None:
            clauses.append("is_active = ?")
            params.append(1 if is_active else 0)

        where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        query = f"SELECT * FROM courses {where_sql} ORDER BY semester ASC, course_code ASC;"
        rows = self.fetch_all(query, tuple(params))
        return [self._row_to_course(row) for row in rows]

    def get_departments(self) -> List[str]:
        """Get unique departments offering courses."""
        rows = self.fetch_all("SELECT DISTINCT department FROM courses ORDER BY department ASC;")
        return [row["department"] for row in rows]

    # ---------------- Enrollment Operations ----------------

    def enroll_student(self, enrollment: Enrollment) -> Enrollment:
        """Enroll a student in a course."""
        query = """
            INSERT INTO enrollments (student_id, course_code, academic_year, semester, status)
            VALUES (?, ?, ?, ?, ?);
        """
        with self.db.get_connection() as conn:
            cursor = conn.execute(
                query,
                (
                    enrollment.student_id,
                    enrollment.course_code,
                    enrollment.academic_year,
                    enrollment.semester,
                    enrollment.status,
                ),
            )
            enrollment.enrollment_id = cursor.lastrowid
        return enrollment

    def bulk_enroll(self, enrollments: List[Enrollment]) -> int:
        """Enroll multiple students in batch."""
        if not enrollments:
            return 0
        query = """
            INSERT OR IGNORE INTO enrollments (student_id, course_code, academic_year, semester, status)
            VALUES (?, ?, ?, ?, ?);
        """
        with self.db.get_connection() as conn:
            data = [
                (e.student_id, e.course_code, e.academic_year, e.semester, e.status)
                for e in enrollments
            ]
            cursor = conn.executemany(query, data)
            return cursor.rowcount

    def drop_student(
        self, student_id: str, course_code: str, academic_year: str, semester: int
    ) -> bool:
        """Remove or drop student enrollment."""
        query = """
            DELETE FROM enrollments
            WHERE student_id = ? AND course_code = ? AND academic_year = ? AND semester = ?;
        """
        with self.db.get_connection() as conn:
            cursor = conn.execute(query, (student_id, course_code, academic_year, semester))
            if cursor.rowcount == 0:
                raise RecordNotFoundError("Enrollment record not found.")
            return True

    def get_enrollments_for_student(
        self,
        student_id: str,
        academic_year: Optional[str] = None,
        semester: Optional[int] = None,
    ) -> List[Enrollment]:
        """Retrieve all course enrollments for a specific student."""
        clauses = ["e.student_id = ?"]
        params: List[object] = [student_id]

        if academic_year:
            clauses.append("e.academic_year = ?")
            params.append(academic_year)
        if semester is not None:
            clauses.append("e.semester = ?")
            params.append(semester)

        where_sql = f"WHERE {' AND '.join(clauses)}"
        query = f"""
            SELECT e.*, c.course_name, c.credits, s.first_name, s.last_name
            FROM enrollments e
            JOIN courses c ON e.course_code = c.course_code
            JOIN students s ON e.student_id = s.student_id
            {where_sql}
            ORDER BY e.semester ASC, e.course_code ASC;
        """
        rows = self.fetch_all(query, tuple(params))
        return [self._row_to_enrollment(row) for row in rows]

    def get_enrollments_for_course(
        self,
        course_code: str,
        academic_year: Optional[str] = None,
        semester: Optional[int] = None,
    ) -> List[Enrollment]:
        """Retrieve all student enrollments for a specific course."""
        clauses = ["e.course_code = ?"]
        params: List[object] = [course_code]

        if academic_year:
            clauses.append("e.academic_year = ?")
            params.append(academic_year)
        if semester is not None:
            clauses.append("e.semester = ?")
            params.append(semester)

        where_sql = f"WHERE {' AND '.join(clauses)}"
        query = f"""
            SELECT e.*, c.course_name, c.credits, s.first_name, s.last_name
            FROM enrollments e
            JOIN courses c ON e.course_code = c.course_code
            JOIN students s ON e.student_id = s.student_id
            {where_sql}
            ORDER BY s.student_id ASC;
        """
        rows = self.fetch_all(query, tuple(params))
        return [self._row_to_enrollment(row) for row in rows]

    def is_enrolled(
        self, student_id: str, course_code: str, academic_year: str, semester: int
    ) -> bool:
        """Check if a student is enrolled in a specific course."""
        query = """
            SELECT 1 FROM enrollments
            WHERE student_id = ? AND course_code = ? AND academic_year = ? AND semester = ?;
        """
        return self.fetch_one(query, (student_id, course_code, academic_year, semester)) is not None
