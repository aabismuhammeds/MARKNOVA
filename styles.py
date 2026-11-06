"""
styles.py - MARKNOVA Premium Light SaaS Styling Engine
Provides responsive CSS, white cards with subtle shadows,
sophisticated dark navy/brown typography, selective blue-to-red gradient text,
and bulletproof unindented HTML rendering helpers.
"""

import streamlit as st

def get_custom_css():
    return """
    <style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    :root {
        --bg-main: #F8FAFC;
        --bg-secondary: #F1F5F9;
        --bg-card: #FFFFFF;
        --bg-card-hover: #FFFFFF;
        --border-subtle: #E2E8F0;
        --border-accent: #BFDBFE;
        --border-hover: #93C5FD;
        --text-navy: #14213D;
        --text-blue: #1E3A5F;
        --text-brown: #49352A;
        --text-main: #172033;
        --text-secondary: #64748B;
        --text-muted: #94A3B8;
        --color-blue: #2563EB;
        --color-violet: #7C3AED;
        --color-red: #EF4444;
        --color-cyan: #0284C7;
        --color-burgundy: #6B1D2F;
        --color-gold: #D4AF37;
        --color-gold-light: #FBF5E6;
        --border-gold: #F3E5AB;
        --shadow-soft: 0 4px 20px -2px rgba(15, 23, 42, 0.05), 0 2px 6px -1px rgba(15, 23, 42, 0.03);
        --shadow-hover: 0 12px 28px -4px rgba(37, 99, 235, 0.12), 0 4px 8px -2px rgba(37, 99, 235, 0.06);
    }

    /* Overall app styling - Clean white & soft off-white */
    .stApp {
        background-color: var(--bg-main) !important;
        background: radial-gradient(circle at 10% 10%, #F0F4F8 0%, #F8FAFC 50%, #FFFFFF 100%) !important;
        font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: var(--text-main) !important;
    }

    /* Prevent horizontal overflow across the entire application */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        overflow-x: hidden !important;
        max-width: 100vw !important;
    }

    /* Ensure flex columns don't overflow on small/medium screens */
    [data-testid="column"] {
        min-width: 0 !important;
    }

    /* Top header removal & streamlinig */
    header[data-testid="stHeader"] {
        background: transparent !important;
    }
    
    footer {
        visibility: hidden !important;
    }

    /* Sidebar Styling - Soft clean light panel */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid var(--border-subtle) !important;
        box-shadow: 2px 0 16px rgba(15, 23, 42, 0.04) !important;
    }

    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.25rem !important;
        padding-bottom: 2rem !important;
    }

    /* MARKNOVA Official Brand Logo Styles */
    .sidebar-logo-container {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        padding: 4px 6px 10px 6px;
        margin-bottom: 2px;
        box-sizing: border-box;
    }

    .sidebar-logo-img {
        max-width: 210px;
        width: 90%;
        height: auto;
        object-fit: contain;
        background: transparent !important;
        filter: drop-shadow(0 3px 10px rgba(20, 33, 61, 0.08));
        transition: transform 0.25s ease;
    }

    .sidebar-logo-img:hover {
        transform: scale(1.025);
    }

    .splash-hero-logo {
        max-width: min(480px, 86vw);
        width: 100%;
        height: auto;
        object-fit: contain;
        background: transparent !important;
        filter: drop-shadow(0 8px 24px rgba(20, 33, 61, 0.12));
        transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .splash-hero-logo:hover {
        transform: scale(1.02);
    }

    .dashboard-header-logo {
        height: 48px;
        width: auto;
        max-width: 175px;
        object-fit: contain;
        background: transparent !important;
        filter: drop-shadow(0 2px 8px rgba(20, 33, 61, 0.06));
    }

    /* Gradient Typography Classes */
    .gradient-text {
        background: linear-gradient(135deg, #2563EB 0%, #7C3AED 50%, #EF4444 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: inline-block;
    }

    .brand-title {
        font-family: 'Outfit', sans-serif;
        font-size: 1.85rem;
        font-weight: 800;
        letter-spacing: 2px;
        background: linear-gradient(135deg, #2563EB 0%, #7C3AED 55%, #EF4444 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin: 0;
        line-height: 1.2;
    }

    .brand-tagline {
        font-family: 'Outfit', sans-serif;
        font-size: 0.8rem;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: var(--text-secondary);
        text-align: center;
        margin-top: 4px;
        margin-bottom: 16px;
        font-weight: 500;
    }

    /* Department Badge */
    .dept-badge {
        background: #F8FAFC;
        border: 1px solid var(--border-subtle);
        border-radius: 10px;
        padding: 12px 14px;
        margin-bottom: 20px;
        font-size: 0.82rem;
        color: var(--text-secondary);
        line-height: 1.45;
    }

    .dept-badge strong {
        color: var(--text-navy);
        display: block;
        font-size: 0.88rem;
        letter-spacing: 0.3px;
        margin-bottom: 2px;
    }

    /* Modern Light SaaS Cards */
    .glass-card {
        background: #FFFFFF;
        border: 1px solid var(--border-subtle);
        border-radius: 14px;
        padding: 22px;
        margin-bottom: 18px;
        box-shadow: var(--shadow-soft);
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        box-sizing: border-box !important;
        width: 100% !important;
        overflow: hidden !important;
    }

    .glass-card:hover {
        border-color: var(--border-hover);
        box-shadow: var(--shadow-hover);
        transform: translateY(-2px);
    }

    .glass-card-topper {
        background: linear-gradient(135deg, #FFFFFF 0%, #F5F3FF 100%);
        border: 1px solid rgba(124, 58, 237, 0.25);
        box-shadow: 0 8px 24px -2px rgba(124, 58, 237, 0.1);
    }

    .glass-card-topper:hover {
        border-color: rgba(124, 58, 237, 0.5);
        box-shadow: 0 14px 32px -4px rgba(124, 58, 237, 0.18);
    }

    /* Subject Performance Card */
    .subject-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 18px 22px;
        margin-bottom: 14px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
        transition: all 0.2s ease;
        position: relative;
        overflow: hidden;
        box-sizing: border-box;
    }

    .subject-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(180deg, #2563EB 0%, #7C3AED 100%);
        border-radius: 4px 0 0 4px;
    }

    .subject-card:hover {
        border-color: #93C5FD;
        box-shadow: 0 6px 18px rgba(37, 99, 235, 0.1);
        transform: translateY(-1px);
    }

    /* Metric KPI Cards */
    .kpi-container {
        display: flex;
        flex-direction: column;
        justifyContent: center;
    }

    .kpi-label {
        font-size: 0.76rem;
        text-transform: uppercase;
        letter-spacing: 1.1px;
        color: var(--text-brown);
        font-weight: 700;
        margin-bottom: 6px;
    }

    .kpi-value {
        font-family: 'Outfit', sans-serif;
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: var(--text-navy);
        line-height: 1.1;
    }

    .kpi-value-gradient {
        background: linear-gradient(135deg, #2563EB 0%, #7C3AED 50%, #EF4444 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .kpi-sub {
        font-size: 0.78rem;
        color: var(--text-secondary);
        margin-top: 5px;
    }

    /* Student Directory Card */
    .student-card {
        background: #FFFFFF;
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        transition: all 0.25s ease;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 120px;
        box-shadow: var(--shadow-soft);
        box-sizing: border-box;
    }

    .student-card:hover {
        border-color: var(--color-blue);
        box-shadow: var(--shadow-hover);
        transform: translateY(-3px);
    }

    .student-roll {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.95rem;
        font-weight: 700;
        color: var(--color-blue);
        letter-spacing: 0.5px;
    }

    .student-name {
        font-size: 1rem;
        font-weight: 600;
        color: var(--text-navy);
        margin-top: 4px;
        margin-bottom: 12px;
        line-height: 1.35;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .student-indicator {
        font-size: 0.78rem;
        color: var(--color-blue);
        display: flex;
        align-items: center;
        gap: 4px;
        font-weight: 600;
        letter-spacing: 0.4px;
    }

    /* Streamlit Buttons - Premium Blue-to-Violet Gradients */
    .stButton > button {
        background: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        color: var(--text-blue) !important;
        border-radius: 10px !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        padding: 0.55rem 1.1rem !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04) !important;
    }

    .stButton > button:hover {
        background: #F8FAFC !important;
        border-color: var(--color-blue) !important;
        color: var(--color-blue) !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.15) !important;
        transform: translateY(-1px) !important;
    }

    .stButton > button:active {
        transform: translateY(0) !important;
    }

    /* Primary CTA Buttons */
    button[kind="primary"] {
        background: linear-gradient(135deg, #2563EB 0%, #7C3AED 100%) !important;
        border: none !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3) !important;
    }

    button[kind="primary"]:hover {
        box-shadow: 0 8px 22px rgba(37, 99, 235, 0.45) !important;
        color: #FFFFFF !important;
        transform: translateY(-1px) !important;
    }

    /* Progress Bar */
    .futuristic-progress-container {
        width: 100%;
        background: #E2E8F0;
        border-radius: 9999px;
        height: 8px;
        overflow: hidden;
        margin-top: 8px;
        margin-bottom: 8px;
        position: relative;
    }

    .futuristic-progress-bar {
        height: 100%;
        border-radius: 9999px;
        background: linear-gradient(90deg, #2563EB 0%, #7C3AED 60%, #EF4444 100%);
        transition: width 0.6s ease;
    }

    /* Chips and Badges */
    .chip {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 5px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }

    .chip-cyan {
        background: #E0F2FE;
        color: #0369A1;
        border: 1px solid #BAE6FD;
    }

    .chip-violet {
        background: #F3E8FF;
        color: #7E22CE;
        border: 1px solid #E9D5FF;
    }

    .chip-green {
        background: #DCFCE7;
        color: #15803D;
        border: 1px solid #BBF7D0;
    }

    .chip-warning {
        background: #FEF3C7;
        color: #B45309;
        border: 1px solid #FDE68A;
    }

    /* Splash Screen Styles */
    .splash-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        max-height: 88vh;
        max-height: 88svh;
        text-align: center;
        padding: clamp(6px, 1.5vh, 20px) 16px;
        position: relative;
        margin: 0 auto;
        width: 100%;
        max-width: 820px;
        box-sizing: border-box;
    }

    .splash-title {
        font-family: 'Outfit', sans-serif;
        font-size: clamp(2.4rem, 5vw, 3.8rem);
        font-weight: 800;
        letter-spacing: 3px;
        background: linear-gradient(135deg, #2563EB 0%, #7C3AED 50%, #EF4444 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
        line-height: 1.1;
    }

    .splash-tagline {
        font-size: clamp(1.05rem, 2vw, 1.3rem);
        color: var(--text-blue);
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: clamp(12px, 2.2vh, 22px);
    }

    /* BRAIN BEHIND Showcase Styles */
    .splash-dev-label {
        font-family: 'Outfit', sans-serif;
        font-size: clamp(1.1rem, 2.2vw, 1.4rem);
        font-weight: 800;
        letter-spacing: 4px;
        color: var(--text-navy);
        text-transform: uppercase;
        margin: 0 0 clamp(8px, 1.6vh, 18px) 0;
        line-height: 1.2;
    }

    .brain-photo-container {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        margin-bottom: clamp(10px, 1.8vh, 18px);
    }

    .brain-illustration-card {
        background: #FFFFFF;
        border: 1px solid rgba(226, 232, 240, 0.95);
        border-radius: 20px;
        padding: clamp(6px, 1vh, 10px) clamp(10px, 1.5vw, 16px);
        box-shadow: 0 8px 24px -2px rgba(15, 23, 42, 0.06), 0 2px 6px -1px rgba(15, 23, 42, 0.03);
        display: inline-flex;
        align-items: center;
        justify-content: center;
        max-width: min(440px, 86vw);
        width: auto;
        overflow: hidden;
        transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.3s ease;
    }

    .brain-illustration-card:hover {
        transform: scale(1.02);
        box-shadow: 0 12px 32px -4px rgba(37, 99, 235, 0.12);
        border-color: #BFDBFE;
    }

    .brain-dev-photo {
        max-height: clamp(125px, 21vh, 180px);
        width: auto;
        max-width: 100%;
        object-fit: contain;
        background: transparent !important;
        display: block;
    }

    /* 4 Brain Behind Names - Responsive Grid & Glass Pills */
    .brain-names-grid {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        align-items: center;
        gap: clamp(6px, 1vh, 10px) clamp(8px, 1.4vw, 14px);
        max-width: 680px;
        margin: 0 auto clamp(8px, 1.3vh, 13px) auto;
    }

    .brain-name-card {
        background: #FFFFFF;
        border: 1px solid rgba(226, 232, 240, 0.95);
        border-radius: 9999px;
        padding: clamp(5px, 0.8vh, 7px) clamp(14px, 1.8vw, 20px);
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        animation: brainFadeUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) both;
    }

    .brain-name-card:hover {
        border-color: #93C5FD;
        box-shadow: 0 6px 18px rgba(37, 99, 235, 0.12), 0 0 14px rgba(124, 58, 237, 0.15);
        transform: translateY(-2px);
    }

    .brain-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: linear-gradient(135deg, #2563EB 0%, #7C3AED 100%);
        box-shadow: 0 0 8px rgba(124, 58, 237, 0.5);
        flex-shrink: 0;
    }

    .brain-name-text {
        font-family: 'Outfit', sans-serif;
        font-size: clamp(0.84rem, 1.2vw, 0.98rem);
        font-weight: 750;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        background: linear-gradient(135deg, #2563EB 0%, #7C3AED 52%, #EF4444 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 2px 8px rgba(124, 58, 237, 0.22));
        white-space: nowrap;
    }

    /* Mentor Appreciation Card (Sherin Miss) */
    .mentor-appreciation-card {
        background: linear-gradient(135deg, rgba(254, 252, 246, 0.96) 0%, rgba(255, 255, 255, 0.98) 50%, rgba(245, 243, 255, 0.96) 100%);
        border: 1px solid rgba(212, 175, 55, 0.45);
        border-radius: 13px;
        padding: clamp(6px, 1vh, 9px) clamp(12px, 1.8vw, 18px);
        box-shadow: 0 4px 16px -2px rgba(124, 58, 237, 0.06), 0 2px 6px -1px rgba(212, 175, 55, 0.08);
        max-width: min(580px, 92vw);
        margin: 0 auto clamp(8px, 1.4vh, 14px) auto;
        text-align: center;
        box-sizing: border-box;
        transition: all 0.25s ease;
    }

    .mentor-appreciation-card:hover {
        border-color: rgba(212, 175, 55, 0.7);
        box-shadow: 0 6px 20px -2px rgba(124, 58, 237, 0.1), 0 0 14px rgba(212, 175, 55, 0.15);
        transform: translateY(-1px);
    }

    .mentor-heading {
        font-family: 'Outfit', sans-serif;
        font-size: clamp(0.78rem, 1.1vw, 0.88rem);
        font-weight: 800;
        letter-spacing: 1.8px;
        text-transform: uppercase;
        background: linear-gradient(135deg, #B45309 0%, #7C3AED 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
    }

    .mentor-sparkle {
        color: #D4AF37;
        font-size: 0.7rem;
    }

    .mentor-quote {
        font-family: 'Outfit', sans-serif;
        font-size: clamp(0.76rem, 1vw, 0.86rem);
        font-style: italic;
        font-weight: 500;
        color: #334155;
        line-height: 1.4;
        margin: 0;
    }

    @keyframes brainFadeUp {
        0% {
            opacity: 0;
            transform: translateY(12px);
        }
        100% {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* Inputs and Selectbox Light Styles */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div {
        background-color: #FFFFFF !important;
        border: 1px solid var(--border-subtle) !important;
        color: var(--text-navy) !important;
        border-radius: 10px !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: var(--color-blue) !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15) !important;
    }

    /* Radio / Tabs custom */
    div[role="radiogroup"] {
        background: #F8FAFC;
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: 6px;
    }

    div[role="tablist"] {
        border-bottom: 1px solid var(--border-subtle);
    }

    button[role="tab"] {
        color: var(--text-secondary) !important;
        font-weight: 600 !important;
    }

    button[role="tab"][aria-selected="true"] {
        color: var(--color-blue) !important;
        border-bottom-color: var(--color-blue) !important;
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #F1F5F9;
    }
    ::-webkit-scrollbar-thumb {
        background: #CBD5E1;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #94A3B8;
    }
    </style>
    """

def clean_html(html_str: str) -> str:
    """
    Strips leading and trailing whitespace from every line.
    Prevents CommonMark from interpreting indented HTML lines as code blocks.
    """
    if not html_str:
        return ""
    return "\n".join(line.strip() for line in html_str.strip().splitlines())

def render_html(html_str: str):
    """
    Safely renders HTML via st.markdown without accidental code block formatting.
    """
    st.markdown(clean_html(html_str), unsafe_allow_html=True)

def render_kpi(label, value, subtext=None, border_color="#E2E8F0", is_gradient=False) -> str:
    """Render an elegant modern light KPI card as clean, unindented HTML."""
    sub_html = f'<div class="kpi-sub">{subtext}</div>' if subtext else ""
    val_class = "kpi-value kpi-value-gradient" if is_gradient else "kpi-value"
    raw = f"""<div class="glass-card" style="border-color: {border_color}; margin-bottom: 14px; padding: 18px 20px;">
<div class="kpi-container">
<div class="kpi-label">{label}</div>
<div class="{val_class}">{value}</div>
{sub_html}
</div>
</div>"""
    return clean_html(raw)

def render_progress_bar(percentage) -> str:
    """Render a modern blue-to-red gradient progress bar as clean, unindented HTML."""
    pct = max(0.0, min(100.0, float(percentage)))
    raw = f"""<div class="futuristic-progress-container"><div class="futuristic-progress-bar" style="width: {pct:.1f}%;"></div></div>"""
    return raw
