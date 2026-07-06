"""KFRE (UK-recalibrated 4-variable) — deterministic, no model.

Grounded in spec/guidelines/kfre.md and spec/kfre_spec.md.

HARD GATE: the UK recalibration constants (Major et al. 2019) are NOT yet supplied. Until
UK_KFRE_CONSTANTS is populated (by the user, clinician-verified), this engine REFUSES to compute
and returns status="constants_unavailable". A wrong risk number is worse than an honest refusal —
do NOT invent constants.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# UK recalibration constants — TO BE SUPPLIED BY THE USER (clinician-verified).
# Expected keys once provided (4-variable Tangri model, UK-recalibrated):
#   {
#     "s0_2yr": <baseline survival at 2 years>,
#     "s0_5yr": <baseline survival at 5 years>,
#     "coef_age": ..., "coef_sex_male": ..., "coef_egfr": ..., "coef_acr_ln": ...,
#     "mean_centering": {...},  # if the calibration centres the linear predictor
#   }
# Leave as None to keep the engine in its safe refuse-to-compute state.
# ---------------------------------------------------------------------------
UK_KFRE_CONSTANTS: dict | None = None

# ACR unit conversion (mg/mmol -> mg/g) for the published equation; activated only once constants
# exist and is unit-tested then. See spec/kfre_spec.md ("safety-critical step").
_MG_MMOL_TO_MG_G = 8.8403

VALID_WHATIFS = ["egfr", "acr"]

_STANDARD_CAVEATS = [
    "KFRE does not account for the competing risk of death and can overestimate risk in older or "
    "frailer people.",
    "eGFR and ACR vary from day to day, so the trend over time matters more than any single value.",
]


@dataclass
class KfreResult:
    status: str  # "ok" | "constants_unavailable" | "not_applicable" | "unstable_value"
    risk_2yr: float | None = None
    risk_5yr: float | None = None
    inputs_echo: dict = field(default_factory=dict)
    caveats: list[str] = field(default_factory=list)
    valid_whatifs: list[str] = field(default_factory=lambda: list(VALID_WHATIFS))


def kfre_risk(
    age: float | None,
    sex: str | None,
    egfr: float | None,
    acr_mg_mmol: float | None,
    *,
    suspected_aki: bool = False,
) -> KfreResult:
    """Estimate 2/5-year kidney-failure risk (UK-calibrated 4-variable KFRE).

    Refuses on unstable/AKI values, on eGFR >= 60 (not applicable to G3a-G5 only), on missing
    inputs, and — in the current state — whenever the UK constants have not been supplied.
    """
    echo = {"age": age, "sex": sex, "egfr": egfr, "acr_mg_mmol": acr_mg_mmol}

    # 1. Never run on unstable / suspected-AKI values.
    if suspected_aki:
        return KfreResult(
            status="unstable_value",
            inputs_echo=echo,
            caveats=["This value looks unstable (possible acute kidney injury), so a kidney-failure "
                     "risk estimate would be misleading and has not been calculated."],
        )

    # 2. Applicability: KFRE is for CKD stages G3a-G5 (eGFR < 60) with all four inputs present.
    missing = [n for n, v in (("age", age), ("sex", sex), ("egfr", egfr), ("acr", acr_mg_mmol)) if v is None]
    if missing:
        return KfreResult(
            status="not_applicable",
            inputs_echo=echo,
            caveats=[f"A KFRE estimate needs age, sex, eGFR and ACR; missing: {', '.join(missing)}."],
        )
    if egfr >= 60:
        return KfreResult(
            status="not_applicable",
            inputs_echo=echo,
            caveats=["KFRE applies to CKD stages G3a-G5 (eGFR below 60). At your eGFR it is not "
                     "applicable."],
        )

    # 3. HARD GATE: refuse to compute until UK constants are supplied.
    if UK_KFRE_CONSTANTS is None:
        return KfreResult(
            status="constants_unavailable",
            inputs_echo=echo,
            caveats=["The UK-calibrated KFRE constants have not been loaded yet, so no risk number "
                     "is shown. A clinician-verified UK calculation is pending — this is deliberate: "
                     "an unverified number would be worse than none."] + _STANDARD_CAVEATS,
        )

    # 4. Compute (only reachable once UK_KFRE_CONSTANTS is populated and validated by tests).
    risk_2yr, risk_5yr = _compute(age, sex, egfr, acr_mg_mmol, UK_KFRE_CONSTANTS)
    return KfreResult(
        status="ok",
        risk_2yr=risk_2yr,
        risk_5yr=risk_5yr,
        inputs_echo=echo,
        caveats=list(_STANDARD_CAVEATS),
    )


def _compute(age, sex, egfr, acr_mg_mmol, k: dict) -> tuple[float, float]:
    """4-variable Tangri linear predictor with UK recalibration. Inert until constants exist."""
    acr_mg_g = acr_mg_mmol * _MG_MMOL_TO_MG_G
    lp = (
        k["coef_age"] * age
        + k["coef_sex_male"] * (1.0 if str(sex).lower().startswith("m") else 0.0)
        + k["coef_egfr"] * egfr
        + k["coef_acr_ln"] * math.log(acr_mg_g)
    )
    centre = k.get("mean_centering_lp", 0.0)
    risk_2yr = 1.0 - k["s0_2yr"] ** math.exp(lp - centre)
    risk_5yr = 1.0 - k["s0_5yr"] ** math.exp(lp - centre)
    return risk_2yr, risk_5yr
