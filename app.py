"""
JalRakshak AI — Home Dashboard
AI-Powered Water Quality Monitoring, Risk Prediction and Early Warning System
"""

import streamlit as st
import pandas as pd
import os, sys

sys.path.insert(0, os.path.dirname(__file__))

from utils.data_processing import load_history
from utils.model_training import load_model

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="JalRakshak AI",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ---- brand colours ---- */
:root {
    --navy:  #0a2342;
    --teal:  #0d7377;
    --aqua:  #14a085;
    --light: #e8f4f8;
    --white: #ffffff;
    --warn:  #f0a500;
    --danger:#d64045;
    --ok:    #2ecc71;
}

/* ---- global typography ---- */
html, body, [class*="css"] { font-family: "Segoe UI", sans-serif; }

/* ---- sidebar ---- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--navy) 0%, #123459 100%);
}
[data-testid="stSidebar"] * { color: #cde8f0 !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stRadio label { color: #cde8f0 !important; }

/* ---- metric cards ---- */
.jr-card {
    background: var(--white);
    border-radius: 12px;
    padding: 20px 24px;
    box-shadow: 0 2px 8px rgba(10,35,66,.10);
    border-left: 5px solid var(--teal);
    margin-bottom: 16px;
}
.jr-card h3 { margin: 0 0 4px 0; font-size: 1.8rem; color: var(--navy); }
.jr-card p  { margin: 0; color: #5a7a8a; font-size: .9rem; }

/* ---- hero ---- */
.jr-hero {
    background: linear-gradient(135deg, var(--navy) 0%, var(--teal) 100%);
    border-radius: 16px;
    padding: 40px 48px;
    color: var(--white);
    margin-bottom: 28px;
}
.jr-hero h1 { font-size: 2.4rem; margin: 0 0 6px 0; letter-spacing: .5px; }
.jr-hero .tagline { font-size: 1.1rem; opacity: .85; margin: 0 0 16px 0; }
.jr-hero .intro   { font-size: .95rem; opacity: .80; max-width: 680px; }

/* ---- section headers ---- */
.jr-section-title {
    color: var(--navy);
    font-size: 1.2rem;
    font-weight: 700;
    border-bottom: 3px solid var(--teal);
    padding-bottom: 6px;
    margin-bottom: 18px;
}

/* ---- SDG badge ---- */
.sdg-box {
    background: linear-gradient(135deg, #1a73a7 0%, #0d7377 100%);
    border-radius: 12px;
    padding: 20px 24px;
    color: white;
}
.sdg-box h4 { margin: 0 0 8px 0; font-size: 1.1rem; }
.sdg-box p  { margin: 0; font-size: .88rem; opacity: .9; }

/* ---- nav buttons ---- */
.stButton > button {
    background: var(--teal);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 22px;
    font-size: .95rem;
    transition: background .2s;
    width: 100%;
}
.stButton > button:hover { background: var(--aqua); }

/* ---- status badge ---- */
.badge-ok     { background:#d4f7e5; color:#1a7a45; border-radius:20px; padding:2px 12px; font-size:.82rem; font-weight:600; }
.badge-warn   { background:#fff3cd; color:#856404; border-radius:20px; padding:2px 12px; font-size:.82rem; font-weight:600; }
.badge-danger { background:#fde8e9; color:#a71d2a; border-radius:20px; padding:2px 12px; font-size:.82rem; font-weight:600; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💧 JalRakshak AI")
    st.markdown("---")
    st.markdown("### Navigation")
    st.page_link("app.py",                           label="🏠 Home Dashboard")
    st.page_link("pages/1_Water_Assessment.py",       label="🔬 Water Assessment")
    st.page_link("pages/2_Dashboard.py",              label="📊 Analytics Dashboard")
    st.page_link("pages/3_Sample_History.py",         label="📂 Sample History")
    st.page_link("pages/4_Learn_About_Water.py",      label="📚 Learn About Water")
    st.markdown("---")
    st.markdown(
        "<small style='color:#8ab4c9;'>⚠️ Preliminary screening only.<br>"
        "Not a substitute for laboratory testing.</small>",
        unsafe_allow_html=True,
    )

# ── Load summary data ─────────────────────────────────────────────────────────
history_df = load_history()
total_samples  = len(history_df)
flagged        = int((history_df["prediction"] == "Flagged").sum()) if not history_df.empty else 0
last_status    = "—"
if not history_df.empty:
    last_status = history_df.iloc[-1].get("prediction", "—")

pipeline, metrics = load_model()
model_ready = pipeline is not None

# ── Hero section ──────────────────────────────────────────────────────────────
st.markdown("""
<div class='jr-hero'>
  <h1>💧 JalRakshak AI</h1>
  <p class='tagline'>Early Detection. Clear Insights. Safer Water.</p>
  <p class='intro'>
    An AI-powered water quality monitoring and preliminary risk screening system
    that uses machine learning to identify unusual parameter patterns and present
    understandable insights — supporting the pursuit of <strong>SDG 6: Clean Water
    and Sanitation</strong>.
  </p>
</div>
""", unsafe_allow_html=True)

# ── Summary metric cards ──────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""
    <div class='jr-card'>
        <h3>{total_samples}</h3>
        <p>🧪 Total Samples Analyzed</p>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class='jr-card' style='border-left-color:#d64045;'>
        <h3>{flagged}</h3>
        <p>⚠️ Samples Flagged for Review</p>
    </div>""", unsafe_allow_html=True)
with c3:
    badge_cls = "badge-ok" if last_status == "Acceptable" else ("badge-danger" if last_status == "Flagged" else "badge-warn")
    st.markdown(f"""
    <div class='jr-card' style='border-left-color:#f0a500;'>
        <h3><span class='{badge_cls}'>{last_status}</span></h3>
        <p>📋 Latest Analysis Result</p>
    </div>""", unsafe_allow_html=True)
with c4:
    model_text  = "✅ Ready" if model_ready else "🔄 Untrained"
    model_style = "border-left-color:#2ecc71;" if model_ready else ""
    st.markdown(f"""
    <div class='jr-card' style='{model_style}'>
        <h3 style='font-size:1.3rem;'>{model_text}</h3>
        <p>🤖 ML Model Status</p>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Main content layout ───────────────────────────────────────────────────────
left, right = st.columns([2, 1])

with left:
    st.markdown("<p class='jr-section-title'>About This System</p>", unsafe_allow_html=True)
    st.markdown("""
    **JalRakshak AI** is a preliminary water-quality screening tool designed to help
    communities, students, and environmental practitioners understand water-parameter
    measurements through the lens of machine learning.

    **What it does:**
    - Accepts water-quality measurements (pH, TDS, turbidity, etc.)
    - Runs a trained Random Forest or Decision Tree classifier
    - Flags parameters outside WHO / BIS reference guidelines
    - Provides plain-language explanations and recommended next steps
    - Stores analysis history for trend monitoring

    **Important limitations:**
    > 🔬 This tool provides *preliminary screening*, not a definitive assessment of
    > water safety. Results must be confirmed by an accredited laboratory.
    > The ML model is trained on a synthetic demonstration dataset and should not be
    > used for regulatory decisions.
    """)

    st.markdown("<p class='jr-section-title'>Quick-Start Guide</p>", unsafe_allow_html=True)
    steps = [
        ("🔬", "Water Assessment", "Enter your water-quality parameters and run the AI analysis."),
        ("📊", "Analytics Dashboard", "Explore charts, model metrics, and sample comparisons."),
        ("📂", "Sample History", "Browse, filter and download all analyzed records."),
        ("📚", "Learn About Water", "Understand parameters, guidelines and SDG 6."),
    ]
    for icon, title, desc in steps:
        st.markdown(f"**{icon} {title}** — {desc}")

with right:
    st.markdown("<p class='jr-section-title'>SDG 6 Alignment</p>", unsafe_allow_html=True)
    st.markdown("""
    <div class='sdg-box'>
        <h4>🌍 UN SDG 6 — Clean Water & Sanitation</h4>
        <p>
            JalRakshak AI supports <strong>SDG 6.1</strong> (universal safe drinking water)
            and <strong>SDG 6.3</strong> (improved water quality) by providing accessible,
            data-driven preliminary screening to communities that may lack laboratory infrastructure.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<p class='jr-section-title'>Module Access</p>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🔬 Assess Water"):
            st.switch_page("pages/1_Water_Assessment.py")
        if st.button("📂 History"):
            st.switch_page("pages/3_Sample_History.py")
    with col_b:
        if st.button("📊 Dashboard"):
            st.switch_page("pages/2_Dashboard.py")
        if st.button("📚 Learn"):
            st.switch_page("pages/4_Learn_About_Water.py")

    st.markdown("<br>", unsafe_allow_html=True)
    if not model_ready:
        st.info("The ML model has not been trained yet. Go to **Water Assessment** to trigger training.")
    else:
        best = metrics.get("best_model", "—")
        bres = metrics.get("all_results", {}).get(best, {})
        st.success(
            f"**Model:** {best.replace('_',' ').title()}  \n"
            f"**Accuracy:** {bres.get('accuracy','—')}  \n"
            f"**F1 Score:** {bres.get('f1','—')}"
        )

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<center><small style='color:#8a9aaa;'>"
    "JalRakshak AI &nbsp;|&nbsp; IBM BharatCares Internship Project &nbsp;|&nbsp; "
    "B.E. AI & Data Science &nbsp;|&nbsp; "
    "Preliminary screening only — not a substitute for laboratory testing."
    "</small></center>",
    unsafe_allow_html=True,
)
