"""Unit tests for AssessmentRepository and MarksRepository."""
from __future__ import annotations

import unittest
from app.core.database import DatabaseManager
from app.models.assessment import Assessment
from app.models.course import Course
from app.models.mark import StudentMark
from app.models.student import Student
from app.repositories.assessment_repository import AssessmentRepository
from app.repositories.course_repository import CourseRepository
from app.repositories.marks_repository import MarksRepository
from app.repositories.student_repository import StudentRepository


class TestMarksAndAssessments(unittest.TestCase):
    """Test assessment setup, weightages, mark upserts, and transcript retrieval."""

    def setUp(self):
        """Initialize in-memory database and repositories."""
        self.db = DatabaseManager(":memory:")
        self.db.initialize_database()

        self.student_repo = StudentRepository(self.db)
        self.course_repo = CourseRepository(self.db)
        self.assessment_repo = AssessmentRepository(self.db)
        self.marks_repo = MarksRepository(self.db)

        # Setup base student and course
        self.student_repo.add(
            Student("STU-001", "Ada", "Lovelace", "ada@test.org", "CS", 1, "2024-2025")
        )
        self.student_repo.add(
            Student("STU-002", "Charles", "Babbage", "charles@test.org", "CS", 1, "2024-2025")
        )
        self.course_repo.add(Course("CS101", "Programming I", "CS", 4.0, 1))

    def test_assessment_crud_and_weightage(self):
        """Test creating assessments and calculating total weightage."""
        a1 = Assessment(
            course_code="CS101",
            name="Midterm Exam",
            max_marks=100.0,
            weightage_percent=40.0,
            academic_year="2024-2025",
            semester=1,
        )
        a2 = Assessment(
            course_code="CS101",
            name="Final Exam",
            max_marks=100.0,
            weightage_percent=60.0,
            academic_year="2024-2025",
            semester=1,
        )
        saved_a1 = self.assessment_repo.add(a1)
        saved_a2 = self.assessment_repo.add(a2)

        self.assertIsNotNone(saved_a1.assessment_id)
        self.assertIsNotNone(saved_a2.assessment_id)

        # Total weightage check (40 + 60 = 100)
        total_weight = self.assessment_repo.get_total_weightage("CS101", "2024-2025", 1)
        self.assertEqual(total_weight, 100.0)

        # List by course
        assessments = self.assessment_repo.list_by_course("CS101", "2024-2025", 1)
        self.assertEqual(len(assessments), 2)
        self.assertEqual(assessments[0].name, "Midterm Exam")

    def test_marks_upsert_and_percentage_calculation(self):
        """Test inserting and updating marks atomically."""
        assessment = self.assessment_repo.add(
            Assessment("CS101", "Quiz 1", 50.0, 20.0, "2024-2025", 1)
        )
        as_id = assessment.assessment_id
        assert as_id is not None

        # 1. Insert initial mark: 45 out of 50
        mark1 = StudentMark(student_id="STU-001", assessment_id=as_id, marks_obtained=45.0)
        saved_mark = self.marks_repo.upsert(mark1)
        self.assertEqual(saved_mark.marks_obtained, 45.0)
        self.assertEqual(saved_mark.percentage, 90.0)

        # 2. Update mark (re-evaluating score to 48.0 and adding remark)
        mark1_updated = StudentMark(
            student_id="STU-001",
            assessment_id=as_id,
            marks_obtained=48.0,
            remarks="Re-evaluated question 3",
        )
        updated_mark = self.marks_repo.upsert(mark1_updated)
        self.assertEqual(updated_mark.marks_obtained, 48.0)
        self.assertEqual(updated_mark.percentage, 96.0)
        self.assertEqual(updated_mark.remarks, "Re-evaluated question 3")

        # Verify only 1 record exists
        all_marks = self.marks_repo.get_marks_for_assessment(as_id)
        self.assertEqual(len(all_marks), 1)

    def test_student_absence(self):
        """Test marking a student absent."""
        assessment = self.assessment_repo.add(
            Assessment("CS101", "Practical Lab", 100.0, 25.0, "2024-2025", 1)
        )
        as_id = assessment.assessment_id
        assert as_id is not None

        mark = StudentMark(
            student_id="STU-002",
            assessment_id=as_id,
            marks_obtained=None,
            is_absent=True,
            remarks="Medical leave",
        )
        saved = self.marks_repo.upsert(mark)
        self.assertTrue(saved.is_absent)
        self.assertEqual(saved.percentage, 0.0)

    def test_bulk_marks_save(self):
        """Test bulk upserting marks for multiple students."""
        assessment = self.assessment_repo.add(
            Assessment("CS101", "Midterm", 100.0, 40.0, "2024-2025", 1)
        )
        as_id = assessment.assessment_id
        assert as_id is not None

        marks = [
            StudentMark(student_id="STU-001", assessment_id=as_id, marks_obtained=92.0),
            StudentMark(student_id="STU-002", assessment_id=as_id, marks_obtained=84.5),
        ]
        count = self.marks_repo.save_bulk(marks)
        self.assertEqual(count, 2)

        results = self.marks_repo.get_marks_for_assessment(as_id)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].marks_obtained, 92.0)
        self.assertEqual(results[1].marks_obtained, 84.5)

    def test_student_transcript_marks(self):
        """Test retrieving all marks for a student across assessments."""
        a1 = self.assessment_repo.add(
            Assessment("CS101", "Assignment", 50.0, 20.0, "2024-2025", 1)
        )
        a2 = self.assessment_repo.add(
            Assessment("CS101", "Final Exam", 100.0, 80.0, "2024-2025", 1)
        )
        assert a1.assessment_id is not None
        assert a2.assessment_id is not None

        self.marks_repo.upsert(StudentMark("STU-001", a1.assessment_id, 48.0))
        self.marks_repo.upsert(StudentMark("STU-001", a2.assessment_id, 95.0))

        transcript = self.marks_repo.get_student_transcript_marks("STU-001")
        self.assertEqual(len(transcript), 2)
        self.assertEqual(transcript[0].assessment_name, "Assignment")
        self.assertEqual(transcript[1].assessment_name, "Final Exam")


if __name__ == "__main__":
    unittest.main()
