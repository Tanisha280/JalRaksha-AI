"""
JalRakshak AI — Learn About Water Quality
Educational content covering parameters, guidelines, SDG 6 and ML limitations.
"""

import streamlit as st
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.data_processing import PARAMETER_THRESHOLDS

st.set_page_config(page_title="Learn About Water · JalRakshak AI", page_icon="📚", layout="wide")

st.markdown("""
<style>
:root { --navy:#0a2342; --teal:#0d7377; --aqua:#14a085; --light:#e8f4f8; }
html, body, [class*="css"] { font-family: "Segoe UI", sans-serif; }
[data-testid="stSidebar"] { background: linear-gradient(180deg,#0a2342 0%,#123459 100%); }
[data-testid="stSidebar"] * { color: #cde8f0 !important; }
.jr-section-title { color:#0a2342; font-size:1.15rem; font-weight:700;
    border-bottom:3px solid #0d7377; padding-bottom:5px; margin-bottom:16px; }
.param-card { background:#f0f8ff; border-radius:10px; padding:16px 20px;
    margin-bottom:12px; border-left:5px solid #0d7377; }
.param-card h4 { margin:0 0 6px 0; color:#0a2342; font-size:1rem; }
.param-card p  { margin:0; color:#444; font-size:.88rem; line-height:1.6; }
.sdg-card { background:linear-gradient(135deg,#1a73a7 0%,#0d7377 100%);
    border-radius:12px; padding:24px 28px; color:white; margin-bottom:16px; }
.sdg-card h3 { margin:0 0 10px 0; font-size:1.2rem; }
.sdg-card p  { margin:0; font-size:.9rem; opacity:.9; }
.warning-box { background:#fff8e1; border:1px solid #ffe082; border-radius:8px;
    padding:14px 18px; color:#5d4037; font-size:.9rem; }
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

st.markdown("## 📚 Learn About Water Quality")
st.markdown(
    "Understand what water-quality parameters mean, why monitoring matters, "
    "and how JalRakshak AI supports the UN's SDG 6 goal."
)

tab1, tab2, tab3, tab4 = st.tabs(
    ["🧪 Parameters", "🌍 SDG 6", "🤖 ML & Limitations", "🔬 Why Lab Testing"]
)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — Parameters
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    st.markdown("<p class='jr-section-title'>Key Water-Quality Parameters</p>", unsafe_allow_html=True)

    PARAM_EXPLANATIONS = {
        "ph": {
            "title": "pH",
            "what": (
                "pH is a measure of how acidic or alkaline water is, on a scale of 0–14. "
                "A pH of 7 is neutral; below 7 is acidic, above 7 is alkaline."
            ),
            "why": (
                "Water outside the 6.5–8.5 range can affect taste, corrode pipes (low pH) "
                "or form scale (high pH), and may indicate contamination."
            ),
            "safe": "6.5 – 8.5 (WHO / BIS IS 10500:2012)",
        },
        "hardness": {
            "title": "Hardness (mg/L as CaCO₃)",
            "what": (
                "Hardness reflects the concentration of dissolved calcium and magnesium. "
                "Hard water leaves scale deposits; very soft water may be corrosive."
            ),
            "why": (
                "No direct health-based limit, but high hardness causes scaling in pipes "
                "and appliances. BIS aesthetic limit is 300 mg/L."
            ),
            "safe": "≤ 300 mg/L (BIS aesthetic limit)",
        },
        "tds": {
            "title": "Total Dissolved Solids — TDS (mg/L)",
            "what": (
                "TDS is the total concentration of dissolved minerals, salts, and metals. "
                "It is a broad indicator of overall mineral content."
            ),
            "why": (
                "High TDS affects taste and may indicate the presence of harmful minerals. "
                "WHO palatability limit is 600 mg/L; BIS permissible limit is 500 mg/L."
            ),
            "safe": "≤ 500 mg/L (BIS) / 600 mg/L (WHO palatability)",
        },
        "turbidity": {
            "title": "Turbidity (NTU)",
            "what": (
                "Turbidity is the cloudiness of water caused by suspended particles "
                "such as sediment, algae or bacteria."
            ),
            "why": (
                "High turbidity can harbour pathogens and indicates inadequate treatment. "
                "WHO recommends ≤4 NTU at the point of delivery; ≤1 NTU is the treatment target."
            ),
            "safe": "≤ 4 NTU at point of delivery (WHO)",
        },
        "conductivity": {
            "title": "Conductivity (μS/cm)",
            "what": (
                "Electrical conductivity measures the ability of water to conduct electricity, "
                "which correlates with its dissolved ion concentration."
            ),
            "why": (
                "Very high conductivity can indicate contamination from industrial or "
                "agricultural runoff. An indicative aesthetic limit is ~1500 μS/cm."
            ),
            "safe": "≤ 1500 μS/cm (indicative aesthetic limit)",
        },
        "chloramines": {
            "title": "Chloramines (mg/L)",
            "what": (
                "Chloramines are disinfectants formed when chlorine reacts with ammonia. "
                "They are used as an alternative to free chlorine in water treatment."
            ),
            "why": (
                "Levels above the guideline may cause eye and nose irritation. "
                "WHO guideline for monochloramine is ≤3 mg/L."
            ),
            "safe": "≤ 3–4 mg/L (WHO / US EPA)",
        },
        "sulfate": {
            "title": "Sulfate (mg/L)",
            "what": (
                "Sulfate is a naturally occurring anion found in many minerals. "
                "It can enter water through dissolution of mineral deposits."
            ),
            "why": (
                "High concentrations cause a bitter or medicinal taste and may have "
                "a laxative effect. WHO aesthetic limit is 250 mg/L."
            ),
            "safe": "≤ 250 mg/L (WHO aesthetic limit)",
        },
        "organic_carbon": {
            "title": "Total Organic Carbon — TOC (mg/L)",
            "what": (
                "TOC measures the total amount of organic compounds in water. "
                "It is used as an indicator of organic contamination or treatment efficiency."
            ),
            "why": (
                "High TOC can indicate the presence of organic pollutants and may react "
                "with disinfectants to form harmful by-products. US EPA MCLG: ≤4 mg/L."
            ),
            "safe": "≤ 4 mg/L (US EPA MCLG for treated water)",
        },
        "trihalomethanes": {
            "title": "Trihalomethanes — THMs (μg/L)",
            "what": (
                "THMs are a group of disinfection by-products formed when chlorine reacts "
                "with organic matter. Common examples: chloroform, bromodichloromethane."
            ),
            "why": (
                "Long-term exposure to high THM levels is associated with health risks "
                "including bladder cancer. US EPA MCL: 80 μg/L total THMs."
            ),
            "safe": "≤ 80 μg/L total THMs (US EPA) / WHO guideline varies by compound",
        },
    }

    for key, info in PARAM_EXPLANATIONS.items():
        with st.expander(f"🔬 {info['title']}", expanded=False):
            st.markdown(f"""
            <div class='param-card'>
                <h4>What is it?</h4>
                <p>{info['what']}</p>
            </div>
            <div class='param-card' style='border-left-color:#14a085;'>
                <h4>Why does it matter?</h4>
                <p>{info['why']}</p>
            </div>
            <div class='param-card' style='border-left-color:#2ecc71;'>
                <h4>✅ Reference guideline</h4>
                <p>{info['safe']}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("""
    <div class='warning-box'>
        <strong>⚠️ Source note:</strong> Reference values are taken from the
        <em>WHO Guidelines for Drinking-water Quality (4th edition)</em> and
        <em>BIS IS 10500:2012</em>.  Always consult the current version of the
        applicable standards for your jurisdiction.
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — SDG 6
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown("<p class='jr-section-title'>UN Sustainable Development Goal 6</p>", unsafe_allow_html=True)

    st.markdown("""
    <div class='sdg-card'>
        <h3>🌍 SDG 6: Clean Water and Sanitation</h3>
        <p>
            The United Nations Sustainable Development Goal 6 calls for universal and equitable
            access to safe and affordable drinking water, adequate sanitation and hygiene for all
            by 2030. It also includes targets to improve water quality, substantially increase
            water-use efficiency, and protect water-related ecosystems.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### How JalRakshak AI Supports SDG 6")

    contributions = [
        ("SDG 6.1", "Universal access to safe drinking water",
         "JalRakshak AI provides a free, open-source preliminary screening tool that can be "
         "used without expensive laboratory equipment, lowering the barrier for communities "
         "to understand their water quality."),
        ("SDG 6.3", "Improve water quality",
         "By flagging parameters outside guideline thresholds and recommending follow-up "
         "testing, JalRakshak AI encourages timely reporting of potentially compromised "
         "water sources."),
        ("SDG 6.b", "Participation of local communities",
         "The educational module empowers community members to understand what water-quality "
         "parameters mean and what actions they can take, fostering informed local participation."),
    ]

    for target, title, description in contributions:
        st.markdown(f"""
        <div class='param-card'>
            <h4>📌 {target} — {title}</h4>
            <p>{description}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("#### Global Water Quality Challenge")
    st.markdown("""
    - Over **2 billion people** lack access to safely managed drinking water (UN, 2023).
    - Contaminated water and poor sanitation are linked to **485,000 diarrhoeal deaths** annually.
    - Climate change is increasing pressure on water resources worldwide.
    - Affordable, technology-enabled monitoring can help bridge the gap in low-resource settings.

    *Source: UN Water, WHO/UNICEF JMP 2023 Progress Report.*
    """)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — ML & Limitations
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    st.markdown("<p class='jr-section-title'>How the Machine Learning Model Works</p>", unsafe_allow_html=True)

    st.markdown("""
    #### ML Pipeline Overview

    JalRakshak AI uses a **supervised classification** approach:

    1. **Dataset**: A synthetic demonstration dataset (1,500 records) with realistic
       parameter ranges is generated if no real dataset is available.
    2. **Preprocessing**: Missing values are imputed using column medians.
       Features are scaled using `StandardScaler`.
    3. **Models trained**: Random Forest and Decision Tree classifiers are trained
       and evaluated.
    4. **Evaluation**: Accuracy, Precision, Recall, F1-score and Confusion Matrix
       are computed on a 20% held-out test set.
    5. **Best model**: The model with the higher F1 score is saved and used for
       new sample predictions.

    #### What the Prediction Means

    | Label | Meaning |
    |---|---|
    | **Acceptable (1)** | The sample's parameters are within a pattern the model associates with acceptable water; *not* proof of safety. |
    | **Flagged (0)** | The sample's parameters fall outside patterns associated with acceptable water; further investigation is recommended. |

    #### Rule-Based Screening

    In addition to the ML prediction, JalRakshak AI performs a **parameter-by-parameter
    rule check** against WHO / BIS reference thresholds.  This is independent of the ML
    model and provides an additional layer of transparency.
    """)

    st.markdown("<p class='jr-section-title'>Important Limitations</p>", unsafe_allow_html=True)

    limitations = [
        ("Training data", "The default model is trained on **synthetic data** with artificial patterns. "
         "It should not be used to make real-world water-safety decisions."),
        ("Binary classification", "The model outputs only 'Acceptable' or 'Flagged'. "
         "Real water quality exists on a continuum and involves many parameters not captured here."),
        ("Missing parameters", "If a parameter is not measured, the model imputes a median value, "
         "which may introduce inaccuracy."),
        ("No microbial analysis", "JalRakshak AI cannot detect bacteria (e.g. E. coli), viruses, "
         "or parasites, which are common causes of waterborne illness."),
        ("Threshold generalizability", "WHO guidelines are globally referenced but local regulatory "
         "limits may differ. Always apply the standards relevant to your jurisdiction."),
        ("Model drift", "The model does not update automatically. If water conditions change, "
         "retraining on updated data is necessary."),
    ]

    for title, text in limitations:
        st.markdown(f"""
        <div class='param-card' style='border-left-color:#d64045;'>
            <h4>⚠️ {title}</h4>
            <p>{text}</p>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — Why Lab Testing
# ─────────────────────────────────────────────────────────────────────────────
with tab4:
    st.markdown("<p class='jr-section-title'>Why Laboratory Testing Is Essential</p>", unsafe_allow_html=True)

    st.markdown("""
    JalRakshak AI is a **preliminary screening tool**, not a replacement for
    certified laboratory analysis.  Here is why laboratory testing remains essential:
    """)

    reasons = [
        ("🦠 Microbial contamination",
         "JalRakshak AI measures physical and chemical parameters only. "
         "Bacteria, viruses, and protozoa — which cause most acute waterborne diseases — "
         "require biological testing methods such as total coliform or E. coli counts."),
        ("⚗️ Heavy metals and trace contaminants",
         "Arsenic, lead, mercury, nitrates, pesticides and industrial chemicals require "
         "specialist analytical equipment (ICP-MS, HPLC) that is beyond the scope of "
         "any parameter-based screening app."),
        ("📜 Legal and regulatory compliance",
         "For water that will be supplied to the public or used in food production, "
         "compliance must be demonstrated by accredited laboratories using certified methods."),
        ("🎯 Accuracy of results",
         "Physical sensors and self-reported measurements carry measurement errors. "
         "Certified laboratories follow strict quality-assurance protocols to produce "
         "defensible analytical results."),
        ("🔄 When to seek laboratory testing",
         "Immediately if a child, elderly person, or immunocompromised individual uses "
         "the water; if the source has recently flooded or been near industrial activity; "
         "if any parameter is flagged; or if health symptoms are observed."),
    ]

    for title, body in reasons:
        with st.expander(title, expanded=False):
            st.markdown(body)

    st.markdown("""
    #### Finding an Accredited Laboratory in India

    - **Bureau of Indian Standards (BIS)**: [www.bis.gov.in](https://www.bis.gov.in)
    - **National Accreditation Board for Testing and Calibration Laboratories (NABL)**:
      [www.nabl-india.org](https://www.nabl-india.org)
    - **Central Pollution Control Board (CPCB)**: [www.cpcb.nic.in](https://www.cpcb.nic.in)
    - **State Pollution Control Boards**: Contact your respective state board.
    - **Jal Jeevan Mission water-testing laboratories**: Contact your district administration.

    > 💡 Many state governments provide subsidised or free water-quality testing
    > for rural households under the Jal Jeevan Mission programme.
    """)
