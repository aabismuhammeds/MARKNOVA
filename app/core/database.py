"""Database manager and schema migration engine using SQLite."""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, List, Union, Callable

from app.config import DATABASE_PATH
from app.core.exceptions import (
    DatabaseError,
    DuplicateRecordError,
    ForeignKeyViolationError,
)

# Migration step definition
MigrationFunction = Callable[[sqlite3.Connection], None]


class DatabaseManager:
    """Manages SQLite database connections, schema creation, and migrations."""

    def __init__(self, db_path: Union[str, Path] = DATABASE_PATH):
        self.db_path = str(db_path)
        self._in_memory_conn: Optional[sqlite3.Connection] = None
        if self.db_path == ":memory:":
            self._in_memory_conn = sqlite3.connect(":memory:")
            self._in_memory_conn.row_factory = sqlite3.Row
            self._in_memory_conn.execute("PRAGMA foreign_keys = ON;")

    def close(self) -> None:
        """Close shared connection if using in-memory mode."""
        if self._in_memory_conn is not None:
            self._in_memory_conn.close()
            self._in_memory_conn = None

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Provide a transactional SQLite connection context with foreign keys enabled."""
        if self._in_memory_conn is not None:
            conn = self._in_memory_conn
            try:
                yield conn
                conn.commit()
            except sqlite3.IntegrityError as err:
                conn.rollback()
                err_msg = str(err).lower()
                if "foreign key" in err_msg:
                    raise ForeignKeyViolationError(f"Foreign key constraint failed: {err}") from err
                if "unique" in err_msg or "primary key" in err_msg:
                    raise DuplicateRecordError(f"Duplicate record constraint failed: {err}") from err
                raise DatabaseError(f"Integrity error: {err}") from err
            except sqlite3.Error as err:
                conn.rollback()
                raise DatabaseError(f"Database error: {err}") from err
            except Exception:
                conn.rollback()
                raise
            return

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        # Enforce foreign key constraints
        conn.execute("PRAGMA foreign_keys = ON;")
        
        # Enable WAL mode for better concurrency on persistent databases
        try:
            conn.execute("PRAGMA journal_mode = WAL;")
        except sqlite3.OperationalError:
            pass

        try:
            yield conn
            conn.commit()
        except sqlite3.IntegrityError as err:
            conn.rollback()
            err_msg = str(err).lower()
            if "foreign key" in err_msg:
                raise ForeignKeyViolationError(f"Foreign key constraint failed: {err}") from err
            if "unique" in err_msg or "primary key" in err_msg:
                raise DuplicateRecordError(f"Duplicate record constraint failed: {err}") from err
            raise DatabaseError(f"Integrity error: {err}") from err
        except sqlite3.Error as err:
            conn.rollback()
            raise DatabaseError(f"Database error: {err}") from err
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def initialize_database(self) -> None:
        """Initialize database tables and run all pending migrations."""
        with self.get_connection() as conn:
            # Create migrations tracking table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version INTEGER PRIMARY KEY,
                    description TEXT NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

        self.apply_migrations()

    def get_applied_migrations(self) -> List[int]:
        """Return list of versions that have already been applied."""
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT version FROM schema_migrations ORDER BY version ASC;")
            return [row["version"] for row in cursor.fetchall()]

    def apply_migrations(self) -> None:
        """Run all unapplied registered migrations in sequence."""
        applied = set(self.get_applied_migrations())
        migrations = self._get_registered_migrations()

        for version, description, migration_func in migrations:
            if version not in applied:
                with self.get_connection() as conn:
                    migration_func(conn)
                    conn.execute(
                        "INSERT INTO schema_migrations (version, description) VALUES (?, ?);",
                        (version, description),
                    )

    def _get_registered_migrations(self) -> List[tuple[int, str, MigrationFunction]]:
        """Return list of (version, description, migration_func) tuples."""
        return [
            (1, "Create initial relational schema", _migration_v1_initial_schema),
        ]


def _migration_v1_initial_schema(conn: sqlite3.Connection) -> None:
    """Migration V1: Create core tables, constraints, and indices."""
    
    # Students Table
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            date_of_birth TEXT,
            department TEXT NOT NULL,
            semester INTEGER NOT NULL CHECK (semester >= 1 AND semester <= 12),
            academic_year TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'graduated', 'suspended')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    # Courses Table
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS courses (
            course_code TEXT PRIMARY KEY,
            course_name TEXT NOT NULL,
            department TEXT NOT NULL,
            credits REAL NOT NULL CHECK (credits > 0),
            semester INTEGER NOT NULL CHECK (semester >= 1 AND semester <= 12),
            description TEXT,
            is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    # Course Enrollments (Junction Table)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS enrollments (
            enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL REFERENCES students(student_id) ON DELETE CASCADE ON UPDATE CASCADE,
            course_code TEXT NOT NULL REFERENCES courses(course_code) ON DELETE CASCADE ON UPDATE CASCADE,
            academic_year TEXT NOT NULL,
            semester INTEGER NOT NULL CHECK (semester >= 1 AND semester <= 12),
            status TEXT NOT NULL DEFAULT 'enrolled' CHECK (status IN ('enrolled', 'completed', 'dropped')),
            enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(student_id, course_code, academic_year, semester)
        );
        """
    )

    # Assessments Table (Evaluation components per course, e.g., Midterm, Final, Quiz)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS assessments (
            assessment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_code TEXT NOT NULL REFERENCES courses(course_code) ON DELETE CASCADE ON UPDATE CASCADE,
            name TEXT NOT NULL,
            max_marks REAL NOT NULL CHECK (max_marks > 0),
            weightage_percent REAL NOT NULL CHECK (weightage_percent >= 0 AND weightage_percent <= 100),
            academic_year TEXT NOT NULL,
            semester INTEGER NOT NULL CHECK (semester >= 1 AND semester <= 12),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(course_code, name, academic_year, semester)
        );
        """
    )

    # Student Marks Table
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS student_marks (
            mark_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL REFERENCES students(student_id) ON DELETE CASCADE ON UPDATE CASCADE,
            assessment_id INTEGER NOT NULL REFERENCES assessments(assessment_id) ON DELETE CASCADE ON UPDATE CASCADE,
            marks_obtained REAL CHECK (marks_obtained IS NULL OR marks_obtained >= 0),
            is_absent INTEGER NOT NULL DEFAULT 0 CHECK (is_absent IN (0, 1)),
            remarks TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(student_id, assessment_id)
        );
        """
    )

    # Grading Scales Table (Configurable boundaries and GPA points)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS grading_scales (
            scale_id INTEGER PRIMARY KEY AUTOINCREMENT,
            letter_grade TEXT NOT NULL UNIQUE,
            min_percentage REAL NOT NULL CHECK (min_percentage >= 0),
            max_percentage REAL NOT NULL CHECK (max_percentage <= 100 AND max_percentage >= min_percentage),
            gpa_point REAL NOT NULL CHECK (gpa_point >= 0),
            description TEXT
        );
        """
    )

    # System Settings Table
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS system_settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            category TEXT DEFAULT 'general',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    # Performance Indices
    conn.execute("CREATE INDEX IF NOT EXISTS idx_students_dept_sem ON students(department, semester);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_enrollments_student ON enrollments(student_id);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_enrollments_course ON enrollments(course_code);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_assessments_course ON assessments(course_code);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_marks_student ON student_marks(student_id);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_marks_assessment ON student_marks(assessment_id);")
