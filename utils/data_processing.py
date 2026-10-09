"""
Data processing utilities for JalRakshak AI.
Handles dataset loading, cleaning, and synthetic data generation.
"""

import pandas as pd
import numpy as np
import os

# ---------------------------------------------------------------------------
# WHO / BIS reference thresholds (guideline values, not regulatory limits)
# Source: WHO Guidelines for Drinking-water Quality (4th ed.)
#         BIS IS 10500:2012
# ---------------------------------------------------------------------------
PARAMETER_THRESHOLDS = {
    "ph": {
        "unit": "dimensionless",
        "min": 6.5,
        "max": 8.5,
        "who_note": "WHO acceptable range: 6.5–8.5",
    },
    "hardness": {
        "unit": "mg/L as CaCO₃",
        "min": 0,
        "max": 300,
        "who_note": "No WHO health-based guideline; 300 mg/L aesthetic limit (BIS)",
    },
    "tds": {
        "unit": "mg/L",
        "min": 0,
        "max": 500,
        "who_note": "WHO palatability limit: 600 mg/L; BIS permissible: 500 mg/L",
    },
    "turbidity": {
        "unit": "NTU",
        "min": 0,
        "max": 4,
        "who_note": "WHO guideline: ≤4 NTU at point of delivery",
    },
    "conductivity": {
        "unit": "μS/cm",
        "min": 0,
        "max": 1500,
        "who_note": "Indicative aesthetic limit ~1500 μS/cm",
    },
    "chloramines": {
        "unit": "mg/L",
        "min": 0,
        "max": 4,
        "who_note": "WHO guideline: ≤3 mg/L (monochloramine)",
    },
    "sulfate": {
        "unit": "mg/L",
        "min": 0,
        "max": 250,
        "who_note": "WHO aesthetic limit: 250 mg/L",
    },
    "organic_carbon": {
        "unit": "mg/L",
        "min": 0,
        "max": 4,
        "who_note": "US EPA MCLG: ≤4 mg/L TOC in treated water",
    },
    "trihalomethanes": {
        "unit": "μg/L",
        "min": 0,
        "max": 80,
        "who_note": "WHO guideline for total THMs: 0.3 mg/L (CHCl3 equivalent); US EPA: 80 μg/L",
    },
}

DATASET_PATH = os.path.join("data", "water_quality.csv")
HISTORY_PATH = os.path.join("data", "sample_history.csv")

HISTORY_COLUMNS = [
    "sample_id", "timestamp", "ph", "hardness", "tds", "turbidity",
    "conductivity", "chloramines", "sulfate", "organic_carbon",
    "trihalomethanes", "prediction", "confidence_pct", "flags", "followup",
]


# ---------------------------------------------------------------------------
# Dataset helpers
# ---------------------------------------------------------------------------

def generate_synthetic_dataset(n_samples: int = 1500, seed: int = 42) -> pd.DataFrame:
    """
    Generate a clearly labelled synthetic water-quality dataset with realistic
    parameter ranges for software testing and demonstration.

    IMPORTANT: This dataset is synthetic and must NOT be used to draw
    conclusions about real-world water safety.
    """
    rng = np.random.default_rng(seed)

    # Most samples are 'acceptable' (potability=1); minority are 'flagged' (0)
    n_acceptable = int(n_samples * 0.60)
    n_flagged = n_samples - n_acceptable

    def _acceptable():
        return {
            "ph":              rng.uniform(6.5, 8.5,  n_acceptable),
            "hardness":        rng.uniform(60,  250,  n_acceptable),
            "tds":             rng.uniform(100, 490,  n_acceptable),
            "turbidity":       rng.uniform(0.1, 3.8,  n_acceptable),
            "conductivity":    rng.uniform(200, 1400, n_acceptable),
            "chloramines":     rng.uniform(0.2, 3.8,  n_acceptable),
            "sulfate":         rng.uniform(30,  240,  n_acceptable),
            "organic_carbon":  rng.uniform(0.5, 3.8,  n_acceptable),
            "trihalomethanes": rng.uniform(5,   75,   n_acceptable),
            "potability":      np.ones(n_acceptable, dtype=int),
        }

    def _flagged():
        return {
            "ph":              np.concatenate([
                                   rng.uniform(2.0, 6.4, n_flagged // 2),
                                   rng.uniform(8.6, 12.0, n_flagged - n_flagged // 2)]),
            "hardness":        rng.uniform(301, 600, n_flagged),
            "tds":             rng.uniform(501, 1200, n_flagged),
            "turbidity":       rng.uniform(4.1, 25,  n_flagged),
            "conductivity":    rng.uniform(1501, 3000, n_flagged),
            "chloramines":     rng.uniform(4.1, 10,  n_flagged),
            "sulfate":         rng.uniform(251, 600, n_flagged),
            "organic_carbon":  rng.uniform(4.1, 20,  n_flagged),
            "trihalomethanes": rng.uniform(81,  250, n_flagged),
            "potability":      np.zeros(n_flagged, dtype=int),
        }

    acc = _acceptable()
    flg = _flagged()

    df = pd.concat([
        pd.DataFrame(acc),
        pd.DataFrame(flg),
    ], ignore_index=True)

    # Introduce ~5% missing values to simulate real-world incompleteness
    for col in df.columns:
        if col == "potability":
            continue
        mask = rng.random(len(df)) < 0.05
        df.loc[mask, col] = np.nan

    df = df.sample(frac=1, random_state=seed).reset_index(drop=True)
    df.insert(0, "data_source", "SYNTHETIC_DEMO")
    return df


def load_dataset() -> pd.DataFrame:
    """Load dataset from CSV; fall back to synthetic data if not found."""
    if os.path.exists(DATASET_PATH):
        df = pd.read_csv(DATASET_PATH)
        # Normalize column names
        df.columns = [c.lower().strip().replace(" ", "_") for c in df.columns]
        if "potability" in df.columns or "is_safe" in df.columns:
            if "is_safe" in df.columns and "potability" not in df.columns:
                df.rename(columns={"is_safe": "potability"}, inplace=True)
            return df
    # Fall back to synthetic
    return generate_synthetic_dataset()


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows missing the target; impute feature NaNs with column medians."""
    df = df.copy()
    if "potability" in df.columns:
        df = df.dropna(subset=["potability"])
    # Impute numeric columns with median
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    for col in numeric_cols:
        if col == "potability":
            continue
        median_val = df[col].median()
        df[col] = df[col].fillna(median_val)
    return df


def get_feature_columns(df: pd.DataFrame) -> list:
    exclude = {"potability", "data_source", "sample_id", "timestamp"}
    return [c for c in df.columns if c not in exclude and df[c].dtype != object]


# ---------------------------------------------------------------------------
# Sample history helpers
# ---------------------------------------------------------------------------

def load_history() -> pd.DataFrame:
    if os.path.exists(HISTORY_PATH):
        return pd.read_csv(HISTORY_PATH, parse_dates=["timestamp"])
    return pd.DataFrame(columns=HISTORY_COLUMNS)


def save_to_history(record: dict):
    """Append a single analysis record to the history CSV."""
    df = load_history()
    new_row = pd.DataFrame([record])
    df = pd.concat([df, new_row], ignore_index=True)
    os.makedirs("data", exist_ok=True)
    df.to_csv(HISTORY_PATH, index=False)


def next_sample_id() -> str:
    df = load_history()
    n = len(df) + 1
    return f"JR-{n:04d}"
