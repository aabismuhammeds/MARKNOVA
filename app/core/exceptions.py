"""Custom exceptions for Student Marks Management System."""
from __future__ import annotations


class AppException(Exception):
    """Base exception for application errors."""
    pass


class DatabaseError(AppException):
    """Base exception for database errors."""
    pass


class RecordNotFoundError(DatabaseError):
    """Raised when a requested record does not exist in the database."""
    pass


class DuplicateRecordError(DatabaseError):
    """Raised when attempting to insert a record violating unique constraints."""
    pass


class ForeignKeyViolationError(DatabaseError):
    """Raised when a foreign key constraint fails."""
    pass


class ValidationError(AppException):
    """Raised when input validation fails."""
    pass
