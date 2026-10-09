"""
Rule-based risk analysis for JalRakshak AI.
Flags parameters outside WHO / BIS reference thresholds and generates
human-readable explanations and recommended follow-up actions.

DISCLAIMER: Results are a preliminary screening aid only.  They do NOT
constitute proof that water is safe or unsafe to drink.  Always confirm
with accredited laboratory testing.
"""

from utils.data_processing import PARAMETER_THRESHOLDS

PARAMETER_LABELS = {
    "ph":              "pH",
    "hardness":        "Hardness",
    "tds":             "Total Dissolved Solids (TDS)",
    "turbidity":       "Turbidity",
    "conductivity":    "Conductivity",
    "chloramines":     "Chloramines",
    "sulfate":         "Sulfate",
    "organic_carbon":  "Total Organic Carbon",
    "trihalomethanes": "Trihalomethanes (THMs)",
}


def screen_parameters(values: dict) -> list:
    """
    Compare each provided measurement against reference thresholds.

    Returns a list of flag dicts:
        {param, label, value, unit, min, max, status, note, explanation}

    status is one of: 'normal', 'low', 'high'
    Only parameters present in PARAMETER_THRESHOLDS are evaluated.
    """
    flags = []
    for param, value in values.items():
        if param not in PARAMETER_THRESHOLDS or value is None:
            continue
        ref = PARAMETER_THRESHOLDS[param]
        lo, hi = ref["min"], ref["max"]
        label = PARAMETER_LABELS.get(param, param.title())

        if value < lo:
            status = "low"
            explanation = (
                f"{label} of {value:.2f} {ref['unit']} is below the "
                f"acceptable lower limit of {lo} {ref['unit']}. "
                f"{ref['who_note']}."
            )
        elif value > hi:
            status = "high"
            explanation = (
                f"{label} of {value:.2f} {ref['unit']} exceeds the "
                f"acceptable upper limit of {hi} {ref['unit']}. "
                f"{ref['who_note']}."
            )
        else:
            status = "normal"
            explanation = (
                f"{label} of {value:.2f} {ref['unit']} is within the "
                f"acceptable range ({lo}–{hi} {ref['unit']}). "
                f"{ref['who_note']}."
            )

        flags.append({
            "param":       param,
            "label":       label,
            "value":       value,
            "unit":        ref["unit"],
            "min":         lo,
            "max":         hi,
            "status":      status,
            "note":        ref["who_note"],
            "explanation": explanation,
        })
    return flags


def build_followup_advice(flags: list, ml_prediction: int | None = None) -> list:
    """
    Return a list of plain-language recommended follow-up actions based on
    flagged parameters and (optionally) the ML prediction.
    """
    advice = []
    flagged_params = [f for f in flags if f["status"] != "normal"]

    if not flagged_params and ml_prediction in (None, 1):
        advice.append(
            "No parameters are outside reference ranges in this preliminary "
            "screening.  However, laboratory testing is still recommended to "
            "confirm water quality."
        )
        return advice

    if ml_prediction == 0:
        advice.append(
            "⚠️ The ML model indicates this sample may require further review.  "
            "This is a preliminary result — please consult an accredited laboratory."
        )

    for f in flagged_params:
        p = f["param"]
        if p == "ph":
            advice.append(
                "pH is out of range.  Acidic water may corrode pipes; alkaline water "
                "may cause scaling.  Have the source tested by a certified laboratory."
            )
        elif p == "turbidity":
            advice.append(
                "Elevated turbidity can indicate suspended particles or microbial "
                "contamination.  Boiling or certified filtration is advised pending "
                "laboratory analysis."
            )
        elif p == "tds":
            advice.append(
                "High TDS may affect taste and indicate dissolved salts or metals.  "
                "Reverse-osmosis filtration may help; confirm with laboratory testing."
            )
        elif p == "chloramines":
            advice.append(
                "Chloramine levels outside the guideline range.  Contact your water "
                "utility or local health authority for guidance."
            )
        elif p == "trihalomethanes":
            advice.append(
                "THM levels above reference value.  THMs are disinfection by-products "
                "associated with long-term health risks at high concentrations.  "
                "Seek laboratory confirmation and contact the water authority."
            )
        elif p in ("sulfate", "hardness", "conductivity", "organic_carbon"):
            advice.append(
                f"{f['label']} is outside the reference range.  "
                "Laboratory analysis is recommended to determine the cause."
            )

    advice.append(
        "📋 Important: These results are for preliminary screening only and do NOT "
        "replace accredited laboratory testing.  Contact your local water authority "
        "or public health department if you have concerns about your water supply."
    )
    return list(dict.fromkeys(advice))  # deduplicate while preserving order


def summarise_flags(flags: list) -> dict:
    total   = len(flags)
    normal  = sum(1 for f in flags if f["status"] == "normal")
    flagged = total - normal
    return {"total": total, "normal": normal, "flagged": flagged}
