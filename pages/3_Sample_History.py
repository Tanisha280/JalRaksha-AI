"""
JalRakshak AI — Sample History
Browse, filter, search and download all analyzed water-quality records.
"""

import streamlit as st
import pandas as pd
import numpy as np
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.data_processing import load_history, HISTORY_PATH

st.set_page_config(page_title="Sample History · JalRakshak AI", page_icon="📂", layout="wide")

st.markdown("""
<style>
:root { --navy:#0a2342; --teal:#0d7377; }
html, body, [class*="css"] { font-family: "Segoe UI", sans-serif; }
[data-testid="stSidebar"] { background: linear-gradient(180deg,#0a2342 0%,#123459 100%); }
[data-testid="stSidebar"] * { color: #cde8f0 !important; }
.jr-section-title { color:#0a2342; font-size:1.15rem; font-weight:700;
    border-bottom:3px solid #0d7377; padding-bottom:5px; margin-bottom:16px; }
.stButton > button { background:#0d7377; color:white; border:none; border-radius:8px;
    padding:8px 18px; }
.badge-ok     { background:#d4f7e5; color:#1a7a45; border-radius:20px;
    padding:2px 10px; font-size:.8rem; font-weight:600; }
.badge-danger { background:#fde8e9; color:#a71d2a; border-radius:20px;
    padding:2px 10px; font-size:.8rem; font-weight:600; }
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

st.markdown("## 📂 Sample History")

df = load_history()

if df.empty:
    st.info(
        "No samples have been analyzed yet. "
        "Go to **Water Assessment** to analyze your first sample."
    )
    st.stop()

# ── Summary metrics ───────────────────────────────────────────────────────────
st.markdown("<p class='jr-section-title'>Summary</p>", unsafe_allow_html=True)
total     = len(df)
flagged   = int((df["prediction"] == "Flagged").sum())
accept    = int((df["prediction"] == "Acceptable").sum())

m1, m2, m3 = st.columns(3)
m1.metric("Total Samples",   total)
m2.metric("Acceptable",      accept)
m3.metric("Flagged",         flagged)

# ── Filters ───────────────────────────────────────────────────────────────────
st.markdown("<p class='jr-section-title'>Filter Records</p>", unsafe_allow_html=True)

fcol1, fcol2, fcol3 = st.columns(3)

with fcol1:
    pred_filter = st.multiselect(
        "Prediction",
        options=df["prediction"].dropna().unique().tolist(),
        default=df["prediction"].dropna().unique().tolist(),
    )

with fcol2:
    search_id = st.text_input("Search by Sample ID", placeholder="e.g. JR-0001")

with fcol3:
    if "timestamp" in df.columns and not df["timestamp"].dropna().empty:
        try:
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
            min_date = df["timestamp"].min().date()
            max_date = df["timestamp"].max().date()
            date_range = st.date_input(
                "Date range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
            )
        except Exception:
            date_range = None
    else:
        date_range = None

# Apply filters
filtered = df.copy()
if pred_filter:
    filtered = filtered[filtered["prediction"].isin(pred_filter)]
if search_id:
    filtered = filtered[
        filtered["sample_id"].astype(str).str.contains(search_id, case=False, na=False)
    ]
if date_range and len(date_range) == 2:
    try:
        start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
        filtered = filtered[
            (filtered["timestamp"] >= start) & (filtered["timestamp"] <= end)
        ]
    except Exception:
        pass

st.markdown(f"Showing **{len(filtered)}** of **{total}** records.")

# ── Data table ────────────────────────────────────────────────────────────────
st.markdown("<p class='jr-section-title'>Records</p>", unsafe_allow_html=True)

display_cols = [c for c in filtered.columns if c in [
    "sample_id", "timestamp", "prediction", "confidence_pct",
    "ph", "hardness", "tds", "turbidity", "conductivity",
    "chloramines", "sulfate", "organic_carbon", "trihalomethanes",
    "flags", "followup",
]]
display_df = filtered[display_cols].copy()

# Colour-code prediction column using Styler
def _colour_pred(val):
    if val == "Flagged":
        return "background-color:#fde8e9; color:#a71d2a; font-weight:600;"
    elif val == "Acceptable":
        return "background-color:#d4f7e5; color:#1a7a45; font-weight:600;"
    return ""

prediction_styles = display_df.style
if hasattr(prediction_styles, "map"):
    prediction_styles = prediction_styles.map(_colour_pred, subset=["prediction"])
else:
    prediction_styles = prediction_styles.applymap(_colour_pred, subset=["prediction"])
styled = prediction_styles.format(na_rep="—", precision=2)
st.dataframe(styled, width="stretch", height=420)

# ── Download ──────────────────────────────────────────────────────────────────
st.markdown("<p class='jr-section-title'>Download</p>", unsafe_allow_html=True)

csv_bytes = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Download Filtered Records as CSV",
    data=csv_bytes,
    file_name="jalrakshak_sample_history.csv",
    mime="text/csv",
    width="content",
)

# ── Detail expander ───────────────────────────────────────────────────────────
st.markdown("<p class='jr-section-title'>Sample Detail View</p>", unsafe_allow_html=True)

sample_ids = filtered["sample_id"].dropna().tolist()
if sample_ids:
    chosen_id = st.selectbox("Select a sample to view details:", sample_ids)
    row = filtered[filtered["sample_id"] == chosen_id].iloc[0]

    detail_col1, detail_col2 = st.columns(2)
    with detail_col1:
        st.markdown(f"**Sample ID:** {row.get('sample_id', '—')}")
        st.markdown(f"**Timestamp:** {row.get('timestamp', '—')}")
        st.markdown(f"**Prediction:** {row.get('prediction', '—')}")
        st.markdown(f"**Confidence:** {row.get('confidence_pct', '—')}%")
    with detail_col2:
        st.markdown(f"**Flags:** {row.get('flags', 'None')}")
        st.markdown(f"**Follow-up:** {row.get('followup', '—')}")

    param_labels = {
        "ph": "pH", "hardness": "Hardness (mg/L)", "tds": "TDS (mg/L)",
        "turbidity": "Turbidity (NTU)", "conductivity": "Conductivity (μS/cm)",
        "chloramines": "Chloramines (mg/L)", "sulfate": "Sulfate (mg/L)",
        "organic_carbon": "TOC (mg/L)", "trihalomethanes": "THMs (μg/L)",
    }
    param_rows = []
    for key, label in param_labels.items():
        val = row.get(key, np.nan)
        if pd.notna(val):
            param_rows.append({"Parameter": label, "Measured Value": round(float(val), 3)})
    if param_rows:
        st.dataframe(pd.DataFrame(param_rows), width="stretch", hide_index=True)
