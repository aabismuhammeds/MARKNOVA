"""Application configuration and constants."""
from __future__ import annotations
import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "academic.db"

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)

# App Metadata
APP_NAME = "Student Marks Management System"
APP_VERSION = "1.0.0"

# Database Configuration
SCHEMA_VERSION = 1
