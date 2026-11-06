"""
student_profiles.py - Interactive Student Directory & Individual Profiles for MARKNOVA.
Provides a responsive roll-sorted grid, real-time search, white cards with subtle shadows,
and a bulletproof analytical profile view without HTML code block rendering bugs.
"""

import streamlit as st
import pandas as pd
from typing import Optional, Dict, Any
from analysis import get_student_profile
from charts import create_student_comparison_radar_chart
from styles import render_kpi, render_progress_bar, clean_html, render_html
from report_generator import generate_individual_student_pdf

def render_student_directory(df: pd.DataFrame):
    """
    Renders the student directory sorted strictly by Roll Number.
    Includes instant search by roll or name, and responsive white SaaS cards.
    """
    header_html = """<div style="margin-bottom: 20px;">
<h2 style="margin: 0; font-size: 1.85rem; font-weight: 800; color: #14213D; letter-spacing: 0.3px;">
Student Directory
</h2>
<p style="margin: 4px 0 0 0; color: #64748B; font-size: 0.92rem;">
Complete directory of enrolled students arranged by roll number. Select any student to view their analytical profile.
</p>
</div>"""
    render_html(header_html)

    if df.empty:
        st.info("No student records available. Please upload a marksheet PDF.")
        return

    # Ensure strictly sorted by roll_no
    sorted_df = df.sort_values(by="roll_no").reset_index(drop=True)

    # Search Bar
    search_col, count_col = st.columns([3, 1])
    with search_col:
        search_query = st.text_input(
            "Search Directory",
            placeholder="🔍 Search by Roll Number or Student Name...",
            label_visibility="collapsed"
        ).strip().lower()

    filtered_df = sorted_df
    if search_query:
        filtered_df = sorted_df[
            sorted_df["roll_no"].str.lower().str.contains(search_query) |
            sorted_df["name"].str.lower().str.contains(search_query)
        ]

    with count_col:
        count_html = f"""<div style="padding-top: 8px; text-align: right; color: #2563EB; font-weight: 700; font-size: 0.9rem;">
Showing {len(filtered_df)} of {len(sorted_df)} Students
</div>"""
        render_html(count_html)

    if filtered_df.empty:
        st.warning("No students matched your search query.")
        return

    # Render cards in a 4-column responsive grid
    cols_per_row = 4
    rows = [filtered_df.iloc[i:i+cols_per_row] for i in range(0, len(filtered_df), cols_per_row)]

    for row_chunk in rows:
        grid_cols = st.columns(cols_per_row)
        for idx, (_, student) in enumerate(row_chunk.iterrows()):
            roll = student["roll_no"]
            name = student["name"]
            with grid_cols[idx]:
                card_html = f"""<div class="student-card">
<div>
<div class="student-roll">{roll}</div>
<div class="student-name" title="{name}">{name}</div>
</div>
<div class="student-indicator">
<span>Open Profile</span> <span>→</span>
</div>
</div>"""
                render_html(card_html)
                if st.button("View Profile", key=f"btn_card_{roll}", use_container_width=True):
                    st.session_state["selected_student_roll"] = roll
                    st.rerun()

def render_subject_card(sub: Dict[str, Any]) -> str:
    """Renders a single subject performance card as clean, unindented HTML."""
    sub_name = sub["name"]
    code = sub["code"]
    mark = sub["marks"]
    max_m = int(sub["max_marks"])
    pct = sub["percentage"]
    status = sub["status"]
    class_avg = sub["class_avg"]
    
    # Status chip
    status_chip = ""
    if status == "AB":
        status_chip = '<span class="chip chip-warning">ABSENT</span>'
    elif status == "BLANK":
        status_chip = '<span class="chip chip-warning">BLANK</span>'
        
    diff = round(mark - class_avg, 1)
    diff_sign = "+" if diff >= 0 else ""
    comp_text = f"Above Average ({diff_sign}{diff})" if diff >= 0 else f"Below Average ({diff_sign}{diff})"
    comp_color = "#15803D" if diff >= 0 else "#DC2626"
    
    prog_bar = render_progress_bar(pct)
    
    card_html = f"""<div class="subject-card">
<div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:6px;">
<div>
<div style="display:flex; align-items:center; gap:8px;">
<span style="font-family:'JetBrains Mono', monospace; font-weight:700; color:#2563EB; font-size:1.02rem;">{code}</span>
{status_chip}
</div>
<div style="font-size:0.86rem; color:#1E3A5F; font-weight:500; margin-top:3px; line-height:1.35;">{sub_name}</div>
</div>
<div style="text-align:right; min-width:85px; margin-left:12px;">
<span style="font-size:1.45rem; font-weight:800; color:#14213D;">{mark}</span>
<span style="font-size:0.9rem; color:#64748B;">/{max_m}</span>
<div style="font-size:0.85rem; color:#2563EB; font-weight:700; margin-top:1px;">{pct}%</div>
</div>
</div>
{prog_bar}
<div style="display:flex; justify-content:space-between; align-items:center; margin-top:6px; font-size:0.78rem;">
<span style="color:#64748B;">Class Average: <strong style="color:#14213D;">{class_avg} / {max_m}</strong></span>
<span style="color:#64748B;">Performance: <strong style="color:{comp_color};">{comp_text}</strong></span>
</div>
</div>"""
    return clean_html(card_html)

def render_individual_profile(df: pd.DataFrame, roll_no: str):
    """
    Renders the detailed analytical profile for a single student.
    Includes competition rank, total marks, percentage, visual subject cards,
    comparison with class average, strongest/weakest subject, and report download.
    """
    profile = get_student_profile(df, roll_no)
    if not profile:
        st.error(f"Student record for roll number {roll_no} not found.")
        if st.button("← Back to Directory"):
            st.session_state["selected_student_roll"] = None
            st.rerun()
        return

    # Navigation bar: Back, Previous, Next, Download
    sorted_rolls = list(df.sort_values(by="roll_no")["roll_no"])
    current_idx = sorted_rolls.index(roll_no) if roll_no in sorted_rolls else 0
    prev_roll = sorted_rolls[current_idx - 1] if current_idx > 0 else None
    next_roll = sorted_rolls[current_idx + 1] if current_idx < len(sorted_rolls) - 1 else None

    nav_c1, nav_c2, nav_c3, nav_c4 = st.columns([2, 1, 1, 2])
    with nav_c1:
        if st.button("← Back to Student Directory", key="btn_back_dir"):
            st.session_state["selected_student_roll"] = None
            st.rerun()
            
    with nav_c2:
        if prev_roll:
            if st.button(f"← Prev ({prev_roll})", key="btn_prev_student"):
                st.session_state["selected_student_roll"] = prev_roll
                st.rerun()
                
    with nav_c3:
        if next_roll:
            if st.button(f"Next ({next_roll}) →", key="btn_next_student"):
                st.session_state["selected_student_roll"] = next_roll
                st.rerun()

    with nav_c4:
        # PDF Report download button
        pdf_bytes = generate_individual_student_pdf(profile)
        st.download_button(
            label="📥 Download Student PDF",
            data=pdf_bytes,
            file_name=f"Report_{profile['roll_no']}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    render_html("<hr style='border: none; border-top: 1px solid #E2E8F0; margin: 16px 0 24px 0;' />")

    # Student Header Banner
    diff_sign = "+" if profile["pct_diff"] >= 0 else ""
    diff_color = "#15803D" if profile["pct_diff"] >= 0 else "#DC2626"
    
    banner_html = f"""<div class="glass-card" style="border-color: #BFDBFE; padding: 22px 26px; background: linear-gradient(135deg, #FFFFFF 0%, #F0F7FF 100%);">
<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
<div>
<div style="font-family: 'JetBrains Mono', monospace; color: #2563EB; font-size: 1.05rem; font-weight: 700; letter-spacing: 0.5px;">
{profile['roll_no']}
</div>
<h1 style="margin: 4px 0 6px 0; font-size: 2.1rem; font-weight: 800; color: #14213D; letter-spacing: 0.3px;">
{profile['name']}
</h1>
<div style="color: #64748B; font-size: 0.88rem;">
College of Engineering Chengannur • EEE • Semester 1
</div>
</div>
<div style="display: flex; gap: 12px; align-items: center;">
<div style="background: #F3E8FF; border: 1px solid #DDD6FE; border-radius: 12px; padding: 10px 20px; text-align: center;">
<div style="font-size: 0.72rem; text-transform: uppercase; color: #7C3AED; font-weight: 700; letter-spacing: 1px;">Class Rank</div>
<div style="font-size: 1.9rem; font-weight: 800; color: #5B21B6; font-family: 'Outfit', sans-serif;">#{profile['rank']}</div>
</div>
</div>
</div>
</div>"""
    render_html(banner_html)

    # KPI Summary Cards
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_html(render_kpi("Overall Score", f"{profile['total']}/200", f"Max Marks: 200", "#E2E8F0"))
    with k2:
        render_html(render_kpi("Overall Percentage", f"{profile['percentage']}%", "Performance Score", "#E2E8F0", is_gradient=True))
    with k3:
        render_html(render_kpi("Class Average", f"{profile['class_avg_pct']}%", f"Difference: <span style='color:{diff_color}; font-weight:700;'>{diff_sign}{profile['pct_diff']}%</span>", "#E2E8F0"))
    with k4:
        render_html(render_kpi("Strongest Subject", f"{profile['strongest_subject']['code']}", f"{profile['strongest_subject']['percentage']}% ({profile['strongest_subject']['marks']}/40)", "#E2E8F0"))

    # Subject-wise Breakdown + Radar Chart Comparison
    left_col, right_col = st.columns([1.15, 0.85], gap="large")

    with left_col:
        render_html("""<div style="margin-bottom: 12px;">
<h3 style="margin: 0; font-size: 1.25rem; font-weight: 800; color: #14213D;">
Subject-Wise Performance
</h3>
</div>""")

        for sub in profile["subjects"]:
            card_code = render_subject_card(sub)
            render_html(card_code)

    with right_col:
        render_html("""<div style="margin-bottom: 12px;">
<h3 style="margin: 0; font-size: 1.25rem; font-weight: 800; color: #14213D;">
Benchmark Comparison
</h3>
</div>""")
        
        # Plotly radar chart (rendered inside container without overflow)
        radar_fig = create_student_comparison_radar_chart(profile)
        st.plotly_chart(radar_fig, use_container_width=True, config={"displayModeBar": False})

        # Highlight Analysis Box
        insights_html = f"""<div class="glass-card" style="border-color: #E2E8F0; padding: 18px 20px; background: #F8FAFC; margin-top: 10px;">
<div style="font-size: 0.78rem; text-transform: uppercase; color: #49352A; font-weight: 800; letter-spacing: 1px; margin-bottom: 10px;">
Analytical Insights
</div>
<div style="margin-bottom: 8px; font-size: 0.88rem; color: #1E3A5F; line-height: 1.45;">
• <strong>Strongest Discipline:</strong> <span style="color:#2563EB; font-weight:700;">{profile['strongest_subject']['name']}</span> ({profile['strongest_subject']['marks']}/40 marks, {profile['strongest_subject']['percentage']}%).
</div>
<div style="margin-bottom: 8px; font-size: 0.88rem; color: #1E3A5F; line-height: 1.45;">
• <strong>Focus Discipline:</strong> <span style="color:#D97706; font-weight:700;">{profile['weakest_subject']['name']}</span> ({profile['weakest_subject']['marks']}/40 marks, {profile['weakest_subject']['percentage']}%).
</div>
<div style="font-size: 0.88rem; color: #1E3A5F; line-height: 1.45;">
• <strong>Class Position:</strong> Scoring <span style="color:{diff_color}; font-weight:800;">{abs(profile['pct_diff'])}% {'higher than' if profile['pct_diff']>=0 else 'lower than'}</span> the overall semester cohort average.
</div>
</div>"""
        render_html(insights_html)
