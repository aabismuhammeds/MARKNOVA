"""
app.py - Main application file for MARKNOVA Academic Performance Dashboard.
Tagline: "Clarity in Every Score."
Theme: Premium Modern Light SaaS (White & Soft Off-White, Dark Navy/Brown Typography, Selective Blue-to-Red Gradient Text).
Developed for College of Engineering Chengannur, Electrical & Electronics Engineering, Semester 1.
"""

import os
import base64
import streamlit as st
import pandas as pd
from typing import Dict, Any, List

from styles import get_custom_css, render_kpi, render_progress_bar, render_html, clean_html
from data_manager import get_initial_dataset, process_marksheet_file, DEFAULT_PDF_PATH
from analysis import (
    get_class_overview_stats,
    get_overall_class_toppers,
    get_subject_analysis,
    get_all_subject_analyses,
    get_student_profile
)
from charts import (
    create_subject_average_pct_chart,
    create_subject_average_marks_chart,
    create_highest_vs_average_chart,
    create_student_comparison_radar_chart,
    create_topper_breakdown_chart
)
from student_profiles import render_student_directory, render_individual_profile
from report_generator import (
    generate_student_marks_csv,
    generate_class_analysis_pdf,
    generate_individual_student_pdf
)
from pdf_processor import SUBJECT_DEFINITIONS

# Set page config
favicon_icon = "assets/favicon_64.png" if os.path.exists("assets/favicon_64.png") else "⚡"
st.set_page_config(
    page_title="MARKNOVA • Clarity in Every Score",
    page_icon=favicon_icon,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Initialize Session State
if "splash_phase" not in st.session_state:
    st.session_state["splash_phase"] = 1  # 1: Brand intro, 2: Developed by, 3: Main dashboard

if "df" not in st.session_state:
    df, meta, report = get_initial_dataset()
    st.session_state["df"] = df
    st.session_state["metadata"] = meta
    st.session_state["report"] = report

if "selected_student_roll" not in st.session_state:
    st.session_state["selected_student_roll"] = None

if "nav_page" not in st.session_state:
    st.session_state["nav_page"] = "Dashboard"

# ==========================================
# INTRODUCTORY SPLASH SCREEN STATE MACHINE
# ==========================================
if st.session_state["splash_phase"] in (1, 2):
    render_html(
        """
        <style>
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        div[data-testid="collapsedControl"] {
            display: none !important;
        }
        .main .block-container, [data-testid="stMainBlockContainer"] {
            max-width: 100vw !important;
            padding-top: clamp(8px, 2.5vh, 25px) !important;
            padding-bottom: clamp(8px, 2vh, 20px) !important;
            padding-left: 12px !important;
            padding-right: 12px !important;
            min-height: 98vh !important;
            min-height: 98svh !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            align-items: center !important;
            overflow: hidden !important;
        }
        div[data-testid="stHorizontalBlock"] {
            width: 100% !important;
            max-width: 680px !important;
            margin: 0 auto !important;
            justify-content: center !important;
        }
        body, html {
            overflow: hidden !important;
        }
        </style>
        """
    )

if st.session_state["splash_phase"] == 1:
    # Screen 1: Official MARKNOVA Brand Showcase
    splash_logo_path = "assets/marknova_logo.png"
    if os.path.exists(splash_logo_path):
        with open(splash_logo_path, "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode("utf-8")
        logo_markup = f'<img src="data:image/png;base64,{logo_b64}" class="splash-hero-logo" alt="MARKNOVA • Clarity in Every Score">'
    else:
        logo_markup = '<h1 class="splash-title">MARKNOVA</h1><p class="splash-tagline">Clarity in Every Score.</p>'

    render_html(
        f"""
        <div class="splash-container">
            <div style="display:inline-block; padding: 5px 18px; border-radius: 9999px; background: #EFF6FF; border: 1px solid #BFDBFE; color: #2563EB; font-size: 0.78rem; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 18px;">
                ACADEMIC PERFORMANCE DASHBOARD
            </div>
            <div style="margin: 0 auto 16px auto; display: flex; justify-content: center; align-items: center; width: 100%;">
                {logo_markup}
            </div>
            <div style="max-width: 580px; margin: 0 auto 28px auto; color: #64748B; font-size: 0.95rem; line-height: 1.6;">
                Engineered for College of Engineering Chengannur, Electrical & Electronics Engineering, Semester 1.
                Automated marksheet extraction, precision analytics, and performance intelligence.
            </div>
        </div>
        """
    )
    
    col1, col2, col3 = st.columns([2, 1.4, 2])
    with col2:
        if st.button("Continue  →", key="splash_next_1", use_container_width=True, type="primary"):
            st.session_state["splash_phase"] = 2
            st.rerun()
            
    st.stop()

elif st.session_state["splash_phase"] == 2:
    # Screen 2: BRAIN BEHIND showcase (Light SaaS mode, 100vw x 100vh viewport fit)
    dev_photo_path = "assets/pop.png"
    has_photo = os.path.exists(dev_photo_path) and os.path.getsize(dev_photo_path) > 0

    if has_photo:
        with open(dev_photo_path, "rb") as f:
            photo_b64 = base64.b64encode(f.read()).decode("utf-8")
        photo_markup = f"""
        <div class="brain-photo-container">
            <div class="brain-illustration-card">
                <img src="data:image/png;base64,{photo_b64}" class="brain-dev-photo" alt="Brain Behind Illustration">
            </div>
        </div>
        """
    else:
        abs_path = os.path.abspath(dev_photo_path)
        print(f"\n⚠️  [MARKNOVA DEV WARNING] Missing illustration file!", flush=True)
        print(f"⚠️  Expected file path: {abs_path}", flush=True)
        print(f"⚠️  Please ensure 'pop.png' is placed in the 'assets/' directory.\n", flush=True)
        photo_markup = """
        <div class="brain-photo-container">
            <div class="brain-illustration-card" style="padding: 18px 26px; border: 1px dashed #CBD5E1;">
                <span style="color: #64748B; font-size: 0.88rem; font-weight: 500;">
                    Illustration pending • Please check terminal for expected file path.
                </span>
            </div>
        </div>
        """

    screen2_html = f"""
    <div class="splash-container">
        <div class="splash-dev-label">BRAIN BEHIND</div>
        {photo_markup}
        <div class="brain-names-grid">
            <div class="brain-name-card" style="animation-delay: 0.08s;">
                <span class="brain-dot"></span>
                <span class="brain-name-text">AABIS MUHAMMED</span>
            </div>
            <div class="brain-name-card" style="animation-delay: 0.16s;">
                <span class="brain-dot"></span>
                <span class="brain-name-text">AARON GEORGE</span>
            </div>
            <div class="brain-name-card" style="animation-delay: 0.24s;">
                <span class="brain-dot"></span>
                <span class="brain-name-text">AARON JOSEPH</span>
            </div>
            <div class="brain-name-card" style="animation-delay: 0.32s;">
                <span class="brain-dot"></span>
                <span class="brain-name-text">ABHIMANYU KEVIN</span>
            </div>
        </div>
        <div class="mentor-appreciation-card">
            <div class="mentor-heading">
                <span class="mentor-sparkle">✦</span>
                SINCERE THANKS TO OUR SHERIN MISS
                <span class="mentor-sparkle">✦</span>
            </div>
            <p class="mentor-quote">
                &ldquo;For giving us the idea that inspired MARKNOVA. Your guidance turned a simple thought into something we are proud to create.&rdquo;
            </p>
        </div>
    </div>
    """

    render_html(screen2_html)

    col1, col2, col3 = st.columns([1.8, 1.4, 1.8])
    with col2:
        if st.button("Enter Dashboard  ⚡", key="splash_enter", use_container_width=True, type="primary"):
            st.session_state["splash_phase"] = 3
            st.rerun()

    st.stop()

# ==========================================
# MAIN APPLICATION INTERFACE (Phase 3)
# ==========================================

df = st.session_state["df"]
metadata = st.session_state["metadata"]
report = st.session_state["report"]

# -----------------
# SIDEBAR
# -----------------
with st.sidebar:
    # Official compact MARKNOVA brand logo
    sb_logo_path = "assets/marknova_logo.png"
    if os.path.exists(sb_logo_path):
        with open(sb_logo_path, "rb") as f:
            sb_logo_b64 = base64.b64encode(f.read()).decode("utf-8")
        render_html(
            f"""
            <div class="sidebar-logo-container">
                <img src="data:image/png;base64,{sb_logo_b64}" class="sidebar-logo-img" alt="MARKNOVA • Clarity in Every Score">
            </div>
            """
        )
    else:
        render_html(
            """
            <div class="brand-title">MARKNOVA</div>
            <div class="brand-tagline">Clarity in Every Score.</div>
            """
        )

    # Department & College badge
    render_html(
        f"""
        <div class="dept-badge">
            <strong>{metadata.get('college', 'College of Engineering Chengannur')}</strong>
            {metadata.get('department', 'Electrical & Electronics Engineering')}<br/>
            <span>{metadata.get('semester', 'Semester 1')} • Academic Year {metadata.get('academic_year', '2026-27')}</span>
        </div>
        """
    )

    # Current PDF indicator
    pdf_name = metadata.get("filename", "No PDF")
    num_students = len(df)
    render_html(
        f"""
        <div style="background: #F0F7FF; border: 1px solid #BFDBFE; border-radius: 8px; padding: 10px; margin-bottom: 20px;">
            <div style="font-size: 0.72rem; color: #49352A; text-transform: uppercase; letter-spacing: 0.8px; font-weight: 700;">Active Marksheet</div>
            <div style="font-size: 0.84rem; font-weight: 600; color: #1E3A5F; margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{pdf_name}">
                📄 {pdf_name}
            </div>
            <div style="font-size: 0.74rem; color: #15803D; margin-top: 4px; font-weight: 600;">
                ● {num_students} Students Verified
            </div>
        </div>
        """
    )

    # Navigation Menu
    nav_options = [
        "Dashboard",
        "Class Topper",
        "Subject Analysis",
        "Student Directory",
        "Performance Comparison",
        "Reports",
        "Settings / Upload PDF"
    ]
    
    selected_nav = st.radio(
        "Navigation",
        nav_options,
        index=nav_options.index(st.session_state["nav_page"]) if st.session_state["nav_page"] in nav_options else 0,
        label_visibility="collapsed"
    )

    # Reset selected student if navigating away from Directory
    if selected_nav != st.session_state["nav_page"]:
        if selected_nav != "Student Directory":
            st.session_state["selected_student_roll"] = None
        st.session_state["nav_page"] = selected_nav
        st.rerun()

    render_html("<hr style='border: none; border-top: 1px solid #E2E8F0; margin: 25px 0 15px 0;' />")
    
    # Replay Splash Screen option
    if st.button("Intro Splash Screen", key="btn_replay_splash", use_container_width=True):
        st.session_state["splash_phase"] = 1
        st.rerun()

# -----------------
# VIEW ROUTING
# -----------------

# 1. MAIN DASHBOARD
if st.session_state["nav_page"] == "Dashboard":
    dash_logo_path = "assets/marknova_logo.png"
    if os.path.exists(dash_logo_path):
        with open(dash_logo_path, "rb") as f:
            dash_b64 = base64.b64encode(f.read()).decode("utf-8")
        dash_logo_html = f'<img src="data:image/png;base64,{dash_b64}" class="dashboard-header-logo" alt="MARKNOVA">'
    else:
        dash_logo_html = ""

    render_html(f"""
    <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px; margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid #E2E8F0;">
        <div style="display: flex; align-items: center; gap: 16px; flex-wrap: wrap;">
            {dash_logo_html}
            <div style="border-left: 2px solid #E2E8F0; padding-left: 16px;">
                <h1 style="margin: 0; font-size: 1.85rem; font-weight: 800; color: #14213D; letter-spacing: 0.2px; line-height: 1.2;">
                    Academic Performance Dashboard
                </h1>
                <p style="margin: 3px 0 0 0; color: #64748B; font-size: 0.9rem;">
                    Semester 1 series assessment intelligence overview • College of Engineering Chengannur (EEE)
                </p>
            </div>
        </div>
    </div>
    """)

    overview = get_class_overview_stats(df)
    toppers = get_overall_class_toppers(df)

    if df.empty:
        st.info("ℹ️ No marksheet loaded yet. Navigate to **Settings / Upload PDF** in the sidebar to upload a marksheet PDF and view analytics.")

    # KPI Row
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        render_html(render_kpi("Total Students", str(overview["total_students"]), "Enrolled Cohort"))
    with c2:
        render_html(render_kpi("Class Average", f"{overview['class_avg_pct']}%", "Overall Aggregate", is_gradient=True))
    with c3:
        render_html(render_kpi("Highest Score", f"{overview['highest_pct']}%", "Cohort Maximum"))
    with c4:
        render_html(render_kpi("Lowest Score", f"{overview['lowest_pct']}%", "Cohort Minimum"))
    with c5:
        render_html(render_kpi("Total Subjects", str(overview["num_subjects"]), "Credit Courses"))

    # Dedicated Class Topper Section (ONLY overall class topper, no Top 2, Top 3, or Top 10)
    render_html("""
    <div style="margin: 24px 0 12px 0;">
        <h2 style="margin: 0; font-size: 1.4rem; font-weight: 700; color: #14213D;">
            🏆 Overall Class Topper
        </h2>
    </div>
    """)

    if toppers:
        for t in toppers:
            render_html(
                f"""
                <div class="glass-card glass-card-topper" style="padding: 24px 28px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
                        <div>
                            <div style="display: inline-block; padding: 4px 12px; border-radius: 6px; background: #F3E8FF; border: 1px solid #DDD6FE; color: #7C3AED; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">
                                CLASS RANK #1
                            </div>
                            <h2 style="margin: 0; font-size: 2rem; font-weight: 800; color: #14213D;">
                                {t['name']}
                            </h2>
                            <div style="font-family: 'JetBrains Mono', monospace; font-size: 1rem; color: #2563EB; font-weight: 700; margin-top: 4px;">
                                Roll Number: {t['roll_no']}
                            </div>
                        </div>
                        <div style="display: flex; gap: 20px;">
                            <div style="text-align: right; background: #FFFFFF; padding: 12px 20px; border-radius: 12px; border: 1px solid #E2E8F0; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
                                <div style="font-size: 0.74rem; color: #49352A; text-transform: uppercase; font-weight: 700;">Total Score</div>
                                <div style="font-size: 1.8rem; font-weight: 800; color: #2563EB;">{t['total']}<span style="font-size: 0.95rem; color:#64748B;">/200</span></div>
                            </div>
                            <div style="text-align: right; background: #FFFFFF; padding: 12px 20px; border-radius: 12px; border: 1px solid #E2E8F0; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
                                <div style="font-size: 0.74rem; color: #49352A; text-transform: uppercase; font-weight: 700;">Percentage</div>
                                <div style="font-size: 1.8rem; font-weight: 800; color: #7C3AED;">{t['percentage']}%</div>
                            </div>
                        </div>
                    </div>
                </div>
                """
            )

    # Subject Average Overview Chart
    render_html("""
    <div style="margin: 28px 0 12px 0;">
        <h2 style="margin: 0; font-size: 1.35rem; font-weight: 700; color: #14213D;">
            Subject Average Performance Overview
        </h2>
    </div>
    """)
    
    sub_avg_fig = create_subject_average_pct_chart(df)
    st.plotly_chart(sub_avg_fig, use_container_width=True)

# 2. CLASS TOPPER PAGE
elif st.session_state["nav_page"] == "Class Topper":
    render_html("""
    <div style="margin-bottom: 22px;">
        <h1 style="margin: 0; font-size: 2.1rem; font-weight: 800; color: #14213D; letter-spacing: 0.3px;">
            Class Topper Showcase
        </h1>
        <p style="margin: 4px 0 0 0; color: #64748B; font-size: 0.95rem;">
            Honoring the premier academic benchmark in Semester 1 (EEE).
        </p>
    </div>
    """)

    toppers = get_overall_class_toppers(df)
    if not toppers:
        st.info("No topper records found.")
    else:
        for t in toppers:
            render_html(
                f"""
                <div class="glass-card glass-card-topper" style="padding: 30px; margin-bottom: 24px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 20px;">
                        <div>
                            <span class="chip chip-violet" style="font-size: 0.8rem; padding: 6px 14px;">RANK #1 • COHORT BENCHMARK</span>
                            <h1 style="margin: 12px 0 6px 0; font-size: 2.5rem; font-weight: 800; color: #14213D;">
                                {t['name']}
                            </h1>
                            <div style="font-family: 'JetBrains Mono', monospace; font-size: 1.15rem; color: #2563EB; font-weight: 700;">
                                {t['roll_no']}
                            </div>
                        </div>
                        <div style="display: flex; gap: 18px;">
                            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px; padding: 16px 24px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.04);">
                                <div style="font-size: 0.74rem; color: #49352A; text-transform: uppercase; font-weight: 700;">Overall Aggregate</div>
                                <div style="font-size: 2.2rem; font-weight: 800; color: #2563EB;">{t['total']}<span style="font-size: 1rem; color: #64748B;">/200</span></div>
                            </div>
                            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px; padding: 16px 24px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.04);">
                                <div style="font-size: 0.74rem; color: #49352A; text-transform: uppercase; font-weight: 700;">Overall Percentage</div>
                                <div style="font-size: 2.2rem; font-weight: 800; color: #7C3AED;">{t['percentage']}%</div>
                            </div>
                        </div>
                    </div>
                </div>
                """
            )

            # Subject Breakdown Cards
            render_html("""
            <h3 style="font-size: 1.3rem; font-weight: 700; color: #14213D; margin-bottom: 14px;">
                Subject-Wise Scores
            </h3>
            """)
            
            sub_cols = st.columns(len(SUBJECT_DEFINITIONS))
            for idx, sub in enumerate(SUBJECT_DEFINITIONS):
                code = sub["code"]
                score = t["subject_marks"].get(code, 0.0)
                pct = round((score / 40.0) * 100.0, 1)
                with sub_cols[idx]:
                    render_html(
                        f"""
                        <div class="glass-card" style="padding: 16px; text-align: center; border-color: #E2E8F0;">
                            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.88rem; font-weight: 700; color: #2563EB;">{code}</div>
                            <div style="font-size: 1.6rem; font-weight: 800; color: #14213D; margin: 4px 0;">{score}<span style="font-size: 0.8rem; color: #64748B;">/40</span></div>
                            <div style="font-size: 0.8rem; color: #7C3AED; font-weight: 700;">{pct}%</div>
                        </div>
                        """
                    )

            # Chart
            render_html("""
            <h3 style="font-size: 1.3rem; font-weight: 700; color: #14213D; margin: 24px 0 12px 0;">
                Subject Performance Chart
            </h3>
            """)
            topper_chart = create_topper_breakdown_chart(t["subject_marks"])
            st.plotly_chart(topper_chart, use_container_width=True)

# 3. SUBJECT ANALYSIS PAGE
elif st.session_state["nav_page"] == "Subject Analysis":
    render_html("""
    <div style="margin-bottom: 22px;">
        <h1 style="margin: 0; font-size: 2.1rem; font-weight: 800; color: #14213D; letter-spacing: 0.3px;">
            Subject-Wise Academic Analysis
        </h1>
        <p style="margin: 4px 0 0 0; color: #64748B; font-size: 0.95rem;">
            Deep assessment analysis for each of the five core subjects in Semester 1.
        </p>
    </div>
    """)

    subject_codes = [s["code"] for s in SUBJECT_DEFINITIONS]
    subject_tabs = st.tabs([f"{s['code']} • {s['name'][:22]}..." for s in SUBJECT_DEFINITIONS])

    for idx, sub_code in enumerate(subject_codes):
        with subject_tabs[idx]:
            analysis = get_subject_analysis(df, sub_code)
            if not analysis:
                st.warning(f"No analysis available for {sub_code}.")
                continue

            render_html(
                f"""
                <div class="glass-card" style="border-color: #BFDBFE; padding: 22px 26px; margin-bottom: 20px; background: linear-gradient(135deg, #FFFFFF 0%, #F0F7FF 100%);">
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 1rem; color: #2563EB; font-weight: 700;">{analysis['code']}</div>
                    <h2 style="margin: 4px 0 6px 0; font-size: 1.7rem; font-weight: 800; color: #14213D;">
                        {analysis['name']}
                    </h2>
                    <div style="font-size: 0.88rem; color: #64748B;">
                        Maximum Marks: {int(analysis['max_marks'])} • Evaluated Students: {analysis['num_valid']}
                    </div>
                </div>
                """
            )

            # Metric Cards
            m1, m2, m3, m4, m5 = st.columns(5)
            with m1:
                render_html(render_kpi("Class Average", f"{analysis['class_avg_marks']}/40", f"Average %: {analysis['class_avg_pct']}%"))
            with m2:
                render_html(render_kpi("Average %", f"{analysis['class_avg_pct']}%", "Cohort Mean", is_gradient=True))
            with m3:
                render_html(render_kpi("Highest Mark", f"{analysis['highest_marks']}/40", "Maximum Scored"))
            with m4:
                render_html(render_kpi("Lowest Mark", f"{analysis['lowest_marks']}/40", "Minimum Scored"))
            with m5:
                render_html(render_kpi("Valid Scores", str(analysis["num_valid"]), "Students Present"))

            # Subject Topper Box (Supports Ties)
            render_html("""
            <h3 style="font-size: 1.25rem; font-weight: 700; color: #14213D; margin: 20px 0 10px 0;">
                ⭐ Subject Topper(s)
            </h3>
            """)

            topper_cols = st.columns(len(analysis["toppers"]))
            for t_idx, top in enumerate(analysis["toppers"]):
                with topper_cols[t_idx]:
                    render_html(
                        f"""
                        <div class="glass-card" style="border-color: #DDD6FE; padding: 18px; background: #FAF5FF;">
                            <span class="chip chip-violet">Subject Highest</span>
                            <div style="font-size: 1.2rem; font-weight: 700; color: #14213D; margin: 8px 0 2px 0;">{top['name']}</div>
                            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.9rem; color: #2563EB; font-weight: 700;">{top['roll_no']}</div>
                            <div style="margin-top: 10px; font-size: 1.5rem; font-weight: 800; color: #7C3AED;">
                                {top['marks']}<span style="font-size: 0.9rem; color: #64748B;">/{int(analysis['max_marks'])}</span>
                                <span style="font-size: 0.85rem; color: #2563EB; font-weight: 700;">({top['percentage']}%)</span>
                            </div>
                        </div>
                        """
                    )

# 4. STUDENT DIRECTORY (Clickable Cards & Profiles)
elif st.session_state["nav_page"] == "Student Directory":
    if st.session_state.get("selected_student_roll"):
        render_individual_profile(df, st.session_state["selected_student_roll"])
    else:
        render_student_directory(df)

# 5. PERFORMANCE COMPARISON PAGE
elif st.session_state["nav_page"] == "Performance Comparison":
    render_html("""
    <div style="margin-bottom: 22px;">
        <h1 style="margin: 0; font-size: 2.1rem; font-weight: 800; color: #14213D; letter-spacing: 0.3px;">
            Interactive Performance Comparison
        </h1>
        <p style="margin: 4px 0 0 0; color: #64748B; font-size: 0.95rem;">
            Comparative benchmarking across courses and individual student profiles.
        </p>
    </div>
    """)

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(create_subject_average_marks_chart(df), use_container_width=True)
    with c2:
        st.plotly_chart(create_highest_vs_average_chart(df), use_container_width=True)

    # Student vs Class Benchmark Interactive Selector
    render_html("<hr style='border: none; border-top: 1px solid #E2E8F0; margin: 24px 0;' />")
    render_html("""
    <h3 style="font-size: 1.3rem; font-weight: 700; color: #14213D; margin-bottom: 12px;">
        Individual Student vs Class Average Benchmark
    </h3>
    """)

    student_options = [f"{r['roll_no']} • {r['name']}" for _, r in df.sort_values(by="roll_no").iterrows()]
    selected_option = st.selectbox("Select Student to Compare", student_options)
    
    if selected_option:
        selected_roll = selected_option.split(" • ")[0]
        comp_profile = get_student_profile(df, selected_roll)
        if comp_profile:
            r_col1, r_col2 = st.columns([1.2, 0.8])
            with r_col1:
                st.plotly_chart(create_student_comparison_radar_chart(comp_profile), use_container_width=True)
            with r_col2:
                diff_sign = "+" if comp_profile["pct_diff"] >= 0 else ""
                diff_col = "#15803D" if comp_profile["pct_diff"] >= 0 else "#DC2626"
                render_html(
                    f"""
                    <div class="glass-card" style="padding: 24px; border-color: #E2E8F0; margin-top: 20px; background: #FFFFFF;">
                        <span class="chip chip-cyan">{comp_profile['roll_no']}</span>
                        <div style="font-size: 1.5rem; font-weight: 800; color: #14213D; margin: 8px 0 4px 0;">{comp_profile['name']}</div>
                        <div style="font-size: 0.9rem; color: #64748B; margin-bottom: 16px;">Class Rank: #{comp_profile['rank']}</div>
                        
                        <div style="margin-bottom: 10px;">
                            <span style="font-size: 0.85rem; color: #49352A; font-weight:600;">Student Aggregate:</span>
                            <span style="font-size: 1.15rem; font-weight: 800; color: #2563EB; margin-left: 6px;">{comp_profile['percentage']}%</span>
                        </div>
                        <div style="margin-bottom: 10px;">
                            <span style="font-size: 0.85rem; color: #49352A; font-weight:600;">Class Average:</span>
                            <span style="font-size: 1.15rem; font-weight: 800; color: #1E3A5F; margin-left: 6px;">{comp_profile['class_avg_pct']}%</span>
                        </div>
                        <div style="margin-bottom: 14px;">
                            <span style="font-size: 0.85rem; color: #49352A; font-weight:600;">Cohort Variance:</span>
                            <span style="font-size: 1.15rem; font-weight: 800; color: {diff_col}; margin-left: 6px;">{diff_sign}{comp_profile['pct_diff']}%</span>
                        </div>
                        
                        <div style="font-size: 0.85rem; color: #64748B; border-top: 1px solid #E2E8F0; padding-top: 10px;">
                            Strongest: <strong style="color:#7C3AED;">{comp_profile['strongest_subject']['code']}</strong> ({comp_profile['strongest_subject']['marks']}/40)
                        </div>
                    </div>
                    """
                )

# 6. REPORTS PAGE
elif st.session_state["nav_page"] == "Reports":
    render_html("""
    <div style="margin-bottom: 22px;">
        <h1 style="margin: 0; font-size: 2.1rem; font-weight: 800; color: #14213D; letter-spacing: 0.3px;">
            Export & Report Generation
        </h1>
        <p style="margin: 4px 0 0 0; color: #64748B; font-size: 0.95rem;">
            Generate and download high-resolution academic analysis reports and structured marksheets.
        </p>
    </div>
    """)

    overview = get_class_overview_stats(df)
    toppers = get_overall_class_toppers(df)
    subject_analyses = get_all_subject_analyses(df)

    r_col1, r_col2 = st.columns(2)

    with r_col1:
        render_html(
            """
            <div class="glass-card" style="padding: 24px; min-height: 220px; border-color: #BFDBFE; background: #FFFFFF;">
                <div style="font-size: 1.3rem; font-weight: 700; color: #14213D; margin-bottom: 6px;">
                    📑 Complete Class Analysis PDF
                </div>
                <p style="color: #64748B; font-size: 0.9rem; line-height: 1.5; margin-bottom: 18px;">
                    Official comprehensive multi-page document featuring college header, class KPIs, subject averages, subject toppers, and full student roster with individual ranks.
                </p>
            </div>
            """
        )
        pdf_bytes = generate_class_analysis_pdf(df, metadata, overview, subject_analyses, toppers)
        st.download_button(
            label="Download Complete Class Report (PDF)",
            data=pdf_bytes,
            file_name="MARKNOVA_Class_Analysis_Report.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary"
        )

    with r_col2:
        render_html(
            """
            <div class="glass-card" style="padding: 24px; min-height: 220px; border-color: #DDD6FE; background: #FFFFFF;">
                <div style="font-size: 1.3rem; font-weight: 700; color: #14213D; margin-bottom: 6px;">
                    📊 Complete Student Marks CSV
                </div>
                <p style="color: #64748B; font-size: 0.9rem; line-height: 1.5; margin-bottom: 18px;">
                    Structured CSV spreadsheet containing Roll Number, Student Name, A1-A6 assessments, five combined subject scores, calculated totals, percentages, and class ranks.
                </p>
            </div>
            """
        )
        csv_bytes = generate_student_marks_csv(df)
        st.download_button(
            label="Download Student Marks (CSV)",
            data=csv_bytes,
            file_name="MARKNOVA_Student_Marks.csv",
            mime="text/csv",
            use_container_width=True
        )

    # Individual Student Report Section
    render_html("<hr style='border: none; border-top: 1px solid #E2E8F0; margin: 30px 0 20px 0;' />")
    render_html("""
    <h3 style="font-size: 1.3rem; font-weight: 700; color: #14213D; margin-bottom: 12px;">
        🎓 Individual Student Academic Report (PDF)
    </h3>
    """)

    ind_col1, ind_col2 = st.columns([2, 1])
    with ind_col1:
        ind_student_opts = [f"{r['roll_no']} • {r['name']}" for _, r in df.sort_values(by="roll_no").iterrows()]
        ind_selected = st.selectbox("Select Student for PDF Generation", ind_student_opts, key="ind_rep_select")
        
    with ind_col2:
        if ind_selected:
            roll_code = ind_selected.split(" • ")[0]
            ind_prof = get_student_profile(df, roll_code)
            if ind_prof:
                ind_pdf_bytes = generate_individual_student_pdf(ind_prof)
                st.download_button(
                    label=f"Download Report for {roll_code} (PDF)",
                    data=ind_pdf_bytes,
                    file_name=f"Report_{roll_code}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

# 7. SETTINGS / UPLOAD PDF PAGE
elif st.session_state["nav_page"] == "Settings / Upload PDF":
    render_html("""
    <div style="margin-bottom: 22px;">
        <h1 style="margin: 0; font-size: 2.1rem; font-weight: 800; color: #14213D; letter-spacing: 0.3px;">
            Data Ingestion & PDF Upload
        </h1>
        <p style="margin: 4px 0 0 0; color: #64748B; font-size: 0.95rem;">
            Upload new series marksheet PDFs and review dynamic extraction summaries.
        </p>
    </div>
    """)

    upload_c1, upload_c2 = st.columns([1.2, 0.8])
    with upload_c1:
        uploaded_file = st.file_uploader(
            "Upload Series Marksheet PDF",
            type=["pdf"],
            help="Upload an internal marksheet statement matching the College of Engineering Chengannur format."
        )

        if uploaded_file is not None:
            if st.button("Process & Load Uploaded PDF", type="primary"):
                with st.spinner("Extracting marksheet data and validating student records..."):
                    new_df, new_meta, new_report = process_marksheet_file(uploaded_file, uploaded_file.name)
                    st.session_state["df"] = new_df
                    st.session_state["metadata"] = new_meta
                    st.session_state["report"] = new_report
                    st.session_state["selected_student_roll"] = None
                    st.success(f"Successfully processed {len(new_df)} student records from {uploaded_file.name}!")
                    st.rerun()

        # Reset button to default PDF
        if os.path.exists(DEFAULT_PDF_PATH):
            if st.button("🔄 Reset to Default S1 Marksheet"):
                with st.spinner("Reloading initial dataset..."):
                    d_df, d_meta, d_rep = get_initial_dataset()
                    st.session_state["df"] = d_df
                    st.session_state["metadata"] = d_meta
                    st.session_state["report"] = d_rep
                    st.session_state["selected_student_roll"] = None
                    st.success("Default marksheet restored successfully.")
                    st.rerun()

    with upload_c2:
        # Extraction & Validation Summary
        render_html("""
        <div class="glass-card" style="padding: 20px; border-color: #E2E8F0; background: #F8FAFC;">
            <div style="font-size: 0.8rem; text-transform: uppercase; color: #49352A; font-weight: 700; letter-spacing: 1px; margin-bottom: 12px;">
                Extraction & Integrity Summary
            </div>
        """)

        render_html(
            f"""
            <div style="font-size: 0.88rem; color: #1E3A5F; margin-bottom: 8px;">
                • Total Records Extracted: <strong style="color: #2563EB;">{report.total_records}</strong>
            </div>
            <div style="font-size: 0.88rem; color: #1E3A5F; margin-bottom: 8px;">
                • Duplicate Roll Numbers: <strong style="color: {'#15803D' if not report.duplicate_rolls else '#DC2626'};">{len(report.duplicate_rolls)}</strong>
            </div>
            <div style="font-size: 0.88rem; color: #1E3A5F; margin-bottom: 8px;">
                • Missing Roll Sequence Gaps: <strong style="color: {'#15803D' if not report.missing_rolls else '#DC2626'};">{len(report.missing_rolls)}</strong>
            </div>
            <div style="font-size: 0.88rem; color: #1E3A5F; margin-bottom: 8px;">
                • Totals Verified vs Source: <strong style="color: {'#15803D' if report.all_totals_verified else '#DC2626'};">{'100% Match' if report.all_totals_verified else 'Mismatches Detected'}</strong>
            </div>
            <div style="font-size: 0.88rem; color: #1E3A5F; margin-bottom: 8px;">
                • Students with Explicit 'AB': <strong style="color: #D97706;">{len(report.students_with_absent)}</strong>
            </div>
            <div style="font-size: 0.88rem; color: #1E3A5F;">
                • Students with Blank Entries: <strong style="color: #D97706;">{len(report.students_with_blank)}</strong>
            </div>
            </div>
            """
        )

        if report.warnings:
            render_html("<div style='margin-top: 14px;'>")
            for w in report.warnings:
                st.warning(w)
            render_html("</div>")
