"""KFRE (UK-recalibrated 4-variable) — deterministic, no model.

Grounded in spec/guidelines/kfre.md and spec/kfre_spec.md.

Coefficients & centering: the original Tangri 4-variable KFRE, transcribed from the ukidney.com KFRE
calculator's JavaScript source (a real source, not model memory). UK recalibration: the coefficients
are held fixed as a linear-predictor offset and the baseline survival S0 is re-estimated on the UK
Major et al. 2019 (PLoS Medicine) cohort via the Breslow estimator — see spec/kfre_recalibration/.
Validated on that cohort: Harrell's C = 0.930; the derived UK S0 (higher than the non-UK Tangri
values) matches the published finding that non-UK calibrations overestimate UK risk.

If UK_KFRE_CONSTANTS is set to None the engine REFUSES to compute (status="constants_unavailable").
A wrong risk number is worse than an honest refusal.

STATUS: constants derived and cohort-validated, but still PENDING UK renal-clinician verification
against the published Major 2019 baseline-survival values.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

# ACR unit conversion (mg/mmol -> mg/g): the published equation uses ln(ACR in mg/g). Safety-critical.
_MG_MMOL_TO_MG_G = 8.8403

# ---------------------------------------------------------------------------
# UK-recalibrated 4-variable KFRE constants.
#   coef/center: Tangri 4-var (from ukidney.com calculator JS). age uses (age/10), egfr uses (egfr/5).
#   s0_2yr/s0_5yr: baseline survival re-estimated on the Major 2019 UK cohort (Breslow, ACR floor
#                  0.6 mg/mmol; robust to floor choice). Set to None to force the safe refusal state.
# ---------------------------------------------------------------------------
UK_KFRE_CONSTANTS: dict | None = {
    "model": "tangri-4var-uk-recalibrated",
    "coef": {"age_per10": -0.2201, "male": 0.2467, "egfr_per5": -0.5567, "ln_acr_mgg": 0.4510},
    "center": {"age_per10": 7.036, "male": 0.5642, "egfr_per5": 7.222, "ln_acr_mgg": 5.137},
    "s0_2yr": 0.98791,
    "s0_5yr": 0.95741,
    "acr_floor_mmol": 0.6,
    "provenance": (
        "Coefficients/centering: Tangri 4-var KFRE via ukidney.com calculator JS. UK baseline "
        "survival: Breslow recalibration on Major et al. 2019 PLoS Med cohort (n=35539, 568 KRT "
        "events); Harrell's C=0.930. Pending UK renal-clinician verification vs the published S0."
    ),
}

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
    """4-variable KFRE with UK-recalibrated baseline survival.

    Prognostic index PI = Σ coef_i · (x_i − center_i), with age scaled per-10, eGFR per-5, and ACR as
    ln(ACR in mg/g). risk(t) = 1 − S0(t) ^ exp(PI). Matches the ukidney.com calculator's linear
    predictor exactly; only S0 differs (UK cohort recalibration).
    """
    acr_floor = k.get("acr_floor_mmol", 0.6)
    acr_mg_g = max(acr_mg_mmol, acr_floor) * _MG_MMOL_TO_MG_G
    male = 1.0 if str(sex).lower().startswith("m") else 0.0
    c, cen = k["coef"], k["center"]
    pi = (
        c["age_per10"] * (age / 10.0 - cen["age_per10"])
        + c["male"] * (male - cen["male"])
        + c["egfr_per5"] * (egfr / 5.0 - cen["egfr_per5"])
        + c["ln_acr_mgg"] * (math.log(acr_mg_g) - cen["ln_acr_mgg"])
    )
    risk_2yr = 1.0 - k["s0_2yr"] ** math.exp(pi)
    risk_5yr = 1.0 - k["s0_5yr"] ** math.exp(pi)
    return risk_2yr, risk_5yr
