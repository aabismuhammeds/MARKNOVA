"""Repository for StudentMark entities."""
from __future__ import annotations

from typing import List, Optional
import sqlite3

from app.core.exceptions import RecordNotFoundError
from app.models.mark import StudentMark
from app.repositories.base_repository import BaseRepository


class MarksRepository(BaseRepository):
    """Data access repository for student marks and grades."""

    def _row_to_mark(self, row: sqlite3.Row) -> StudentMark:
        keys = row.keys()
        return StudentMark(
            mark_id=row["mark_id"],
            student_id=row["student_id"],
            assessment_id=row["assessment_id"],
            marks_obtained=float(row["marks_obtained"]) if row["marks_obtained"] is not None else None,
            is_absent=bool(row["is_absent"]),
            remarks=row["remarks"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            student_name=f"{row['first_name']} {row['last_name']}".strip() if "first_name" in keys and "last_name" in keys else None,
            course_code=row["course_code"] if "course_code" in keys else None,
            course_name=row["course_name"] if "course_name" in keys else None,
            assessment_name=row["assessment_name"] if "assessment_name" in keys else None,
            max_marks=float(row["max_marks"]) if "max_marks" in keys and row["max_marks"] is not None else None,
            weightage_percent=float(row["weightage_percent"]) if "weightage_percent" in keys and row["weightage_percent"] is not None else None,
        )

    def upsert(self, mark: StudentMark) -> StudentMark:
        """Insert or update a student mark atomically using ON CONFLICT."""
        query = """
            INSERT INTO student_marks (student_id, assessment_id, marks_obtained, is_absent, remarks)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(student_id, assessment_id) DO UPDATE SET
                marks_obtained = excluded.marks_obtained,
                is_absent = excluded.is_absent,
                remarks = excluded.remarks,
                updated_at = CURRENT_TIMESTAMP;
        """
        with self.db.get_connection() as conn:
            conn.execute(
                query,
                (
                    mark.student_id,
                    mark.assessment_id,
                    mark.marks_obtained,
                    1 if mark.is_absent else 0,
                    mark.remarks,
                ),
            )
        return self.get_by_student_and_assessment(mark.student_id, mark.assessment_id) or mark

    def save_bulk(self, marks: List[StudentMark]) -> int:
        """Upsert a batch of marks inside a single transaction."""
        if not marks:
            return 0
        query = """
            INSERT INTO student_marks (student_id, assessment_id, marks_obtained, is_absent, remarks)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(student_id, assessment_id) DO UPDATE SET
                marks_obtained = excluded.marks_obtained,
                is_absent = excluded.is_absent,
                remarks = excluded.remarks,
                updated_at = CURRENT_TIMESTAMP;
        """
        data = [
            (
                m.student_id,
                m.assessment_id,
                m.marks_obtained,
                1 if m.is_absent else 0,
                m.remarks,
            )
            for m in marks
        ]
        with self.db.get_connection() as conn:
            cursor = conn.executemany(query, data)
            return cursor.rowcount

    def get_by_student_and_assessment(
        self, student_id: str, assessment_id: int
    ) -> Optional[StudentMark]:
        """Fetch a specific mark entry by student and assessment IDs."""
        query = """
            SELECT 
                sm.*, 
                s.first_name, s.last_name, 
                a.name as assessment_name, a.max_marks, a.weightage_percent, a.course_code,
                c.course_name
            FROM student_marks sm
            JOIN students s ON sm.student_id = s.student_id
            JOIN assessments a ON sm.assessment_id = a.assessment_id
            JOIN courses c ON a.course_code = c.course_code
            WHERE sm.student_id = ? AND sm.assessment_id = ?;
        """
        row = self.fetch_one(query, (student_id, assessment_id))
        return self._row_to_mark(row) if row else None

    def get_marks_for_assessment(self, assessment_id: int) -> List[StudentMark]:
        """Get all marks submitted for a particular assessment."""
        query = """
            SELECT 
                sm.*, 
                s.first_name, s.last_name, 
                a.name as assessment_name, a.max_marks, a.weightage_percent, a.course_code,
                c.course_name
            FROM student_marks sm
            JOIN students s ON sm.student_id = s.student_id
            JOIN assessments a ON sm.assessment_id = a.assessment_id
            JOIN courses c ON a.course_code = c.course_code
            WHERE sm.assessment_id = ?
            ORDER BY s.student_id ASC;
        """
        rows = self.fetch_all(query, (assessment_id,))
        return [self._row_to_mark(row) for row in rows]

    def get_marks_for_course_and_student(
        self, student_id: str, course_code: str, academic_year: str, semester: int
    ) -> List[StudentMark]:
        """Get all assessment marks for a student in a specific course offering."""
        query = """
            SELECT 
                sm.*, 
                s.first_name, s.last_name, 
                a.name as assessment_name, a.max_marks, a.weightage_percent, a.course_code,
                c.course_name
            FROM assessments a
            JOIN courses c ON a.course_code = c.course_code
            LEFT JOIN student_marks sm ON a.assessment_id = sm.assessment_id AND sm.student_id = ?
            LEFT JOIN students s ON s.student_id = ?
            WHERE a.course_code = ? AND a.academic_year = ? AND a.semester = ?
            ORDER BY a.assessment_id ASC;
        """
        rows = self.fetch_all(query, (student_id, student_id, course_code, academic_year, semester))
        return [self._row_to_mark(row) for row in rows]

    def get_student_transcript_marks(
        self,
        student_id: str,
        academic_year: Optional[str] = None,
        semester: Optional[int] = None,
    ) -> List[StudentMark]:
        """Retrieve all graded marks for a student across all courses."""
        clauses = ["sm.student_id = ?"]
        params: List[object] = [student_id]

        if academic_year:
            clauses.append("a.academic_year = ?")
            params.append(academic_year)
        if semester is not None:
            clauses.append("a.semester = ?")
            params.append(semester)

        where_sql = f"WHERE {' AND '.join(clauses)}"
        query = f"""
            SELECT 
                sm.*, 
                s.first_name, s.last_name, 
                a.name as assessment_name, a.max_marks, a.weightage_percent, a.course_code,
                c.course_name
            FROM student_marks sm
            JOIN students s ON sm.student_id = s.student_id
            JOIN assessments a ON sm.assessment_id = a.assessment_id
            JOIN courses c ON a.course_code = c.course_code
            {where_sql}
            ORDER BY a.semester ASC, a.course_code ASC, a.assessment_id ASC;
        """
        rows = self.fetch_all(query, tuple(params))
        return [self._row_to_mark(row) for row in rows]

    def delete(self, mark_id: int) -> bool:
        """Delete a mark entry by mark_id."""
        with self.db.get_connection() as conn:
            cursor = conn.execute("DELETE FROM student_marks WHERE mark_id = ?;", (mark_id,))
            if cursor.rowcount == 0:
                raise RecordNotFoundError(f"Mark with ID {mark_id} not found.")
            return True
