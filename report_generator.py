"""
report_generator.py - PDF and CSV report generation engine for MARKNOVA.
Generates:
1. Complete Class Analysis PDF (Class summary, subject toppers, full student roster)
2. Student Marks CSV (Roll, Name, A1-A6, 5 Subjects, Total, %, Rank)
3. Individual Student Performance Report PDF
"""

import os
import io
import pandas as pd
from typing import Dict, List, Any
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, Image as RLImage
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from pdf_processor import SUBJECT_DEFINITIONS

def generate_student_marks_csv(df: pd.DataFrame) -> bytes:
    """Generates a comprehensive CSV containing assessment marks, subjects, totals, and ranks."""
    export_cols = [
        "roll_no", "name",
        "A1", "A2", "A3", "A4", "A5", "A6",
        "GYMAT101", "UCEST105", "GXCYT122", "GMEST103", "GXEST104",
        "total", "percentage", "rank"
    ]
    # Filter available cols
    available_cols = [c for c in export_cols if c in df.columns]
    out_df = df[available_cols].copy()
    
    # Rename for clean export
    rename_dict = {
        "roll_no": "Roll Number",
        "name": "Student Name",
        "A1": "A1 (GYMAT101)",
        "A2": "A2 (UCEST105)",
        "A3": "A3 (GXCYT122)",
        "A4": "A4 (GMEST103)",
        "A5": "A5 (Part 1)",
        "A6": "A6 (Part 2)",
        "GYMAT101": "GYMAT101 Marks",
        "UCEST105": "UCEST105 Marks",
        "GXCYT122": "GXCYT122 Marks",
        "GMEST103": "GMEST103 Marks",
        "GXEST104": "GXEST104 Marks",
        "total": "Total Marks (200)",
        "percentage": "Percentage (%)",
        "rank": "Class Rank"
    }
    out_df = out_df.rename(columns=rename_dict)
    
    csv_buffer = io.StringIO()
    out_df.to_csv(csv_buffer, index=False)
    return csv_buffer.getvalue().encode("utf-8")

def generate_class_analysis_pdf(df: pd.DataFrame, metadata: Dict[str, Any], class_overview: Dict[str, Any], subject_analyses: List[Dict[str, Any]], toppers: List[Dict[str, Any]]) -> bytes:
    """
    Generates a complete multi-page Class Analysis PDF report using ReportLab.
    Includes college metadata, overall class topper, subject toppers, and full tabular marksheet.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A'),
        alignment=TA_CENTER
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#475569'),
        alignment=TA_CENTER
    )
    
    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=12,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'TableBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#1E293B')
    )

    header_cell_style = ParagraphStyle(
        'HeaderCell',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white,
        alignment=TA_CENTER
    )

    elements = []

    # Official MARKNOVA Brand Logo Header
    logo_path = "assets/marknova_logo.png"
    if os.path.exists(logo_path):
        logo_img = RLImage(logo_path, width=150, height=50)
        logo_table = Table([[logo_img]], colWidths=[720])
        logo_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
        ]))
        elements.append(logo_table)
        elements.append(Spacer(1, 2))

    # Title Banner
    elements.append(Paragraph("ACADEMIC PERFORMANCE REPORT", title_style))
    elements.append(Spacer(1, 3))
    sub_text = (
        f"{metadata.get('college', 'College of Engineering Chengannur')} | "
        f"{metadata.get('department', 'Electrical & Electronics Engineering')} | "
        f"{metadata.get('semester', 'Semester 1')} ({metadata.get('academic_year', '2026-27')})"
    )
    elements.append(Paragraph(sub_text, subtitle_style))
    elements.append(Spacer(1, 10))

    # KPI Summary Table
    topper_str = ", ".join([f"{t['name']} ({t['roll_no']}) - {t['total']}/200 ({t['percentage']}%)" for t in toppers])
    kpi_data = [
        ["Total Students Enrolled", str(class_overview.get("total_students", 0)), "Class Average %", f"{class_overview.get('class_avg_pct', 0)}%"],
        ["Highest Percentage", f"{class_overview.get('highest_pct', 0)}%", "Lowest Percentage", f"{class_overview.get('lowest_pct', 0)}%"],
        ["Overall Class Topper", topper_str, "Subjects Assessed", str(len(SUBJECT_DEFINITIONS))]
    ]
    
    kpi_table = Table(kpi_data, colWidths=[140, 220, 140, 220])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1E293B')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(kpi_table)
    elements.append(Spacer(1, 14))

    # Subject Performance Summary
    elements.append(Paragraph("Subject Performance & Toppers Summary", h2_style))
    sub_summary_data = [
        [
            Paragraph("Subject Code", header_cell_style),
            Paragraph("Subject Name", header_cell_style),
            Paragraph("Max", header_cell_style),
            Paragraph("Avg Mark", header_cell_style),
            Paragraph("Avg %", header_cell_style),
            Paragraph("High", header_cell_style),
            Paragraph("Low", header_cell_style),
            Paragraph("Subject Topper(s)", header_cell_style)
        ]
    ]

    for sub in subject_analyses:
        toppers_list = ", ".join([f"{t['name']} ({t['marks']})" for t in sub.get("toppers", [])])
        sub_summary_data.append([
            Paragraph(sub["code"], body_style),
            Paragraph(sub["name"], body_style),
            str(int(sub["max_marks"])),
            str(sub["class_avg_marks"]),
            f"{sub['class_avg_pct']}%",
            str(sub["highest_marks"]),
            str(sub["lowest_marks"]),
            Paragraph(toppers_list, body_style)
        ])

    sub_table = Table(sub_summary_data, colWidths=[65, 230, 35, 50, 45, 40, 40, 215])
    sub_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('ALIGN', (2, 1), (6, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(sub_table)
    elements.append(Spacer(1, 16))

    # Complete Student-Wise Roster Table (Page Break before full table)
    elements.append(PageBreak())
    elements.append(Paragraph("Complete Student Roster & Assessment Breakdown", h2_style))
    
    roster_headers = [
        Paragraph("Roll No", header_cell_style),
        Paragraph("Student Name", header_cell_style),
        Paragraph("GYMAT101<br/>(40)", header_cell_style),
        Paragraph("UCEST105<br/>(40)", header_cell_style),
        Paragraph("GXCYT122<br/>(40)", header_cell_style),
        Paragraph("GMEST103<br/>(40)", header_cell_style),
        Paragraph("GXEST104<br/>(40)", header_cell_style),
        Paragraph("Total<br/>(200)", header_cell_style),
        Paragraph("Pct<br/>(%)", header_cell_style),
        Paragraph("Rank", header_cell_style)
    ]
    
    roster_data = [roster_headers]
    sorted_df = df.sort_values(by="roll_no").reset_index(drop=True)
    
    for _, row in sorted_df.iterrows():
        roster_data.append([
            Paragraph(row["roll_no"], body_style),
            Paragraph(row["name"], body_style),
            str(row["GYMAT101"]),
            str(row["UCEST105"]),
            str(row["GXCYT122"]),
            str(row["GMEST103"]),
            str(row["GXEST104"]),
            str(row["total"]),
            f"{row['percentage']}%",
            f"#{int(row['rank'])}"
        ])

    roster_table = Table(
        roster_data,
        colWidths=[65, 210, 60, 60, 60, 60, 60, 50, 45, 50],
        repeatRows=1
    )
    roster_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('ALIGN', (2, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('PADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(roster_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

def generate_individual_student_pdf(profile: Dict[str, Any]) -> bytes:
    """
    Generates a single-page individual student academic performance report using ReportLab.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'StudentDocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0F172A'),
        alignment=TA_CENTER
    )
    
    subtitle_style = ParagraphStyle(
        'StudentDocSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#64748B'),
        alignment=TA_CENTER
    )
    
    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=12,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'TableBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#1E293B')
    )

    header_cell_style = ParagraphStyle(
        'HeaderCell',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.white,
        alignment=TA_CENTER
    )

    elements = []

    # Official MARKNOVA Brand Logo Header
    logo_path = "assets/marknova_logo.png"
    if os.path.exists(logo_path):
        logo_img = RLImage(logo_path, width=144, height=48)
        logo_table = Table([[logo_img]], colWidths=[532])
        logo_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
        ]))
        elements.append(logo_table)
        elements.append(Spacer(1, 2))

    # Title & Header
    elements.append(Paragraph("INDIVIDUAL STUDENT PERFORMANCE REPORT", title_style))
    elements.append(Spacer(1, 3))
    elements.append(Paragraph("College of Engineering Chengannur | Electrical & Electronics Engineering | Semester 1", subtitle_style))
    elements.append(Spacer(1, 12))

    # Student Information Table
    info_data = [
        ["Student Name", profile["name"], "Roll Number", profile["roll_no"]],
        ["Class Rank", f"#{profile['rank']} (Competition Ranking)", "Overall Score", f"{profile['total']} / {profile['max_total']}"],
        ["Percentage", f"{profile['percentage']}%", "Cohort Average", f"{profile['class_avg_pct']}%"]
    ]
    info_table = Table(info_data, colWidths=[110, 155, 110, 155])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0, 0), (-1, -1), 7),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 16))

    # Subject Breakdown Table
    elements.append(Paragraph("Subject-Wise Academic Performance", h2_style))
    
    sub_headers = [
        Paragraph("Code", header_cell_style),
        Paragraph("Subject Name", header_cell_style),
        Paragraph("Obtained", header_cell_style),
        Paragraph("Max", header_cell_style),
        Paragraph("Percentage", header_cell_style),
        Paragraph("Class Avg", header_cell_style),
        Paragraph("Comparison", header_cell_style)
    ]
    
    sub_table_data = [sub_headers]
    for s in profile["subjects"]:
        comp_str = f"+{round(s['marks'] - s['class_avg'], 1)}" if s['marks'] >= s['class_avg'] else str(round(s['marks'] - s['class_avg'], 1))
        sub_table_data.append([
            Paragraph(s["code"], body_style),
            Paragraph(s["name"], body_style),
            str(s["marks"]),
            str(int(s["max_marks"])),
            f"{s['percentage']}%",
            str(s["class_avg"]),
            comp_str
        ])

    sub_table = Table(sub_table_data, colWidths=[65, 195, 55, 45, 55, 55, 60])
    sub_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('ALIGN', (2, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(sub_table)
    elements.append(Spacer(1, 16))

    # Highlights
    elements.append(Paragraph("Performance Summary & Insights", h2_style))
    diff_sign = "+" if profile["pct_diff"] >= 0 else ""
    summary_text = (
        f"• <b>Academic Standing:</b> Class Rank #{profile['rank']} with an overall aggregate score of {profile['total']}/200 ({profile['percentage']}%).<br/>"
        f"• <b>Cohort Comparison:</b> Student is scoring <b>{diff_sign}{profile['pct_diff']}%</b> relative to the overall class average ({profile['class_avg_pct']}%).<br/>"
        f"• <b>Strongest Subject:</b> {profile['strongest_subject']['name']} ({profile['strongest_subject']['code']}) with {profile['strongest_subject']['marks']}/40 marks ({profile['strongest_subject']['percentage']}%).<br/>"
        f"• <b>Focus Subject:</b> {profile['weakest_subject']['name']} ({profile['weakest_subject']['code']}) with {profile['weakest_subject']['marks']}/40 marks ({profile['weakest_subject']['percentage']}%)."
    )
    elements.append(Paragraph(summary_text, body_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
