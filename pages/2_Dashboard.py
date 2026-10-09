"""
JalRakshak AI — Analytics Dashboard
Model metrics, parameter distributions, trend analysis.
"""

import streamlit as st
import pandas as pd
import numpy as np
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.data_processing import load_history, PARAMETER_THRESHOLDS
from utils.model_training import get_or_train_model, train_and_evaluate
from utils.visualizations import (
    confusion_matrix_chart, model_comparison_chart,
    history_trend_chart, prediction_distribution_chart,
    parameter_distribution_chart, scatter_comparison_chart,
)

st.set_page_config(page_title="Analytics Dashboard · JalRakshak AI", page_icon="📊", layout="wide")

st.markdown("""
<style>
:root { --navy:#0a2342; --teal:#0d7377; }
html, body, [class*="css"] { font-family: "Segoe UI", sans-serif; }
[data-testid="stSidebar"] { background: linear-gradient(180deg,#0a2342 0%,#123459 100%); }
[data-testid="stSidebar"] * { color: #cde8f0 !important; }
.jr-section-title { color:#0a2342; font-size:1.15rem; font-weight:700;
    border-bottom:3px solid #0d7377; padding-bottom:5px; margin-bottom:16px; }
.metric-chip { background:#e8f4f8; border-radius:10px; padding:14px 18px;
    text-align:center; margin-bottom:10px; }
.metric-chip h2 { color:#0a2342; margin:0; font-size:1.9rem; }
.metric-chip p  { color:#5a7a8a; margin:0; font-size:.85rem; }
.stButton > button { background:#0d7377; color:white; border:none; border-radius:8px;
    padding:8px 18px; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 💧 JalRakshak AI")
    st.markdown("---")
    st.page_link("app.py",                       label="🏠 Home Dashboard")
    st.page_link("pages/1_Water_Assessment.py",   label="🔬 Water Assessment")
    st.page_link("pages/2_Dashboard.py",          label="📊 Analytics Dashboard")
    st.page_link("pages/3_Sample_History.py",     label="📂 Sample History")
    st.page_link("pages/4_Learn_About_Water.py",  label="📚 Learn About Water")

st.markdown("## 📊 Analytics Dashboard")

# ── Load data ─────────────────────────────────────────────────────────────────
history_df = load_history()
pipeline, metrics = get_or_train_model()

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(
    ["🤖 Model Performance", "📈 Parameter Trends", "🔍 Sample Comparisons", "📦 Data Overview"]
)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — Model Performance
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    if metrics is None:
        st.info("No trained model found. Use Water Assessment to trigger training.")
    else:
        best = metrics["best_model"]
        all_res = metrics["all_results"]
        best_res = all_res[best]

        st.markdown("<p class='jr-section-title'>Best Model Summary</p>", unsafe_allow_html=True)
        m1, m2, m3, m4, m5 = st.columns(5)
        for col, (name, val) in zip(
            [m1, m2, m3, m4, m5],
            [
                ("Accuracy",  best_res["accuracy"]),
                ("Precision", best_res["precision"]),
                ("Recall",    best_res["recall"]),
                ("F1 Score",  best_res["f1"]),
                ("Train Size",best_res["n_train"]),
            ],
        ):
            with col:
                st.markdown(f"""
                <div class='metric-chip'>
                    <h2>{val if isinstance(val,int) else f'{val:.3f}'}</h2>
                    <p>{name}</p>
                </div>""", unsafe_allow_html=True)

        st.markdown(
            f"<small>Best model: **{best.replace('_',' ').title()}** "
            f"| Test samples: {best_res['n_test']} "
            f"| ⚠️ Trained on synthetic demo data — not real-world validated</small>",
            unsafe_allow_html=True,
        )

        col_cm, col_cmp = st.columns(2)
        with col_cm:
            st.plotly_chart(
                confusion_matrix_chart(best_res["confusion_matrix"]),
                width="stretch",
            )
        with col_cmp:
            st.plotly_chart(
                model_comparison_chart(all_res),
                width="stretch",
            )

        st.markdown("<p class='jr-section-title'>Classification Report</p>", unsafe_allow_html=True)
        st.code(best_res["classification_report"], language=None)

        st.markdown("<p class='jr-section-title'>Retrain Model</p>", unsafe_allow_html=True)
        st.markdown(
            "Click to retrain on the current dataset. "
            "Existing model file will be overwritten."
        )
        if st.button("🔄 Retrain Model"):
            with st.spinner("Training…"):
                new_metrics = train_and_evaluate()
            st.success("Model retrained successfully!")
            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — Parameter Trends
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    PARAM_LABELS = {
        "ph": "pH", "hardness": "Hardness (mg/L)", "tds": "TDS (mg/L)",
        "turbidity": "Turbidity (NTU)", "conductivity": "Conductivity (μS/cm)",
        "chloramines": "Chloramines (mg/L)", "sulfate": "Sulfate (mg/L)",
        "organic_carbon": "TOC (mg/L)", "trihalomethanes": "THMs (μg/L)",
    }

    if history_df.empty:
        st.info("No sample history yet. Analyse some samples in **Water Assessment** first.")
    else:
        st.markdown("<p class='jr-section-title'>Trend Over Time</p>", unsafe_allow_html=True)
        avail = [p for p in PARAM_LABELS if p in history_df.columns]
        chosen = st.selectbox("Select parameter to plot over time:", avail,
                              format_func=lambda p: PARAM_LABELS[p])
        st.plotly_chart(
            history_trend_chart(history_df, chosen, PARAM_LABELS[chosen]),
            width="stretch",
        )

        st.markdown("<p class='jr-section-title'>Distribution</p>", unsafe_allow_html=True)
        dist_param = st.selectbox("Select parameter for distribution:", avail,
                                  format_func=lambda p: PARAM_LABELS[p], key="dist_sel")
        st.plotly_chart(
            parameter_distribution_chart(history_df, dist_param, PARAM_LABELS[dist_param]),
            width="stretch",
        )

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — Sample Comparisons
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    PARAM_LABELS_FULL = {
        "ph": "pH", "hardness": "Hardness (mg/L)", "tds": "TDS (mg/L)",
        "turbidity": "Turbidity (NTU)", "conductivity": "Conductivity (μS/cm)",
        "chloramines": "Chloramines (mg/L)", "sulfate": "Sulfate (mg/L)",
        "organic_carbon": "TOC (mg/L)", "trihalomethanes": "THMs (μg/L)",
    }

    if history_df.empty:
        st.info("No sample history yet.")
    else:
        avail_cmp = [p for p in PARAM_LABELS_FULL if p in history_df.columns]
        st.markdown("<p class='jr-section-title'>Scatter Comparison</p>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            x_col = st.selectbox("X-axis:", avail_cmp,
                                 format_func=lambda p: PARAM_LABELS_FULL[p])
        with c2:
            y_default = avail_cmp[1] if len(avail_cmp) > 1 else avail_cmp[0]
            y_col = st.selectbox("Y-axis:", avail_cmp,
                                 index=avail_cmp.index(y_default),
                                 format_func=lambda p: PARAM_LABELS_FULL[p])
        st.plotly_chart(
            scatter_comparison_chart(
                history_df, x_col, y_col,
                PARAM_LABELS_FULL[x_col], PARAM_LABELS_FULL[y_col],
            ),
            width="stretch",
        )

        st.markdown("<p class='jr-section-title'>Prediction Distribution</p>", unsafe_allow_html=True)
        st.plotly_chart(prediction_distribution_chart(history_df), width="stretch")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — Data Overview
# ─────────────────────────────────────────────────────────────────────────────
with tab4:
    from utils.data_processing import load_dataset, clean_dataset

    st.markdown("<p class='jr-section-title'>Training Dataset Overview</p>", unsafe_allow_html=True)

    with st.spinner("Loading dataset…"):
        raw_df = load_dataset()
        clean  = clean_dataset(raw_df)

    is_synthetic = "data_source" in raw_df.columns and (raw_df["data_source"] == "SYNTHETIC_DEMO").all()
    if is_synthetic:
        st.warning(
            "⚠️ Using **synthetic demonstration dataset**. "
            "Place a real `water_quality.csv` in the `data/` folder to use real data."
        )
    else:
        st.success("Real dataset loaded from `data/water_quality.csv`.")

    c_a, c_b, c_c = st.columns(3)
    c_a.metric("Total Records",  len(raw_df))
    c_b.metric("After Cleaning", len(clean))
    c_c.metric("Features",       len([c for c in clean.columns if c not in ("potability","data_source")]))

    st.markdown("<p class='jr-section-title'>Sample Records</p>", unsafe_allow_html=True)
    st.dataframe(raw_df.head(20), width="stretch")

    st.markdown("<p class='jr-section-title'>Descriptive Statistics</p>", unsafe_allow_html=True)
    numeric_df = clean.select_dtypes(include=[np.number])
    st.dataframe(numeric_df.describe().round(3), width="stretch")
