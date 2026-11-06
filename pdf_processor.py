"""
pdf_processor.py - Dynamic marksheet PDF parsing and extraction engine.
Uses PyMuPDF (fitz) to dynamically extract student records, assessment scores,
and metadata without hardcoding records.
"""

import fitz  # PyMuPDF
import re
from typing import Dict, List, Any, Tuple, Optional

# Static definitions for College of Engineering Chengannur Semester 1 EEE
SUBJECT_DEFINITIONS = [
    {
        "code": "GYMAT101",
        "name": "Mathematics for Electrical Science and Physical Science - 1",
        "assessments": ["A1"],
        "max_marks": 40.0
    },
    {
        "code": "UCEST105",
        "name": "Algorithmic Thinking with Python",
        "assessments": ["A2"],
        "max_marks": 40.0
    },
    {
        "code": "GXCYT122",
        "name": "Chemistry for Information Science and Electrical Science",
        "assessments": ["A3"],
        "max_marks": 40.0
    },
    {
        "code": "GMEST103",
        "name": "Engineering Graphics and Computer Aided Drawing",
        "assessments": ["A4"],
        "max_marks": 40.0
    },
    {
        "code": "GXEST104",
        "name": "Introduction to Electrical and Electronics Engineering",
        "assessments": ["A5", "A6"],
        "max_marks": 40.0
    }
]

ASSESSMENT_MAX = {
    "A1": 40.0,
    "A2": 40.0,
    "A3": 40.0,
    "A4": 40.0,
    "A5": 20.0,
    "A6": 20.0
}

# Coordinate bin ranges based on PDF geometry
COL_BINS = [
    ('roll_no', 30.0, 92.0),
    ('name', 92.0, 305.0),
    ('A1', 305.0, 385.0),
    ('A2', 385.0, 465.0),
    ('A3', 465.0, 545.0),
    ('A4', 545.0, 625.0),
    ('A5', 625.0, 665.0),
    ('A6', 665.0, 705.0),
    ('total_str', 705.0, 775.0),
    ('pct_str', 775.0, 835.0)
]

def extract_metadata(doc: fitz.Document) -> Dict[str, str]:
    """Extract college, department, semester, and academic year from document header."""
    metadata = {
        "college": "College of Engineering Chengannur",
        "department": "Electrical and Electronics Engineering",
        "branch": "B Tech in Electrical And Electronics Engg",
        "semester": "Semester 1",
        "academic_year": "2026-27"
    }
    
    if len(doc) == 0:
        return metadata

    text_page1 = doc[0].get_text("text")
    
    # Try regex matching from text
    sem_match = re.search(r"Semester:\s*(Semester\s*\d+[^\n]*)", text_page1, re.IGNORECASE)
    if sem_match:
        metadata["semester"] = sem_match.group(1).strip()

    year_match = re.search(r"Academic Year:\s*([\d\-]+)", text_page1, re.IGNORECASE)
    if year_match:
        metadata["academic_year"] = year_match.group(1).strip()

    branch_match = re.search(r"Branch:\s*([^\n]+)", text_page1, re.IGNORECASE)
    if branch_match:
        metadata["branch"] = branch_match.group(1).strip()

    return metadata

def parse_mark_value(val_str: str) -> Tuple[float, str, Optional[str]]:
    """
    Parses a string mark into (numeric_mark, status, raw_str).
    Status can be:
      - 'PRESENT': Valid numeric mark
      - 'AB': Explicit absent
      - 'BLANK': Missing / Blank entry
    """
    clean = val_str.strip().upper() if val_str else ""
    if clean == "AB":
        return 0.0, "AB", "AB"
    if not clean:
        return 0.0, "BLANK", ""
    
    try:
        num = float(clean)
        return num, "PRESENT", clean
    except ValueError:
        return 0.0, "INVALID", clean

def extract_marksheet_pdf(file_bytes_or_path: Any) -> Tuple[Dict[str, Any], List[Dict[str, Any]], List[str]]:
    """
    Extracts student records and validation details from PDF bytes or path.
    Returns:
      (metadata, student_records, warnings)
    """
    warnings: List[str] = []
    
    if isinstance(file_bytes_or_path, (str, bytes, bytearray)):
        if isinstance(file_bytes_or_path, str):
            doc = fitz.open(file_bytes_or_path)
        else:
            doc = fitz.open(stream=file_bytes_or_path, filetype="pdf")
    else:
        # Streamlit UploadedFile or file-like object
        content = file_bytes_or_path.read()
        doc = fitz.open(stream=content, filetype="pdf")

    metadata = extract_metadata(doc)
    student_records: List[Dict[str, Any]] = []
    seen_roll_numbers = set()
    completed_marksheet = False

    for page_idx in range(len(doc)):
        if completed_marksheet:
            break
            
        page = doc[page_idx]
        words = page.get_text("words")
        
        # Check if 'Class Average' row exists on this page (denotes end of student rows)
        avg_words = [w for w in words if "Average" in w[4] and w[0] < 200]
        avg_y = min([w[1] for w in avg_words]) if avg_words else 9999.0
        
        # Identify candidate roll numbers in the first column
        roll_words = [
            w for w in words
            if re.match(r"^[A-Z0-9]{5,10}$", w[4]) and w[0] < 95 and w[1] < avg_y
        ]
        
        # On page 1, ignore any table headers above y=215
        if page_idx == 0:
            roll_words = [w for w in roll_words if w[1] > 215]
            
        roll_words.sort(key=lambda w: w[1])

        for rw in roll_words:
            roll = rw[4]
            if roll in seen_roll_numbers:
                warnings.append(f"Duplicate roll number detected: {roll}")
                continue
            seen_roll_numbers.add(roll)
            
            y_center = (rw[1] + rw[3]) / 2.0
            row_words = [w for w in words if abs((w[1] + w[3]) / 2.0 - y_center) < 8.0]
            
            # Map words into columns
            raw_cols: Dict[str, str] = {}
            for col_name, x_min, x_max in COL_BINS:
                if col_name == "roll_no":
                    continue
                matching = [w for w in row_words if x_min <= (w[0] + w[2]) / 2.0 < x_max]
                matching.sort(key=lambda w: w[0])
                raw_cols[col_name] = " ".join(w[4] for w in matching).strip()

            name = raw_cols.get("name", "").strip()
            
            # Parse assessments A1 to A6
            assessment_data = {}
            statuses = {}
            raw_marks = {}
            
            has_blank = False
            has_absent = False
            
            for code in ["A1", "A2", "A3", "A4", "A5", "A6"]:
                raw_str = raw_cols.get(code, "")
                num, status, val_clean = parse_mark_value(raw_str)
                assessment_data[code] = num
                statuses[code] = status
                raw_marks[code] = val_clean
                
                # Check maximum bounds
                max_bound = ASSESSMENT_MAX[code]
                if num > max_bound:
                    warnings.append(f"Student {roll} exceeded max marks for {code}: {num} > {max_bound}")
                
                if status == "BLANK":
                    has_blank = True
                elif status == "AB":
                    has_absent = True

            # Calculate subjects
            # GYMAT101 = A1
            # UCEST105 = A2
            # GXCYT122 = A3
            # GMEST103 = A4
            # GXEST104 = A5 + A6
            gxest104_mark = assessment_data["A5"] + assessment_data["A6"]
            
            # Determine GXEST104 status
            if statuses["A5"] == "BLANK" and statuses["A6"] == "BLANK":
                gxest104_status = "BLANK"
            elif statuses["A5"] == "AB" and statuses["A6"] == "AB":
                gxest104_status = "AB"
            else:
                gxest104_status = "PRESENT"

            subject_marks = {
                "GYMAT101": assessment_data["A1"],
                "UCEST105": assessment_data["A2"],
                "GXCYT122": assessment_data["A3"],
                "GMEST103": assessment_data["A4"],
                "GXEST104": gxest104_mark
            }

            subject_statuses = {
                "GYMAT101": statuses["A1"],
                "UCEST105": statuses["A2"],
                "GXCYT122": statuses["A3"],
                "GMEST103": statuses["A4"],
                "GXEST104": gxest104_status
            }

            calculated_total = sum(subject_marks.values())
            calculated_pct = round((calculated_total / 200.0) * 100.0, 2)

            # Parse source total and pct if available
            source_total_str = raw_cols.get("total_str", "")
            source_pct_str = raw_cols.get("pct_str", "")
            
            source_total = None
            if "/" in source_total_str:
                try:
                    source_total = float(source_total_str.split("/")[0])
                except ValueError:
                    pass

            source_pct = None
            if source_pct_str:
                try:
                    source_pct = float(source_pct_str)
                except ValueError:
                    pass

            # Validate calculated vs source
            total_verified = True
            if source_total is not None and abs(calculated_total - source_total) > 0.05:
                warnings.append(f"Total mismatch for {roll} ({name}): calculated {calculated_total} vs source {source_total}")
                total_verified = False

            student_record = {
                "roll_no": roll,
                "name": name,
                "A1": assessment_data["A1"],
                "A2": assessment_data["A2"],
                "A3": assessment_data["A3"],
                "A4": assessment_data["A4"],
                "A5": assessment_data["A5"],
                "A6": assessment_data["A6"],
                "status_A1": statuses["A1"],
                "status_A2": statuses["A2"],
                "status_A3": statuses["A3"],
                "status_A4": statuses["A4"],
                "status_A5": statuses["A5"],
                "status_A6": statuses["A6"],
                "raw_A1": raw_marks["A1"],
                "raw_A2": raw_marks["A2"],
                "raw_A3": raw_marks["A3"],
                "raw_A4": raw_marks["A4"],
                "raw_A5": raw_marks["A5"],
                "raw_A6": raw_marks["A6"],
                "GYMAT101": subject_marks["GYMAT101"],
                "UCEST105": subject_marks["UCEST105"],
                "GXCYT122": subject_marks["GXCYT122"],
                "GMEST103": subject_marks["GMEST103"],
                "GXEST104": subject_marks["GXEST104"],
                "status_GYMAT101": subject_statuses["GYMAT101"],
                "status_UCEST105": subject_statuses["UCEST105"],
                "status_GXCYT122": subject_statuses["GXCYT122"],
                "status_GMEST103": subject_statuses["GMEST103"],
                "status_GXEST104": subject_statuses["GXEST104"],
                "total": calculated_total,
                "percentage": calculated_pct,
                "source_total": source_total,
                "source_pct": source_pct,
                "total_verified": total_verified,
                "has_blank": has_blank,
                "has_absent": has_absent
            }
            
            student_records.append(student_record)

        if avg_words:
            completed_marksheet = True

    return metadata, student_records, warnings
