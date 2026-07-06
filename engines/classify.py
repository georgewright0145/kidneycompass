"""KDIGO 2024 CKD classification — deterministic, no model.

Grounded in spec/guidelines/kdigo_2024_classification.md and spec/classification_spec.md.
Maps (eGFR, ACR mg/mmol) -> KDIGO CGA category, risk band, and NICE monitoring frequency.
Every input is optional; the engine degrades gracefully and never invents a category.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# --- G axis: (inclusive lower bound, label). Checked high -> low. ---
_G_BANDS = [
    (90, "G1"),
    (60, "G2"),
    (45, "G3a"),
    (30, "G3b"),
    (15, "G4"),
    (0, "G5"),
]

# --- Risk heat-map: (g_category, a_category) -> band. From kdigo_2024_classification.md ---
_HEATMAP = {
    ("G1", "A1"): "green", ("G1", "A2"): "amber", ("G1", "A3"): "orange",
    ("G2", "A1"): "green", ("G2", "A2"): "amber", ("G2", "A3"): "orange",
    ("G3a", "A1"): "amber", ("G3a", "A2"): "orange", ("G3a", "A3"): "red",
    ("G3b", "A1"): "orange", ("G3b", "A2"): "red", ("G3b", "A3"): "red",
    ("G4", "A1"): "red", ("G4", "A2"): "red", ("G4", "A3"): "red",
    ("G5", "A1"): "red", ("G5", "A2"): "red", ("G5", "A3"): "red",
}

_SEVERE_G = {"G4", "G5"}


@dataclass
class Classification:
    g_category: str | None = None
    a_category: str | None = None
    risk_band: str | None = None
    monitoring_per_year: int | None = None
    meets_ckd_definition: bool = False
    notes: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)


def g_category(egfr: float | None) -> str | None:
    """eGFR (ml/min/1.73m^2) -> G category, inclusive of the lower bound."""
    if egfr is None:
        return None
    for lower, label in _G_BANDS:
        if egfr >= lower:
            return label
    return "G5"  # unreachable (0 bound), defensive


def a_category(acr_mg_mmol: float | None) -> str | None:
    """Urine ACR (mg/mmol, UK units) -> A category. A2 boundary inclusive; A3 strictly > 30."""
    if acr_mg_mmol is None:
        return None
    if acr_mg_mmol < 3:
        return "A1"
    if acr_mg_mmol <= 30:
        return "A2"
    return "A3"


def _monitoring_per_year(band: str | None, g_cat: str | None) -> int | None:
    if band is None:
        return None
    if band in ("green", "amber"):
        return 1
    if band == "orange":
        return 2
    # red: two or more; encode most-severe G4/G5 as 3 (the "3-4 at most severe" guidance)
    if band == "red":
        return 3 if g_cat in _SEVERE_G else 2
    return None


def classify(egfr: float | None, acr: float | None) -> Classification:
    """Classify against KDIGO. ACR is mg/mmol (UK units). Never invents from absent data."""
    c = Classification()
    if egfr is None:
        c.missing.append("egfr")
    if acr is None:
        c.missing.append("acr")

    c.g_category = g_category(egfr)
    c.a_category = a_category(acr)

    # Risk band (heat-map) requires BOTH axes.
    if c.g_category and c.a_category:
        c.risk_band = _HEATMAP[(c.g_category, c.a_category)]
        c.monitoring_per_year = _monitoring_per_year(c.risk_band, c.g_category)
    else:
        if c.g_category and not c.a_category:
            c.notes.append(
                "Only eGFR available: classified on the G axis. A urine ACR (mg/mmol) is needed "
                "to place you on the full KDIGO risk heat-map — worth asking your GP for one."
            )
        elif c.a_category and not c.g_category:
            c.notes.append(
                "Only ACR available: classified on the A axis. An eGFR is needed for the full "
                "KDIGO risk heat-map."
            )
        else:
            c.notes.append("No eGFR or ACR provided — nothing to classify yet.")

    # CKD definition: eGFR < 60 OR ACR >= 3 (sustained > 3 months). A1 + eGFR >= 60 does not meet it.
    meets = (egfr is not None and egfr < 60) or (acr is not None and acr >= 3)
    c.meets_ckd_definition = bool(meets)
    if meets:
        c.notes.append(
            "These values meet the CKD definition only if sustained for more than 3 months — "
            "a single result is not a diagnosis."
        )
    elif egfr is not None and acr is not None:
        c.notes.append(
            "These values (eGFR 60 or above with a normal ACR) do not by themselves meet the CKD "
            "definition."
        )

    if c.a_category is not None:
        c.notes.append("ACR is shown in UK units (mg/mmol).")

    return c
