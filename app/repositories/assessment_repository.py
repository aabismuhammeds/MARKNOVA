"""Repository for Assessment entities."""
from __future__ import annotations

from typing import List, Optional
import sqlite3

from app.core.exceptions import RecordNotFoundError
from app.models.assessment import Assessment
from app.repositories.base_repository import BaseRepository


class AssessmentRepository(BaseRepository):
    """Data access repository for course evaluation assessments."""

    def _row_to_assessment(self, row: sqlite3.Row) -> Assessment:
        keys = row.keys()
        return Assessment(
            assessment_id=row["assessment_id"],
            course_code=row["course_code"],
            name=row["name"],
            max_marks=float(row["max_marks"]),
            weightage_percent=float(row["weightage_percent"]),
            academic_year=row["academic_year"],
            semester=int(row["semester"]),
            created_at=row["created_at"],
            course_name=row["course_name"] if "course_name" in keys else None,
        )

    def add(self, assessment: Assessment) -> Assessment:
        """Insert a new assessment component."""
        query = """
            INSERT INTO assessments (
                course_code, name, max_marks, weightage_percent, academic_year, semester
            ) VALUES (?, ?, ?, ?, ?, ?);
        """
        with self.db.get_connection() as conn:
            cursor = conn.execute(
                query,
                (
                    assessment.course_code,
                    assessment.name,
                    assessment.max_marks,
                    assessment.weightage_percent,
                    assessment.academic_year,
                    assessment.semester,
                ),
            )
            assessment.assessment_id = cursor.lastrowid
        return assessment

    def update(self, assessment: Assessment) -> Assessment:
        """Update an assessment component."""
        if assessment.assessment_id is None:
            raise ValueError("Cannot update assessment without assessment_id.")
        query = """
            UPDATE assessments SET
                name = ?,
                max_marks = ?,
                weightage_percent = ?,
                academic_year = ?,
                semester = ?
            WHERE assessment_id = ?;
        """
        with self.db.get_connection() as conn:
            cursor = conn.execute(
                query,
                (
                    assessment.name,
                    assessment.max_marks,
                    assessment.weightage_percent,
                    assessment.academic_year,
                    assessment.semester,
                    assessment.assessment_id,
                ),
            )
            if cursor.rowcount == 0:
                raise RecordNotFoundError(f"Assessment with ID {assessment.assessment_id} not found.")
        return assessment

    def delete(self, assessment_id: int) -> bool:
        """Delete an assessment. Cascades to student marks."""
        with self.db.get_connection() as conn:
            cursor = conn.execute("DELETE FROM assessments WHERE assessment_id = ?;", (assessment_id,))
            if cursor.rowcount == 0:
                raise RecordNotFoundError(f"Assessment with ID {assessment_id} not found.")
            return True

    def get_by_id(self, assessment_id: int) -> Optional[Assessment]:
        """Retrieve assessment by ID."""
        query = """
            SELECT a.*, c.course_name
            FROM assessments a
            JOIN courses c ON a.course_code = c.course_code
            WHERE a.assessment_id = ?;
        """
        row = self.fetch_one(query, (assessment_id,))
        return self._row_to_assessment(row) if row else None

    def list_by_course(
        self,
        course_code: str,
        academic_year: Optional[str] = None,
        semester: Optional[int] = None,
    ) -> List[Assessment]:
        """List all assessments for a specific course, optionally filtered by term."""
        clauses = ["a.course_code = ?"]
        params: List[object] = [course_code]

        if academic_year:
            clauses.append("a.academic_year = ?")
            params.append(academic_year)
        if semester is not None:
            clauses.append("a.semester = ?")
            params.append(semester)

        where_sql = f"WHERE {' AND '.join(clauses)}"
        query = f"""
            SELECT a.*, c.course_name
            FROM assessments a
            JOIN courses c ON a.course_code = c.course_code
            {where_sql}
            ORDER BY a.assessment_id ASC;
        """
        rows = self.fetch_all(query, tuple(params))
        return [self._row_to_assessment(row) for row in rows]

    def get_total_weightage(
        self, course_code: str, academic_year: str, semester: int
    ) -> float:
        """Calculate total configured weightage percent for a course offering."""
        query = """
            SELECT SUM(weightage_percent) as total_weight
            FROM assessments
            WHERE course_code = ? AND academic_year = ? AND semester = ?;
        """
        row = self.fetch_one(query, (course_code, academic_year, semester))
        return float(row["total_weight"]) if row and row["total_weight"] is not None else 0.0
