"""
Visualization helpers for JalRakshak AI.
All charts use Plotly and return fig objects for st.plotly_chart().
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# Brand palette
NAVY   = "#0a2342"
TEAL   = "#0d7377"
AQUA   = "#14a085"
LIGHT  = "#e8f4f8"
WHITE  = "#ffffff"
WARN   = "#f0a500"
DANGER = "#d64045"
OK     = "#2ecc71"


def _base_layout(title: str = "", height: int = 380) -> dict:
    return dict(
        title=dict(text=title, font=dict(size=15, color=NAVY), x=0.02),
        height=height,
        paper_bgcolor=WHITE,
        plot_bgcolor=LIGHT,
        font=dict(family="Segoe UI, sans-serif", size=12, color=NAVY),
        margin=dict(l=40, r=20, t=50, b=40),
    )


# ---------------------------------------------------------------------------
# Parameter gauge / bar chart
# ---------------------------------------------------------------------------

def parameter_status_chart(flags: list) -> go.Figure:
    """Horizontal bar chart showing each parameter value vs its safe range."""
    if not flags:
        return go.Figure()

    labels = [f["label"] for f in flags]
    values = [f["value"] for f in flags]
    maxes  = [f["max"]   for f in flags]
    colors = [OK if f["status"] == "normal" else (WARN if f["status"] == "low" else DANGER)
              for f in flags]

    fig = go.Figure()
    # Safe-range bar (background)
    fig.add_trace(go.Bar(
        name="Safe Range Max",
        y=labels,
        x=maxes,
        orientation="h",
        marker_color="rgba(13,115,119,0.12)",
        showlegend=True,
    ))
    # Actual value bar
    fig.add_trace(go.Bar(
        name="Measured Value",
        y=labels,
        x=values,
        orientation="h",
        marker_color=colors,
        text=[f"{v:.2f}" for v in values],
        textposition="outside",
        showlegend=True,
    ))

    fig.update_layout(
        **_base_layout("Parameter Values vs Safe Range Maxima", height=420),
        barmode="overlay",
        xaxis_title="Value",
        legend=dict(orientation="h", y=-0.15),
    )
    return fig


# ---------------------------------------------------------------------------
# Radar chart
# ---------------------------------------------------------------------------

def radar_chart(flags: list) -> go.Figure:
    """Normalized radar chart (0 = min, 1 = max of safe range)."""
    if not flags:
        return go.Figure()

    categories = [f["label"] for f in flags]
    # Normalize: value / safe_max  (clipped to [0, 1.5] for visibility)
    normalized = []
    for f in flags:
        mx = f["max"] if f["max"] != 0 else 1
        normalized.append(min(f["value"] / mx, 1.5))

    categories_closed = categories + [categories[0]]
    normalized_closed = normalized + [normalized[0]]
    safe_line = [1.0] * len(categories_closed)

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=safe_line, theta=categories_closed,
        fill="toself", fillcolor="rgba(46,204,113,0.12)",
        line=dict(color=OK, dash="dash"), name="Safe Limit (1.0)",
    ))
    fig.add_trace(go.Scatterpolar(
        r=normalized_closed, theta=categories_closed,
        fill="toself", fillcolor="rgba(13,115,119,0.30)",
        line=dict(color=TEAL, width=2), name="Sample",
    ))
    fig.update_layout(
        polar=dict(
            bgcolor=LIGHT,
            radialaxis=dict(visible=True, range=[0, 1.6], tickfont=dict(size=10)),
        ),
        **_base_layout("Normalised Parameter Profile", height=420),
        showlegend=True,
    )
    return fig


# ---------------------------------------------------------------------------
# Confusion matrix heatmap
# ---------------------------------------------------------------------------

def confusion_matrix_chart(cm: list) -> go.Figure:
    labels = ["Flagged (0)", "Acceptable (1)"]
    z = np.array(cm)
    fig = go.Figure(go.Heatmap(
        z=z, x=labels, y=labels,
        colorscale=[[0, WHITE], [1, TEAL]],
        text=z, texttemplate="%{text}",
        showscale=False,
    ))
    fig.update_layout(
        **_base_layout("Confusion Matrix (Test Set)", height=320),
        xaxis_title="Predicted",
        yaxis_title="Actual",
    )
    return fig


# ---------------------------------------------------------------------------
# Model comparison bar chart
# ---------------------------------------------------------------------------

def model_comparison_chart(all_results: dict) -> go.Figure:
    metrics = ["accuracy", "precision", "recall", "f1"]
    labels  = [m.capitalize() for m in metrics]

    fig = go.Figure()
    colors_list = [TEAL, AQUA, WARN, NAVY]
    for i, (name, res) in enumerate(all_results.items()):
        vals = [res[m] for m in metrics]
        fig.add_trace(go.Bar(
            name=name.replace("_", " ").title(),
            x=labels, y=vals,
            marker_color=colors_list[i % len(colors_list)],
            text=[f"{v:.3f}" for v in vals],
            textposition="outside",
        ))
    fig.update_layout(
        **_base_layout("Model Comparison — Test-Set Metrics", height=380),
        barmode="group",
        yaxis=dict(range=[0, 1.1], title="Score"),
        legend=dict(orientation="h", y=-0.2),
    )
    return fig


# ---------------------------------------------------------------------------
# History / trend charts
# ---------------------------------------------------------------------------

def history_trend_chart(df: pd.DataFrame, param: str, label: str) -> go.Figure:
    """Line chart of a parameter over time from history DataFrame."""
    if df.empty or param not in df.columns:
        return go.Figure()
    d = df.dropna(subset=[param, "timestamp"]).sort_values("timestamp")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=d["timestamp"], y=d[param],
        mode="lines+markers",
        line=dict(color=TEAL, width=2),
        marker=dict(size=6, color=TEAL),
        name=label,
    ))
    fig.update_layout(**_base_layout(f"{label} Over Time", height=320))
    fig.update_xaxes(title="Date / Time")
    fig.update_yaxes(title=label)
    return fig


def prediction_distribution_chart(df: pd.DataFrame) -> go.Figure:
    """Pie chart of prediction categories in history."""
    if df.empty or "prediction" not in df.columns:
        return go.Figure()
    counts = df["prediction"].value_counts()
    labels = counts.index.tolist()
    values = counts.values.tolist()
    color_map = {"Acceptable": OK, "Flagged": DANGER}
    colors_pie = [color_map.get(l, TEAL) for l in labels]
    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        marker=dict(colors=colors_pie),
        hole=0.4,
    ))
    fig.update_layout(**_base_layout("Prediction Distribution", height=320))
    return fig


def parameter_distribution_chart(df: pd.DataFrame, param: str, label: str) -> go.Figure:
    """Histogram of a parameter across all history records."""
    if df.empty or param not in df.columns:
        return go.Figure()
    d = df[param].dropna()
    fig = go.Figure(go.Histogram(
        x=d, nbinsx=30,
        marker_color=TEAL, opacity=0.8,
    ))
    fig.update_layout(**_base_layout(f"{label} Distribution", height=300))
    fig.update_xaxes(title=label)
    fig.update_yaxes(title="Count")
    return fig


def scatter_comparison_chart(df: pd.DataFrame, x_col: str, y_col: str,
                              x_label: str, y_label: str) -> go.Figure:
    """Scatter chart comparing two parameters, coloured by prediction."""
    if df.empty:
        return go.Figure()
    color_col = "prediction" if "prediction" in df.columns else None
    color_map = {"Acceptable": OK, "Flagged": DANGER}
    colors = [color_map.get(str(v), TEAL) for v in df.get(color_col, [TEAL] * len(df))]
    fig = go.Figure(go.Scatter(
        x=df.get(x_col), y=df.get(y_col),
        mode="markers",
        marker=dict(color=colors, size=7, opacity=0.7),
        text=df.get("sample_id", None),
        hovertemplate=f"{x_label}: %{{x}}<br>{y_label}: %{{y}}<extra></extra>",
    ))
    fig.update_layout(**_base_layout(f"{x_label} vs {y_label}", height=340))
    fig.update_xaxes(title=x_label)
    fig.update_yaxes(title=y_label)
    return fig
