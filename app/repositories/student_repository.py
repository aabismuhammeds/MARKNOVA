"""Repository for Student entities."""
from __future__ import annotations

from typing import List, Optional
import sqlite3

from app.core.exceptions import RecordNotFoundError
from app.models.student import Student
from app.repositories.base_repository import BaseRepository


class StudentRepository(BaseRepository):
    """Data access repository for students."""

    def _row_to_student(self, row: sqlite3.Row) -> Student:
        return Student(
            student_id=row["student_id"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            email=row["email"],
            phone=row["phone"],
            date_of_birth=row["date_of_birth"],
            department=row["department"],
            semester=row["semester"],
            academic_year=row["academic_year"],
            status=row["status"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def add(self, student: Student) -> Student:
        """Insert a new student record into the database."""
        query = """
            INSERT INTO students (
                student_id, first_name, last_name, email, phone,
                date_of_birth, department, semester, academic_year, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        with self.db.get_connection() as conn:
            conn.execute(
                query,
                (
                    student.student_id,
                    student.first_name,
                    student.last_name,
                    student.email,
                    student.phone,
                    student.date_of_birth,
                    student.department,
                    student.semester,
                    student.academic_year,
                    student.status,
                ),
            )
        return self.get_by_id(student.student_id) or student

    def update(self, student: Student) -> Student:
        """Update an existing student record."""
        query = """
            UPDATE students SET
                first_name = ?,
                last_name = ?,
                email = ?,
                phone = ?,
                date_of_birth = ?,
                department = ?,
                semester = ?,
                academic_year = ?,
                status = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE student_id = ?;
        """
        with self.db.get_connection() as conn:
            cursor = conn.execute(
                query,
                (
                    student.first_name,
                    student.last_name,
                    student.email,
                    student.phone,
                    student.date_of_birth,
                    student.department,
                    student.semester,
                    student.academic_year,
                    student.status,
                    student.student_id,
                ),
            )
            if cursor.rowcount == 0:
                raise RecordNotFoundError(f"Student with ID '{student.student_id}' not found.")
        return self.get_by_id(student.student_id) or student

    def delete(self, student_id: str) -> bool:
        """Delete a student by ID. Cascade-deletes enrollments and marks."""
        with self.db.get_connection() as conn:
            cursor = conn.execute("DELETE FROM students WHERE student_id = ?;", (student_id,))
            if cursor.rowcount == 0:
                raise RecordNotFoundError(f"Student with ID '{student_id}' not found.")
            return True

    def get_by_id(self, student_id: str) -> Optional[Student]:
        """Retrieve a student by their unique student_id."""
        row = self.fetch_one("SELECT * FROM students WHERE student_id = ?;", (student_id,))
        return self._row_to_student(row) if row else None

    def get_by_email(self, email: str) -> Optional[Student]:
        """Retrieve a student by their unique email."""
        row = self.fetch_one("SELECT * FROM students WHERE email = ?;", (email,))
        return self._row_to_student(row) if row else None

    def list_all(
        self,
        department: Optional[str] = None,
        semester: Optional[int] = None,
        academic_year: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[Student]:
        """Query students with optional filtering and pagination."""
        clauses = []
        params: List[object] = []

        if department:
            clauses.append("department = ?")
            params.append(department)
        if semester is not None:
            clauses.append("semester = ?")
            params.append(semester)
        if academic_year:
            clauses.append("academic_year = ?")
            params.append(academic_year)
        if status:
            clauses.append("status = ?")
            params.append(status)
        if search:
            search_param = f"%{search.strip()}%"
            clauses.append(
                "(student_id LIKE ? OR first_name LIKE ? OR last_name LIKE ? OR email LIKE ?)"
            )
            params.extend([search_param, search_param, search_param, search_param])

        where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        pagination_sql = ""
        if limit is not None:
            pagination_sql = f"LIMIT {int(limit)}"
            if offset is not None:
                pagination_sql += f" OFFSET {int(offset)}"

        query = f"SELECT * FROM students {where_sql} ORDER BY student_id ASC {pagination_sql};"
        rows = self.fetch_all(query, tuple(params))
        return [self._row_to_student(row) for row in rows]

    def count(
        self,
        department: Optional[str] = None,
        semester: Optional[int] = None,
        status: Optional[str] = None,
    ) -> int:
        """Count students matching filter criteria."""
        clauses = []
        params: List[object] = []

        if department:
            clauses.append("department = ?")
            params.append(department)
        if semester is not None:
            clauses.append("semester = ?")
            params.append(semester)
        if status:
            clauses.append("status = ?")
            params.append(status)

        where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        query = f"SELECT COUNT(*) as total FROM students {where_sql};"
        row = self.fetch_one(query, tuple(params))
        return row["total"] if row else 0

    def get_departments(self) -> List[str]:
        """Get unique departments from existing student records."""
        rows = self.fetch_all("SELECT DISTINCT department FROM students ORDER BY department ASC;")
        return [row["department"] for row in rows]

    def get_academic_years(self) -> List[str]:
        """Get unique academic years from existing student records."""
        rows = self.fetch_all("SELECT DISTINCT academic_year FROM students ORDER BY academic_year DESC;")
        return [row["academic_year"] for row in rows]
