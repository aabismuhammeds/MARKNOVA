"""
data_manager.py - Data management, validation engine, and session caching for MARKNOVA.
Handles data integrity checks, roll sequence validation, and state persistence.
"""

import os
import pandas as pd
from typing import Dict, List, Any, Tuple
from pdf_processor import extract_marksheet_pdf, SUBJECT_DEFINITIONS

DEFAULT_PDF_PATH = "data/S1 F FIRST SERIES MARKS.pdf"

class DataValidationReport:
    """Encapsulates data validation results and integrity statistics."""
    def __init__(self):
        self.total_records = 0
        self.missing_rolls: List[str] = []
        self.duplicate_rolls: List[str] = []
        self.out_of_bound_marks: List[str] = []
        self.total_mismatches: List[str] = []
        self.students_with_absent: List[str] = []
        self.students_with_blank: List[str] = []
        self.all_totals_verified = True
        self.warnings: List[str] = []

    @property
    def is_valid(self) -> bool:
        return len(self.duplicate_rolls) == 0 and len(self.out_of_bound_marks) == 0 and len(self.total_mismatches) == 0

def validate_dataset(records: List[Dict[str, Any]], warnings_from_parser: List[str]) -> DataValidationReport:
    """Runs comprehensive data validation over the extracted student dataset."""
    report = DataValidationReport()
    report.total_records = len(records)
    report.warnings = list(warnings_from_parser)
    
    seen_rolls = set()
    roll_numbers = []

    for r in records:
        roll = r["roll_no"]
        roll_numbers.append(roll)
        
        # Duplicate detection
        if roll in seen_rolls:
            report.duplicate_rolls.append(roll)
        seen_rolls.add(roll)
        
        # Mismatch check
        if not r.get("total_verified", True):
            report.total_mismatches.append(f"{roll}: calc {r['total']} != src {r.get('source_total')}")
            report.all_totals_verified = False
            
        # Absence and blank checks
        if r.get("has_absent", False):
            report.students_with_absent.append(roll)
        if r.get("has_blank", False):
            report.students_with_blank.append(roll)

    # Check roll sequence (e.g. sequential alphanumeric roll numbers)
    if roll_numbers:
        prefix_matches = [r[:5] for r in roll_numbers if len(r) >= 5]
        if prefix_matches:
            common_prefix = max(set(prefix_matches), key=prefix_matches.count)
            # Find numbers
            extracted_indices = []
            for r in roll_numbers:
                if r.startswith(common_prefix):
                    suffix = r[len(common_prefix):]
                    if suffix.isdigit():
                        extracted_indices.append(int(suffix))
            
            if extracted_indices:
                min_idx = min(extracted_indices)
                max_idx = max(extracted_indices)
                # Check for gaps
                for idx in range(min_idx, max_idx + 1):
                    if idx not in extracted_indices:
                        missing_roll = f"{common_prefix}{idx:02d}"
                        report.missing_rolls.append(missing_roll)

    return report

def process_marksheet_file(file_obj_or_path: Any, filename: str = "Uploaded PDF") -> Tuple[pd.DataFrame, Dict[str, Any], DataValidationReport]:
    """
    Parses, validates, and transforms marksheet data into a clean Pandas DataFrame.
    """
    metadata, raw_records, warnings = extract_marksheet_pdf(file_obj_or_path)
    validation_report = validate_dataset(raw_records, warnings)
    
    df = pd.DataFrame(raw_records)
    
    if not df.empty:
        # Dynamically compute competition rank (1, 2, 2, 4) using min ranking on descending percentage
        df["rank"] = df["percentage"].rank(ascending=False, method="min").astype(int)
        # Always maintain primary sorting by roll_no
        df = df.sort_values(by="roll_no").reset_index(drop=True)
    
    metadata["filename"] = filename
    metadata["student_count"] = len(df)
    
    return df, metadata, validation_report

def get_initial_dataset() -> Tuple[pd.DataFrame, Dict[str, Any], DataValidationReport]:
    """Loads the pre-supplied marksheet if available in the data directory."""
    if os.path.exists(DEFAULT_PDF_PATH):
        return process_marksheet_file(DEFAULT_PDF_PATH, "S1 F FIRST SERIES MARKS.pdf")
    # Return empty structures if not present
    empty_df = pd.DataFrame()
    empty_meta = {
        "college": "College of Engineering Chengannur",
        "department": "Electrical and Electronics Engineering",
        "branch": "B Tech in Electrical And Electronics Engg",
        "semester": "Semester 1",
        "academic_year": "2026-27",
        "filename": "No PDF loaded",
        "student_count": 0
    }
    empty_report = DataValidationReport()
    return empty_df, empty_meta, empty_report
