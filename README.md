# MARKNOVA • Academic Performance Dashboard
> *Clarity in Every Score.*

MARKNOVA is a production-quality, futuristic academic performance analytics web application built specifically for the students and faculty of **College of Engineering Chengannur, Electrical and Electronics Engineering (EEE), Semester 1**.

The platform ingests series assessment marksheet PDFs, dynamically parses and validates student scores, and presents actionable academic intelligence through a premium, modern light-mode SaaS analytics dashboard with clean white backgrounds, sophisticated dark navy/brown typography, and selective blue-to-red gradient text.

---

## ⚡ Core Highlights

- **Pure Python & Streamlit Engine**: Runs completely locally with zero external JavaScript frameworks.
- **Dynamic PyMuPDF Extraction**: Extracts roll numbers, student names, and assessment columns (A1–A6) with 100% mathematical fidelity.
- **Assessment Combination**: Automatically unites A5 and A6 (max 20 each) into **GXEST104** (max 40).
- **Data Integrity & Validation**: Distinguishes between explicit `AB` (absent) entries and blank cells, checks bounds, verifies calculated totals against source totals, and flags anomalies.
- **Competition Class Ranking**: Ranks students dynamically based on overall descending percentage using competition ranking (`1, 2, 2, 4`), visible exclusively inside the student profile.
- **Strict Privacy Guidelines**: No public ranking leaderboards, Top 2, Top 3, Top 10 lists, grade distribution histograms, or fail reports. The directory is sorted strictly by roll number.
- **Sleek Intro Splash Flow**: Two-stage animated splash screen showcasing MARKNOVA branding ("Clarity in Every Score") followed by the **BRAIN BEHIND** creators showcase (`AABIS MUHAMMED`, `AARON GEORGE`, `AARON JOSEPH`, `ABHIMANYU KEVIN`) and the developer photo (`assets/pop.png`).
- **Export & Reporting Engine**: Generates comprehensive Class Analysis PDFs, structured Student CSVs, and individual Student Report PDFs using ReportLab.

---

## 📂 Project Architecture

```
MARKNOVA/
├── app.py                   # Main Streamlit router, splash state machine & views
├── pdf_processor.py         # PyMuPDF coordinate-based extraction & schema mapping
├── data_manager.py          # Data ingestion, integrity checks & session persistence
├── analysis.py              # Pure calculation engine (averages, toppers, competition ranks)
├── student_profiles.py      # Student roll grid & individual student profile UI
├── charts.py                # Modern light SaaS Plotly charts (averages, radars, benchmarks)
├── report_generator.py      # ReportLab PDF generator (Class & Student) + CSV export
├── styles.py                # Light SaaS theme, gradient typography, KPI cards & progress bars
├── requirements.txt         # Production dependencies
├── assets/
│   ├── marknova_logo.png    # Official fairytale brand logo
│   ├── favicon_64.png       # Derived open-book browser favicon
│   └── pop.png              # Developer photo (transparent PNG)
├── data/                    # Directory for user marksheet PDFs
├── reports/                 # Output directory for generated reports
└── README.md                # Comprehensive documentation
```

---

## 🚀 Installation & Execution

### 1. Prerequisites
- Python 3.9+ installed on your system.

### 2. Environment Setup
```bash
# Clone or navigate to the project directory
cd /path/to/ATP

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On macOS/Linux
# .venv\Scripts\activate   # On Windows

# Install production dependencies
pip install -r requirements.txt
```

### 3. Launching MARKNOVA
```bash
streamlit run app.py
```
Open your browser to `http://localhost:8501`.

---

## 📋 Assessment & Subject Structure

The platform maps the six assessment columns from the marksheet to the five accredited semester subjects:

| Column | Maximum | Mapped Subject Code | Course Title |
| :---: | :---: | :---: | :--- |
| **A1** | 40 | `GYMAT101` | Mathematics for Electrical Science and Physical Science - 1 |
| **A2** | 40 | `UCEST105` | Algorithmic Thinking with Python |
| **A3** | 40 | `GXCYT122` | Chemistry for Information Science and Electrical Science |
| **A4** | 40 | `GMEST103` | Engineering Graphics and Computer Aided Drawing |
| **A5 + A6** | 20 + 20 = 40 | `GXEST104` | Introduction to Electrical and Electronics Engineering |

**Total Score**: 200 Marks.

---

## 🛡️ Analytical Policies & Exclusions

In accordance with academic privacy standards:
1. **Directory Ordering**: Student cards are ordered strictly by Roll Number.
2. **Rank Display**: Individual class rank is revealed only upon opening a specific student's profile.
3. **Excluded Analytics**: Top 10, Top 3, Top 2 lists, public leaderboards, grade distribution graphs, and fail lists are completely excluded from the application.
