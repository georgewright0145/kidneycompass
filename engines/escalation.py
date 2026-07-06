"""Escalation gate — THE SAFETY CORE. Deterministic, no model, cannot be prompt-injected.

Grounded in spec/escalation_spec.md and PRD 4.11. Tuned for recall: when in doubt, escalate.
Returns escalate/urgency/reason-codes plus calm, non-prescriptive suggested wording.
"""

from __future__ import annotations

from dataclasses import dataclass, field

EGFR_REFERRAL = 30.0          # eGFR < 30 -> refer/discuss (nice_ng203)
ACR_REFERRAL = 70.0           # ACR >= 70 mg/mmol (nice_ng203)
HB_ANAEMIA = 110.0            # Hb <= 110 g/L (nice_ng203 anaemia)
KFRE_REFERRAL = 0.05          # 5-year KFRE > 5% (nice_ng203)
RAPID_EGFR_DROP_PCT = 0.25    # sustained >= 25% fall (conservative; flag for clinician confirmation)
RAPID_EGFR_DROP_ABS = 15.0    # or sustained fall >= 15 ml/min/1.73m2 within 12 months


@dataclass
class PatientState:
    egfr: float | None = None
    acr: float | None = None
    hb: float | None = None
    kfre_5yr: float | None = None
    suspected_aki: bool = False
    significant_new_symptom: bool = False
    egfr_drop_pct_12m: float | None = None      # fractional drop, e.g. 0.30 for 30%
    egfr_drop_abs_12m: float | None = None       # absolute ml/min drop over 12 months
    anaemia_symptoms: bool = False


@dataclass
class EscalationDecision:
    escalate: bool = False
    urgency: str = "routine"  # "urgent" | "gp_soon" | "routine"
    reasons: list[dict] = field(default_factory=list)
    suggested_wording: str = ""


def evaluate_escalation(state: PatientState) -> EscalationDecision:
    reasons: list[dict] = []
    urgent = False

    if state.suspected_aki:
        reasons.append({
            "code": "SUSPECTED_AKI",
            "message": "A sudden change in your kidney blood test may indicate acute kidney injury, "
                       "which needs prompt clinical assessment.",
        })
        urgent = True

    if state.egfr is not None and state.egfr < EGFR_REFERRAL:
        reasons.append({
            "code": "EGFR_BELOW_30",
            "message": "Your eGFR is below 30, a level at which guidelines suggest specialist "
                       "kidney input may be worth discussing.",
        })

    if state.acr is not None and state.acr >= ACR_REFERRAL:
        reasons.append({
            "code": "ACR_70_OR_MORE",
            "message": "Your urine ACR is 70 mg/mmol or above, a NICE referral threshold worth "
                       "raising with your GP.",
        })

    rapid = False
    if state.egfr_drop_pct_12m is not None and state.egfr_drop_pct_12m >= RAPID_EGFR_DROP_PCT:
        rapid = True
    if state.egfr_drop_abs_12m is not None and state.egfr_drop_abs_12m >= RAPID_EGFR_DROP_ABS:
        rapid = True
    if rapid:
        reasons.append({
            "code": "RAPID_EGFR_FALL",
            "message": "Your kidney function appears to have fallen relatively quickly, which is "
                       "worth reviewing with your GP.",
        })

    if state.kfre_5yr is not None and state.kfre_5yr > KFRE_REFERRAL:
        reasons.append({
            "code": "KFRE_OVER_5PCT",
            "message": "Your estimated 5-year kidney risk is above the 5% level NICE uses as a "
                       "referral threshold.",
        })

    if (state.hb is not None and state.hb <= HB_ANAEMIA) or state.anaemia_symptoms:
        reasons.append({
            "code": "HB_ANAEMIA",
            "message": "Your haemoglobin is at or below the level where anaemia related to kidney "
                       "disease is worth checking with your GP.",
        })

    if state.significant_new_symptom:
        reasons.append({
            "code": "NEW_SIGNIFICANT_SYMPTOM",
            "message": "You have reported a significant new symptom that is worth raising with your "
                       "care team.",
        })

    escalate = len(reasons) > 0
    if not escalate:
        urgency = "routine"
    elif urgent:
        urgency = "urgent"
    else:
        urgency = "gp_soon"

    return EscalationDecision(
        escalate=escalate,
        urgency=urgency,
        reasons=reasons,
        suggested_wording=_wording(urgency, reasons),
    )


def _wording(urgency: str, reasons: list[dict]) -> str:
    if not reasons:
        return ""
    lead = {
        "urgent": "Please seek medical help promptly — contact your GP practice today, or if it is "
                  "closed or you feel very unwell, call NHS 111.",
        "gp_soon": "It would be worth contacting your GP practice to discuss this.",
        "routine": "",
    }[urgency]
    points = " ".join(r["message"] for r in reasons)
    tail = (" This is educational support and does not replace your GP or care team; the decision "
            "about any treatment is theirs to make with you.")
    return f"{lead} {points}{tail}".strip()
