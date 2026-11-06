"""Unit tests for ConfigRepository."""
from __future__ import annotations

import unittest
from app.core.database import DatabaseManager
from app.models.grading_scale import GradingScale
from app.repositories.config_repository import ConfigRepository


class TestConfigRepository(unittest.TestCase):
    """Test configuration repository for grading scales and settings."""

    def setUp(self):
        """Initialize in-memory database and repository."""
        self.db = DatabaseManager(":memory:")
        self.db.initialize_database()
        self.repo = ConfigRepository(self.db)

    def test_system_settings_crud(self):
        """Test setting and getting application key-value pairs."""
        # Non-existent key with default
        val = self.repo.get_setting("non_existent", default="default_val")
        self.assertEqual(val, "default_val")

        # Set and get
        self.repo.set_setting("institution_name", "Metropolis University")
        self.assertEqual(self.repo.get_setting("institution_name"), "Metropolis University")

        # Update existing
        self.repo.set_setting("institution_name", "Gotham Academy")
        self.assertEqual(self.repo.get_setting("institution_name"), "Gotham Academy")

    def test_grading_scales_setup(self):
        """Test setting and retrieving custom grading scales."""
        scales = [
            GradingScale("A+", 90.0, 100.0, 4.0, "Outstanding"),
            GradingScale("A", 80.0, 89.99, 3.7, "Excellent"),
            GradingScale("B", 70.0, 79.99, 3.0, "Good"),
            GradingScale("F", 0.0, 69.99, 0.0, "Fail"),
        ]
        self.repo.set_grading_scales(scales)

        retrieved = self.repo.get_grading_scales()
        self.assertEqual(len(retrieved), 4)
        self.assertEqual(retrieved[0].letter_grade, "A+")
        self.assertEqual(retrieved[0].gpa_point, 4.0)
        self.assertEqual(retrieved[3].letter_grade, "F")


if __name__ == "__main__":
    unittest.main()
