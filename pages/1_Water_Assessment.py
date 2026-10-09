"""
JalRakshak AI — Water Quality Assessment
Enter measurements, run the ML pipeline, and view the risk analysis.
"""

import streamlit as st
import pandas as pd
import numpy as np
import os, sys, datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.data_processing import (
    PARAMETER_THRESHOLDS, save_to_history, next_sample_id,
)
from utils.model_training import get_or_train_model, predict_sample
from utils.risk_analysis import screen_parameters, build_followup_advice, summarise_flags
from utils.visualizations import parameter_status_chart, radar_chart

st.set_page_config(page_title="Water Assessment · JalRakshak AI", page_icon="🔬", layout="wide")

# Shared CSS
st.markdown("""
<style>
:root { --navy:#0a2342; --teal:#0d7377; --aqua:#14a085; --light:#e8f4f8; }
html, body, [class*="css"] { font-family: "Segoe UI", sans-serif; }
[data-testid="stSidebar"] { background: linear-gradient(180deg,#0a2342 0%,#123459 100%); }
[data-testid="stSidebar"] * { color: #cde8f0 !important; }
.jr-section-title { color:#0a2342; font-size:1.15rem; font-weight:700;
    border-bottom:3px solid #0d7377; padding-bottom:5px; margin-bottom:16px; }
.result-card { border-radius:12px; padding:20px 24px; margin-bottom:14px; }
.result-ok   { background:#d4f7e5; border-left:6px solid #2ecc71; }
.result-warn { background:#fde8e9; border-left:6px solid #d64045; }
.flag-row    { padding:10px 14px; border-radius:8px; margin-bottom:8px; font-size:.9rem; }
.flag-normal { background:#eafaf1; border-left:4px solid #2ecc71; }
.flag-high   { background:#fde8e9; border-left:4px solid #d64045; }
.flag-low    { background:#fff3cd; border-left:4px solid #f0a500; }
.stButton > button { background:#0d7377; color:white; border:none; border-radius:8px;
    padding:10px 22px; width:100%; }
.stButton > button:hover { background:#14a085; }
.disclaimer { background:#fff8e1; border:1px solid #ffe082; border-radius:8px;
    padding:12px 16px; font-size:.85rem; color:#5d4037; margin-top:12px; }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## 💧 JalRakshak AI")
    st.markdown("---")
    st.page_link("app.py",                       label="🏠 Home Dashboard")
    st.page_link("pages/1_Water_Assessment.py",   label="🔬 Water Assessment")
    st.page_link("pages/2_Dashboard.py",          label="📊 Analytics Dashboard")
    st.page_link("pages/3_Sample_History.py",     label="📂 Sample History")
    st.page_link("pages/4_Learn_About_Water.py",  label="📚 Learn About Water")

# Page header
st.markdown("## 🔬 Water Quality Assessment")
st.markdown(
    "Enter the available water-quality measurements below. "
    "All fields are optional — only parameters you provide will be analysed. "
    "Results are a **preliminary screening** — not a laboratory assessment."
)

# ── Step 1: Parameter input ───────────────────────────────────────────────────
st.markdown("<p class='jr-section-title'>Step 1 — Enter Measurements</p>", unsafe_allow_html=True)

PARAM_META = {
    "ph":              {"label": "pH",                              "unit": "(dimensionless)", "min_v": 0.0,  "max_v": 14.0, "default": 7.2},
    "hardness":        {"label": "Hardness",                        "unit": "mg/L",            "min_v": 0.0,  "max_v": 800.0,"default": 180.0},
    "tds":             {"label": "Total Dissolved Solids (TDS)",    "unit": "mg/L",            "min_v": 0.0,  "max_v": 2000.0,"default":300.0},
    "turbidity":       {"label": "Turbidity",                       "unit": "NTU",             "min_v": 0.0,  "max_v": 100.0,"default": 1.5},
    "conductivity":    {"label": "Conductivity",                    "unit": "μS/cm",           "min_v": 0.0,  "max_v": 5000.0,"default":450.0},
    "chloramines":     {"label": "Chloramines",                     "unit": "mg/L",            "min_v": 0.0,  "max_v": 15.0, "default": 2.0},
    "sulfate":         {"label": "Sulfate",                         "unit": "mg/L",            "min_v": 0.0,  "max_v": 1000.0,"default":150.0},
    "organic_carbon":  {"label": "Total Organic Carbon (TOC)",      "unit": "mg/L",            "min_v": 0.0,  "max_v": 50.0, "default": 2.0},
    "trihalomethanes": {"label": "Trihalomethanes (THMs)",          "unit": "μg/L",            "min_v": 0.0,  "max_v": 500.0,"default":50.0},
}

col_sel, col_form = st.columns([1, 2])

with col_sel:
    st.markdown("**Select parameters available for this sample:**")
    selected_params = {}
    for key, meta in PARAM_META.items():
        if st.checkbox(f"{meta['label']} ({meta['unit']})", value=True, key=f"chk_{key}"):
            selected_params[key] = meta

with col_form:
    if not selected_params:
        st.warning("Please select at least one parameter.")
        st.stop()

    user_values = {}
    errors = {}

    st.markdown("**Enter measured values:**")
    grid_cols = st.columns(2)
    for idx, (key, meta) in enumerate(selected_params.items()):
        with grid_cols[idx % 2]:
            val = st.number_input(
                f"{meta['label']} ({meta['unit']})",
                min_value=meta["min_v"],
                max_value=meta["max_v"],
                value=meta["default"],
                step=0.01,
                key=f"input_{key}",
                help=PARAMETER_THRESHOLDS.get(key, {}).get("who_note", ""),
            )
            user_values[key] = val

# ── Step 2: Analyse ───────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
run_col, _ = st.columns([1, 3])
with run_col:
    run_analysis = st.button("🚀 Run AI Analysis", width="stretch")

if run_analysis:
    st.markdown("---")
    st.markdown("<p class='jr-section-title'>Step 2 — AI Analysis Results</p>", unsafe_allow_html=True)

    # Load / train model
    with st.spinner("Loading ML model (this may take ~30 s on first run)…"):
        pipeline, metrics = get_or_train_model()

    if pipeline is None:
        st.error("Could not load or train the ML model. Check console for errors.")
        st.stop()

    feature_columns = metrics["feature_columns"]

    # Only pass parameters the model was trained on
    model_input = {k: user_values.get(k, np.nan) for k in feature_columns}

    # ML prediction
    prediction, confidence, proba = predict_sample(pipeline, model_input, feature_columns)
    pred_label = "Acceptable" if prediction == 1 else "Flagged"

    # Rule-based screening
    flags = screen_parameters(user_values)
    flag_summary = summarise_flags(flags)
    followup = build_followup_advice(flags, ml_prediction=prediction)

    # ── Result card ──────────────────────────────────────────────────────────
    card_cls = "result-ok" if prediction == 1 else "result-warn"
    icon     = "✅" if prediction == 1 else "⚠️"
    res_col1, res_col2 = st.columns([1, 1])

    with res_col1:
        st.markdown(f"""
        <div class='result-card {card_cls}'>
            <h3 style='margin:0 0 8px 0;'>{icon} ML Prediction: {pred_label}</h3>
            <p style='margin:0 0 4px 0;'>
                <strong>Model confidence:</strong> {confidence*100:.1f}%
                &nbsp;|&nbsp;
                <strong>Acceptable probability:</strong> {proba['acceptable']*100:.1f}%
                &nbsp;|&nbsp;
                <strong>Flagged probability:</strong> {proba['flagged']*100:.1f}%
            </p>
            <p style='margin:4px 0 0 0; font-size:.84rem; color:#555;'>
                Model: {metrics['best_model'].replace('_',' ').title()}
                &nbsp;|&nbsp; Trained on synthetic demonstration data
            </p>
        </div>
        """, unsafe_allow_html=True)

    with res_col2:
        st.markdown(f"""
        <div class='result-card' style='background:#e8f4f8; border-left:6px solid #0d7377;'>
            <h3 style='margin:0 0 8px 0;'>🔍 Parameter Screening</h3>
            <p style='margin:0;'>
                <strong>{flag_summary['total']}</strong> parameter(s) checked
                &nbsp;|&nbsp;
                <strong style='color:#2ecc71;'>{flag_summary['normal']}</strong> normal
                &nbsp;|&nbsp;
                <strong style='color:#d64045;'>{flag_summary['flagged']}</strong> flagged
            </p>
        </div>
        """, unsafe_allow_html=True)

    # ── Charts ───────────────────────────────────────────────────────────────
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.plotly_chart(parameter_status_chart(flags), width="stretch")
    with chart_col2:
        if len(flags) >= 3:
            st.plotly_chart(radar_chart(flags), width="stretch")

    # ── Parameter-by-parameter breakdown ─────────────────────────────────────
    st.markdown("<p class='jr-section-title'>Parameter Details</p>", unsafe_allow_html=True)
    for f in flags:
        css_cls = f"flag-{f['status']}"
        icon_map = {"normal": "✅", "high": "🔴", "low": "🟡"}
        st.markdown(
            f"<div class='flag-row {css_cls}'>"
            f"<strong>{icon_map.get(f['status'],'ℹ️')} {f['label']}</strong>: "
            f"{f['explanation']}"
            f"</div>",
            unsafe_allow_html=True,
        )

    # ── Follow-up advice ──────────────────────────────────────────────────────
    st.markdown("<p class='jr-section-title'>Recommended Follow-up</p>", unsafe_allow_html=True)
    for advice in followup:
        st.markdown(f"- {advice}")

    # ── Disclaimer ────────────────────────────────────────────────────────────
    st.markdown("""
    <div class='disclaimer'>
        ⚠️ <strong>Disclaimer:</strong> These results are a preliminary automated screening
        and do <em>not</em> confirm that the water is safe or unsafe to drink. A normal
        result is <em>not</em> a guarantee of safety. Always verify with an accredited
        laboratory before making decisions about water consumption.
    </div>
    """, unsafe_allow_html=True)

    # ── Save to history ───────────────────────────────────────────────────────
    flagged_params_list = ", ".join(
        [f["label"] for f in flags if f["status"] != "normal"]
    ) or "None"

    record = {
        "sample_id":      next_sample_id(),
        "timestamp":      datetime.datetime.now().isoformat(timespec="seconds"),
        "prediction":     pred_label,
        "confidence_pct": round(confidence * 100, 1),
        "flags":          flagged_params_list,
        "followup":       followup[0] if followup else "",
    }
    for key in PARAM_META:
        record[key] = user_values.get(key, np.nan)

    save_to_history(record)
    st.success(f"✅ Sample **{record['sample_id']}** saved to history.")
