"""
charts.py - Modern Light SaaS Plotly visualizations for MARKNOVA.
Provides clean white-themed interactive charts with deep navy typography,
blue, cyan, violet and red data series, clear grid lines, and crisp tooltips.
Strictly excludes grade distribution or student performance histograms.
"""

import plotly.graph_objects as go
import pandas as pd
from typing import Dict, List, Any
from pdf_processor import SUBJECT_DEFINITIONS

# Premium Light Palette Constants
COLOR_BLUE = "#2563EB"
COLOR_CYAN = "#0284C7"
COLOR_VIOLET = "#7C3AED"
COLOR_RED = "#EF4444"
COLOR_NAVY = "#14213D"
COLOR_DARK_BLUE = "#1E3A5F"
COLOR_BROWN = "#49352A"
COLOR_GRID = "#E2E8F0"
COLOR_BG_CARD = "#FFFFFF"
COLOR_TEXT = "#14213D"
COLOR_MUTED = "#64748B"

def apply_light_layout(fig: go.Figure, title: str = "", height: int = 380) -> go.Figure:
    """Applies a consistent modern light SaaS layout to any Plotly figure."""
    fig.update_layout(
        title={
            "text": title,
            "y": 0.94,
            "x": 0.02,
            "xanchor": "left",
            "yanchor": "top",
            "font": {"family": "Outfit, sans-serif", "size": 16, "color": COLOR_NAVY}
        },
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        height=height,
        margin={"l": 40, "r": 30, "t": 60, "b": 40},
        font={"family": "Outfit, sans-serif", "color": COLOR_NAVY},
        hoverlabel={
            "bgcolor": "#FFFFFF",
            "bordercolor": "#CBD5E1",
            "font": {"family": "Outfit, sans-serif", "color": COLOR_NAVY, "size": 13}
        },
        legend={
            "font": {"color": COLOR_NAVY, "size": 12},
            "bgcolor": "#F8FAFC",
            "bordercolor": "#E2E8F0",
            "borderwidth": 1
        }
    )
    return fig

def create_subject_average_pct_chart(df: pd.DataFrame) -> go.Figure:
    """Renders a sleek horizontal bar chart of subject-wise class average percentages."""
    labels = []
    codes = []
    avg_pcts = []
    
    for sub in SUBJECT_DEFINITIONS:
        code = sub["code"]
        name_short = sub["name"].split(" and ")[0].split(" for ")[0]
        avg_mark = df[code].mean() if code in df.columns else 0.0
        pct = round((avg_mark / sub["max_marks"]) * 100.0, 1)
        
        labels.append(f"<b>{code}</b><br><span style='font-size:10px;color:#64748B'>{name_short}</span>")
        codes.append(code)
        avg_pcts.append(pct)
        
    fig = go.Figure(
        data=[
            go.Bar(
                x=avg_pcts,
                y=labels,
                orientation="h",
                text=[f"{p}%" for p in avg_pcts],
                textposition="outside",
                marker=dict(
                    color=avg_pcts,
                    colorscale=[
                        [0.0, "#2563EB"],
                        [0.6, "#7C3AED"],
                        [1.0, "#EF4444"]
                    ],
                    line=dict(color="#1E3A5F", width=1)
                ),
                hovertemplate="<b>%{y}</b><br>Class Average: %{x}%<extra></extra>"
            )
        ]
    )
    
    fig.update_xaxes(
        range=[0, 100],
        title="Class Average (%)",
        gridcolor=COLOR_GRID,
        zerolinecolor=COLOR_GRID
    )
    fig.update_yaxes(
        autorange="reversed",
        gridcolor="rgba(0,0,0,0)"
    )
    
    return apply_light_layout(fig, "Subject-Wise Class Average (%)", height=340)

def create_subject_average_marks_chart(df: pd.DataFrame) -> go.Figure:
    """Renders vertical bar chart of subject-wise average marks."""
    codes = [sub["code"] for sub in SUBJECT_DEFINITIONS]
    avg_marks = [round(df[c].mean(), 2) for c in codes if c in df.columns]
    
    fig = go.Figure(
        data=[
            go.Bar(
                x=codes,
                y=avg_marks,
                text=avg_marks,
                textposition="outside",
                marker=dict(
                    color=COLOR_BLUE,
                    line=dict(color="#1D4ED8", width=1)
                ),
                hovertemplate="<b>%{x}</b><br>Average Mark: %{y}/40<extra></extra>"
            )
        ]
    )
    
    fig.update_yaxes(range=[0, 42], title="Average Marks (out of 40)", gridcolor=COLOR_GRID)
    fig.update_xaxes(title="Course Code", gridcolor="rgba(0,0,0,0)")
    
    return apply_light_layout(fig, "Subject-Wise Average Marks", height=340)

def create_highest_vs_average_chart(df: pd.DataFrame) -> go.Figure:
    """Compares highest marks achieved vs class average marks across all 5 subjects."""
    codes = [sub["code"] for sub in SUBJECT_DEFINITIONS]
    avg_marks = [round(df[c].mean(), 2) for c in codes if c in df.columns]
    highest_marks = [round(df[c].max(), 2) for c in codes if c in df.columns]
    
    fig = go.Figure()
    
    fig.add_trace(
        go.Bar(
            name="Subject Highest",
            x=codes,
            y=highest_marks,
            text=highest_marks,
            textposition="outside",
            marker=dict(
                color=COLOR_VIOLET,
                line=dict(color="#6D28D9", width=1)
            ),
            hovertemplate="<b>%{x} (Highest)</b>: %{y}/40<extra></extra>"
        )
    )
    
    fig.add_trace(
        go.Bar(
            name="Class Average",
            x=codes,
            y=avg_marks,
            text=avg_marks,
            textposition="outside",
            marker=dict(
                color=COLOR_CYAN,
                line=dict(color="#0369A1", width=1)
            ),
            hovertemplate="<b>%{x} (Class Average)</b>: %{y}/40<extra></extra>"
        )
    )
    
    fig.update_layout(barmode="group", bargroupgap=0.15)
    fig.update_yaxes(range=[0, 45], title="Marks (out of 40)", gridcolor=COLOR_GRID)
    fig.update_xaxes(title="Subject Code", gridcolor="rgba(0,0,0,0)")
    
    return apply_light_layout(fig, "Highest vs Class Average Marks per Subject", height=380)

def create_student_comparison_radar_chart(student_profile: Dict[str, Any]) -> go.Figure:
    """Renders an elegant Radar chart comparing an individual student to the class average."""
    subjects = student_profile["subjects"]
    codes = [s["code"] for s in subjects]
    codes_closed = codes + [codes[0]]
    
    student_pcts = [s["percentage"] for s in subjects]
    student_pcts_closed = student_pcts + [student_pcts[0]]
    
    class_pcts = [round((s["class_avg"] / s["max_marks"]) * 100.0, 1) for s in subjects]
    class_pcts_closed = class_pcts + [class_pcts[0]]
    
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatterpolar(
            r=class_pcts_closed,
            theta=codes_closed,
            fill='toself',
            name='Class Average',
            fillcolor='rgba(37, 99, 235, 0.12)',
            line=dict(color=COLOR_BLUE, width=2, dash='dot')
        )
    )
    
    # Clean display name for legend
    legend_name = student_profile['name']
    if len(legend_name) > 18:
        legend_name = legend_name[:16] + "..."
        
    fig.add_trace(
        go.Scatterpolar(
            r=student_pcts_closed,
            theta=codes_closed,
            fill='toself',
            name=legend_name,
            fillcolor='rgba(124, 58, 237, 0.22)',
            line=dict(color=COLOR_VIOLET, width=2.5)
        )
    )
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                gridcolor=COLOR_GRID,
                linecolor=COLOR_GRID,
                tickfont=dict(color=COLOR_MUTED, size=9)
            ),
            angularaxis=dict(
                gridcolor=COLOR_GRID,
                linecolor=COLOR_GRID,
                tickfont=dict(color=COLOR_NAVY, size=11, family="Outfit, sans-serif")
            ),
            bgcolor="#FFFFFF"
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.12,
            xanchor="center",
            x=0.5,
            font=dict(color=COLOR_NAVY, size=11),
            bgcolor="rgba(255, 255, 255, 0.95)",
            bordercolor=COLOR_GRID,
            borderwidth=1
        ),
        margin=dict(l=35, r=35, t=45, b=45),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        height=340
    )
    
    return apply_light_layout(fig, "Student vs Class Benchmark (Radar %)", height=350)

def create_topper_breakdown_chart(topper_marks: Dict[str, float]) -> go.Figure:
    """Renders a sleek breakdown of the class topper's marks."""
    codes = list(topper_marks.keys())
    marks = list(topper_marks.values())
    pcts = [round((m / 40.0) * 100.0, 1) for m in marks]
    
    fig = go.Figure(
        data=[
            go.Bar(
                x=codes,
                y=marks,
                text=[f"{m}/40 ({p}%)" for m, p in zip(marks, pcts)],
                textposition="outside",
                marker=dict(
                    color=COLOR_VIOLET,
                    line=dict(color="#6D28D9", width=1.5)
                ),
                hovertemplate="<b>%{x}</b>: %{y}/40<extra></extra>"
            )
        ]
    )
    
    fig.update_yaxes(range=[0, 45], title="Score Obtained (/40)", gridcolor=COLOR_GRID)
    fig.update_xaxes(title="Subject Code", gridcolor="rgba(0,0,0,0)")
    
    return apply_light_layout(fig, "Topper Subject Score Distribution", height=340)
