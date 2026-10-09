"""
Model training utilities for JalRakshak AI.
Trains, evaluates, saves and loads the classification pipeline.
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, classification_report,
)

from utils.data_processing import load_dataset, clean_dataset, get_feature_columns

MODEL_PATH = os.path.join("models", "jalrakshak_model.joblib")
METRICS_PATH = os.path.join("models", "model_metrics.joblib")


def build_pipeline(model_name: str = "random_forest") -> Pipeline:
    if model_name == "decision_tree":
        clf = DecisionTreeClassifier(max_depth=8, random_state=42)
    else:
        clf = RandomForestClassifier(
            n_estimators=120, max_depth=10, random_state=42, n_jobs=-1
        )
    return Pipeline([
        ("scaler", StandardScaler()),
        ("clf", clf),
    ])


def train_and_evaluate():
    """
    Full training run: load → clean → split → train two models → evaluate.
    Saves the better model and returns a metrics dict.
    """
    df = load_dataset()
    df = clean_dataset(df)

    feature_cols = get_feature_columns(df)
    X = df[feature_cols].values
    y = df["potability"].values.astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    results = {}
    for name in ("random_forest", "decision_tree"):
        pipe = build_pipeline(name)
        pipe.fit(X_train, y_train)
        y_pred = pipe.predict(X_test)
        results[name] = {
            "pipeline": pipe,
            "accuracy":  round(accuracy_score(y_test, y_pred), 4),
            "precision": round(precision_score(y_test, y_pred, zero_division=0), 4),
            "recall":    round(recall_score(y_test, y_pred, zero_division=0), 4),
            "f1":        round(f1_score(y_test, y_pred, zero_division=0), 4),
            "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
            "classification_report": classification_report(
                y_test, y_pred,
                target_names=["Flagged (0)", "Acceptable (1)"],
                zero_division=0,
            ),
            "feature_columns": feature_cols,
            "n_train": len(X_train),
            "n_test":  len(X_test),
        }

    # Pick the model with higher F1 score
    best_name = max(results, key=lambda k: results[k]["f1"])
    best_result = results[best_name]

    os.makedirs("models", exist_ok=True)
    joblib.dump(best_result["pipeline"], MODEL_PATH)

    metrics = {
        "best_model": best_name,
        "all_results": {k: {m: v for m, v in r.items() if m != "pipeline"}
                        for k, r in results.items()},
        "feature_columns": feature_cols,
    }
    joblib.dump(metrics, METRICS_PATH)
    return metrics


def load_model():
    """Load the saved model pipeline.  Returns (pipeline, metrics) or (None, None)."""
    if os.path.exists(MODEL_PATH) and os.path.exists(METRICS_PATH):
        pipeline = joblib.load(MODEL_PATH)
        metrics  = joblib.load(METRICS_PATH)
        return pipeline, metrics
    return None, None


def get_or_train_model():
    """Load existing model or train a fresh one."""
    pipeline, metrics = load_model()
    if pipeline is None:
        metrics  = train_and_evaluate()
        pipeline, _ = load_model()
    return pipeline, metrics


def predict_sample(pipeline, feature_values: dict, feature_columns: list):
    """
    Predict potability for a single sample.

    Returns:
        prediction (int): 0 = flagged, 1 = acceptable
        confidence (float): probability of predicted class (0–1)
        proba (dict): {'flagged': float, 'acceptable': float}
    """
    row = np.array([[feature_values.get(c, np.nan) for c in feature_columns]])
    prediction = int(pipeline.predict(row)[0])
    probas = pipeline.predict_proba(row)[0]
    # classes_ order: [0, 1]
    proba_dict = {
        "flagged":    round(float(probas[0]), 4),
        "acceptable": round(float(probas[1]), 4),
    }
    confidence = probas[prediction]
    return prediction, float(confidence), proba_dict
