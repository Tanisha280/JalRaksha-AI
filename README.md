# 💧 JalRakshak AI

**AI-Powered Water Quality Monitoring, Risk Prediction and Early Warning System**

> *Early Detection. Clear Insights. Safer Water.*

JalRakshak AI is a preliminary water-quality screening web application built with
Streamlit and Scikit-learn, developed as part of the **IBM BharatCares Internship**
programme. It supports **UN SDG 6 — Clean Water and Sanitation** by providing
machine-learning-based screening insights for water-quality parameters.

---

## ⚠️ Important Disclaimer

These results are a **preliminary automated screening only**. They do **not** confirm
that water is safe or unsafe to drink. A normal result is not a guarantee of safety.
Always verify with an accredited laboratory before making decisions about water consumption.

---

## 📋 Features

| Module | Description |
|--------|-------------|
| 🏠 Home Dashboard | Summary cards, project intro, SDG 6 alignment, quick navigation |
| 🔬 Water Assessment | Enter measurements, run ML model, view risk analysis |
| 📊 Analytics Dashboard | Model metrics, confusion matrix, parameter trends, scatter plots |
| 📂 Sample History | Browse, filter, search, and download analyzed records |
| 📚 Learn About Water | Parameter explanations, SDG 6 guide, ML limitations, lab testing info |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or later
- pip

### Installation

```bash
# 1. Clone or download the project
cd JalrakshakAi

# 2. (Recommended) Create a virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Run the application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

---

## 📂 Project Structure

```
JalrakshakAi/
├── app.py                          # Home dashboard (Streamlit entry point)
├── requirements.txt
├── README.md
├── data/
│   ├── water_quality.csv           # Synthetic demo dataset (auto-generated)
│   └── sample_history.csv          # Analysis history (created on first use)
├── models/
│   ├── jalrakshak_model.joblib     # Saved ML pipeline (created on first run)
│   └── model_metrics.joblib        # Saved model metrics
├── utils/
│   ├── __init__.py
│   ├── data_processing.py          # Dataset loading, cleaning, history I/O
│   ├── model_training.py           # ML pipeline training and inference
│   ├── risk_analysis.py            # Rule-based parameter screening
│   └── visualizations.py           # Plotly chart builders
├── pages/
│   ├── __init__.py
│   ├── 1_Water_Assessment.py       # Assessment form and results
│   ├── 2_Dashboard.py              # Analytics and model metrics
│   ├── 3_Sample_History.py         # History browser
│   └── 4_Learn_About_Water.py      # Educational content
└── assets/                         # Static assets (future use)
```

---

## 🤖 ML Pipeline

1. **Dataset**: Synthetic 1,500-sample demonstration dataset with realistic
   WHO/BIS-range parameter distributions (60% acceptable, 40% flagged).
   Missing values (~5%) are introduced to simulate real-world incompleteness.
2. **Preprocessing**: Median imputation → StandardScaler.
3. **Models**: Random Forest (120 estimators, max_depth=10) vs Decision Tree (max_depth=8).
4. **Split**: 80% train / 20% test, stratified.
5. **Selection**: Model with higher F1 score is saved.
6. **Prediction**: Returns class label + per-class probabilities.

> **Note**: The default model is trained on synthetic data. To use a real dataset,
> place a CSV file named `water_quality.csv` in the `data/` folder. The file must
> contain a `potability` column (1 = acceptable, 0 = flagged) and any subset of:
> `ph`, `hardness`, `tds`, `turbidity`, `conductivity`, `chloramines`,
> `sulfate`, `organic_carbon`, `trihalomethanes`.

---

## 🔬 Reference Thresholds

Parameter thresholds are sourced from:
- **WHO Guidelines for Drinking-water Quality** (4th edition, 2022)
- **BIS IS 10500:2012** (Indian Standard for Drinking Water)
- **US EPA** drinking water standards (for THMs and TOC)

These are reference guidelines used for rule-based screening only. Consult the
current applicable standards for your jurisdiction.

---

## 🌍 SDG 6 Alignment

| SDG Target | Contribution |
|---|---|
| **6.1** Universal safe drinking water | Free screening tool accessible without lab equipment |
| **6.3** Improve water quality | Flags parameters outside guidelines, encourages testing |
| **6.b** Community participation | Educates users on water parameters and actions |

---

## 🔮 Future Enhancements

The codebase is structured to support:
- IoT sensor integration (real-time MQTT data ingestion)
- Location-based monitoring with map visualizations
- Multilingual interface
- Automated email/SMS alerts for flagged samples
- Integration with government water-quality databases

> These are planned features and are not currently implemented.

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| streamlit | Web application framework |
| pandas | Data manipulation |
| numpy | Numerical computation |
| scikit-learn | ML pipeline (Random Forest, Decision Tree, Scaler) |
| plotly | Interactive charts |
| joblib | Model persistence |

---

## 👩‍💻 Author

Developed for the **IBM BharatCares Internship Programme**  
B.E. Artificial Intelligence and Data Science

---

## 📄 License

This project is submitted as an academic internship deliverable.
Not for commercial use or regulatory decision-making.
