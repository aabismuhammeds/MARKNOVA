"""
analysis.py - Analytical Engine for MARKNOVA Academic Performance Dashboard.
Performs dynamic calculations for class averages, overall toppers, subject toppers,
ties detection, student percentiles, and competition rankings.
"""

import pandas as pd
from typing import Dict, List, Any, Optional
from pdf_processor import SUBJECT_DEFINITIONS

def get_class_overview_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculates overall class key performance indicators."""
    if df.empty:
        return {
            "total_students": 0,
            "class_avg_pct": 0.0,
            "highest_pct": 0.0,
            "lowest_pct": 0.0,
            "num_subjects": 5
        }
    
    return {
        "total_students": len(df),
        "class_avg_pct": round(df["percentage"].mean(), 2),
        "highest_pct": round(df["percentage"].max(), 2),
        "lowest_pct": round(df["percentage"].min(), 2),
        "num_subjects": len(SUBJECT_DEFINITIONS)
    }

def get_overall_class_toppers(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Returns the overall class topper(s). If there is a tie, returns all tied students.
    Strictly excludes Top 2, Top 3, or Top 10 rankings.
    """
    if df.empty:
        return []
    
    max_pct = df["percentage"].max()
    topper_rows = df[df["percentage"] == max_pct]
    
    toppers = []
    for _, row in topper_rows.iterrows():
        toppers.append({
            "roll_no": row["roll_no"],
            "name": row["name"],
            "total": row["total"],
            "percentage": row["percentage"],
            "subject_marks": {
                sub["code"]: row[sub["code"]] for sub in SUBJECT_DEFINITIONS
            }
        })
    return toppers

def get_subject_analysis(df: pd.DataFrame, subject_code: str) -> Optional[Dict[str, Any]]:
    """
    Calculates detailed metrics for a specific subject, including tie-aware toppers.
    """
    if df.empty or subject_code not in df.columns:
        return None
    
    sub_def = next((s for s in SUBJECT_DEFINITIONS if s["code"] == subject_code), None)
    if not sub_def:
        return None
        
    status_col = f"status_{subject_code}"
    
    # Valid students: students who were present and not blank
    if status_col in df.columns:
        valid_df = df[df[status_col] == "PRESENT"]
    else:
        valid_df = df
        
    num_valid = len(valid_df)
    max_marks = sub_def["max_marks"]
    
    # Marks calculations (averages across total class records with 0 for absent, and valid appeared)
    avg_marks = round(df[subject_code].mean(), 2)
    avg_pct = round((avg_marks / max_marks) * 100.0, 2)
    
    highest_marks = df[subject_code].max()
    lowest_marks = df[subject_code].min()
    
    # Subject Toppers (supports ties)
    toppers_df = df[df[subject_code] == highest_marks]
    subject_toppers = []
    for _, row in toppers_df.iterrows():
        subject_toppers.append({
            "name": row["name"],
            "roll_no": row["roll_no"],
            "marks": row[subject_code],
            "percentage": round((row[subject_code] / max_marks) * 100.0, 2)
        })
        
    return {
        "code": subject_code,
        "name": sub_def["name"],
        "max_marks": max_marks,
        "class_avg_marks": avg_marks,
        "class_avg_pct": avg_pct,
        "highest_marks": highest_marks,
        "lowest_marks": lowest_marks,
        "num_valid": num_valid,
        "toppers": subject_toppers
    }

def get_all_subject_analyses(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Returns analysis for all 5 subjects."""
    analyses = []
    for sub in SUBJECT_DEFINITIONS:
        analysis = get_subject_analysis(df, sub["code"])
        if analysis:
            analyses.append(analysis)
    return analyses

def get_student_profile(df: pd.DataFrame, roll_no: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves and calculates all individual metrics for a student by roll number.
    Includes competition rank, subject breakdowns, strengths, weaknesses, and class delta.
    """
    if df.empty:
        return None
        
    student_rows = df[df["roll_no"] == roll_no]
    if student_rows.empty:
        return None
        
    row = student_rows.iloc[0]
    class_avg_pct = round(df["percentage"].mean(), 2)
    pct_diff = round(row["percentage"] - class_avg_pct, 2)
    
    # Subject wise performance breakdown
    subject_details = []
    for sub in SUBJECT_DEFINITIONS:
        code = sub["code"]
        mark = row[code]
        max_m = sub["max_marks"]
        pct = round((mark / max_m) * 100.0, 2)
        status = row.get(f"status_{code}", "PRESENT")
        
        # Calculate subject class average for comparison
        sub_avg = round(df[code].mean(), 2)
        
        subject_details.append({
            "code": code,
            "name": sub["name"],
            "marks": mark,
            "max_marks": max_m,
            "percentage": pct,
            "status": status,
            "class_avg": sub_avg
        })
        
    # Identify strongest and weakest subject based on percentage
    sorted_by_pct = sorted(subject_details, key=lambda s: s["percentage"], reverse=True)
    strongest = sorted_by_pct[0]
    weakest = sorted_by_pct[-1]
    
    return {
        "roll_no": row["roll_no"],
        "name": row["name"],
        "rank": int(row["rank"]),
        "total": row["total"],
        "max_total": 200.0,
        "percentage": row["percentage"],
        "class_avg_pct": class_avg_pct,
        "pct_diff": pct_diff,
        "strongest_subject": strongest,
        "weakest_subject": weakest,
        "subjects": subject_details
    }
