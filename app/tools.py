"""Deterministic clinical tools exposed to the ADK agents.

Every tool is a thin, JSON-serializable wrapper around an engine in engines/. The LLM decides WHICH
tool to call and explains the RESULT in plain English; it never computes the clinical number itself.
The escalation gate result returned here is authoritative and cannot be overridden by the model.
"""

from __future__ import annotations

import json
from datetime import datetime

from google.adk.tools import ToolContext

from engines.aki_check import CreatinineReading, check_aki
from engines.appointment import build_appointment_summary
from engines.classify import classify
from engines.escalation import PatientState, evaluate_escalation
from engines.guidance import referral_criteria, review_medications
from engines.kfre import kfre_risk

# Session-state key holding the authoritative pending escalation. Written by the tools whenever a
# gate fires; enforced onto the final response by app/escalation_delivery.py so escalation delivery
# never depends on the model choosing to relay it.
PENDING_ESCALATION_KEY = "pending_escalation"


def _record_escalation(tool_context: ToolContext | None, decision) -> None:
    if tool_context is None or not decision.escalate:
        return
    prior = tool_context.state.get(PENDING_ESCALATION_KEY)
    # Keep the most urgent decision seen this turn (urgent outranks gp_soon).
    if prior and prior.get("urgency") == "urgent" and decision.urgency != "urgent":
        return
    tool_context.state[PENDING_ESCALATION_KEY] = {
        "escalate": decision.escalate,
        "urgency": decision.urgency,
        "reasons": decision.reasons,
        "suggested_wording": decision.suggested_wording,
    }


def classify_ckd(egfr: float | None, acr_mg_mmol: float | None) -> dict:
    """Classify a person's CKD against KDIGO from eGFR and urine ACR.

    Args:
        egfr: eGFR in ml/min/1.73m^2, or null if not available.
        acr_mg_mmol: Urine albumin-to-creatinine ratio in mg/mmol (UK units), or null.

    Returns:
        dict with KDIGO g_category, a_category, risk_band, monitoring_per_year,
        meets_ckd_definition, notes, and any missing inputs.
    """
    c = classify(egfr, acr_mg_mmol)
    return {
        "g_category": c.g_category,
        "a_category": c.a_category,
        "risk_band": c.risk_band,
        "monitoring_per_year": c.monitoring_per_year,
        "meets_ckd_definition": c.meets_ckd_definition,
        "notes": c.notes,
        "missing": c.missing,
    }


def check_aki_from_readings(
    creatinine_readings_json: str, baseline_umol_l: float | None, tool_context: ToolContext
) -> dict:
    """Check for suspected acute kidney injury from timestamped creatinine readings.

    Args:
        creatinine_readings_json: JSON array of readings, each an object with
            "value_umol_l" (number, creatinine in umol/L) and "timestamp" (ISO 8601 string).
        baseline_umol_l: The person's usual stable creatinine in umol/L, or null to infer it.

    Returns:
        dict with suspected_aki (bool), criterion, detail, flagged_reading_ts, baseline_used.
        On a suspected-AKI hit the flagged reading must be held out of the CKD trend and risk estimate,
        and the person must be escalated to prompt clinical assessment.
    """
    try:
        raw = json.loads(creatinine_readings_json) if creatinine_readings_json else []
    except (json.JSONDecodeError, TypeError):
        return {"suspected_aki": False, "detail": "Could not parse creatinine readings.", "criterion": None}

    readings = []
    for item in raw:
        try:
            readings.append(
                CreatinineReading(
                    value_umol_l=float(item["value_umol_l"]),
                    timestamp=datetime.fromisoformat(str(item["timestamp"]).replace("Z", "+00:00")),
                )
            )
        except (KeyError, ValueError, TypeError):
            continue

    res = check_aki(readings, baseline=baseline_umol_l)
    # A suspected-AKI hit is a must-always-escalate class: record the escalation deterministically
    # now, so delivery does not depend on the model separately calling assess_escalation.
    if res.suspected_aki:
        _record_escalation(tool_context, evaluate_escalation(PatientState(suspected_aki=True)))
    return {
        "suspected_aki": res.suspected_aki,
        "criterion": res.criterion,
        "detail": res.detail,
        "flagged_reading_ts": res.flagged_reading_ts.isoformat() if res.flagged_reading_ts else None,
        "baseline_used": res.baseline_used,
    }


def assess_escalation(
    egfr: float | None,
    acr_mg_mmol: float | None,
    hb_g_l: float | None,
    kfre_5yr: float | None,
    suspected_aki: bool,
    significant_new_symptom: bool,
    tool_context: ToolContext,
) -> dict:
    """Run the deterministic escalation gate (the safety core). Recall over precision.

    Args:
        egfr: eGFR in ml/min/1.73m^2, or null.
        acr_mg_mmol: Urine ACR in mg/mmol, or null.
        hb_g_l: Haemoglobin in g/L, or null.
        kfre_5yr: 5-year KFRE risk as a fraction (e.g. 0.07 for 7%), or null.
        suspected_aki: True if the AKI check flagged a suspected acute kidney injury.
        significant_new_symptom: True if the person reports a significant new symptom.

    Returns:
        dict with escalate (bool), urgency (urgent|gp_soon|routine), reasons (list of code+message),
        and suggested_wording. This decision is authoritative; do not soften or override it.
    """
    decision = evaluate_escalation(
        PatientState(
            egfr=egfr,
            acr=acr_mg_mmol,
            hb=hb_g_l,
            kfre_5yr=kfre_5yr,
            suspected_aki=suspected_aki,
            significant_new_symptom=significant_new_symptom,
        )
    )
    _record_escalation(tool_context, decision)
    return {
        "escalate": decision.escalate,
        "urgency": decision.urgency,
        "reasons": decision.reasons,
        "suggested_wording": decision.suggested_wording,
    }


def estimate_dialysis_risk(
    age: float | None,
    sex: str | None,
    egfr: float | None,
    acr_mg_mmol: float | None,
    suspected_aki: bool,
) -> dict:
    """Estimate 2- and 5-year kidney-failure (dialysis) risk with the UK-calibrated KFRE.

    Only eGFR and ACR are valid what-if inputs. Refuses on unstable/AKI values, on eGFR >= 60,
    and — currently — until the UK recalibration constants are supplied (returns a clear status
    rather than an invented number).

    Args:
        age: Age in years, or null.
        sex: "male" or "female", or null.
        egfr: eGFR in ml/min/1.73m^2, or null.
        acr_mg_mmol: Urine ACR in mg/mmol, or null.
        suspected_aki: True if the value may be affected by acute kidney injury.

    Returns:
        dict with status, risk_2yr, risk_5yr, caveats, valid_whatifs.
    """
    res = kfre_risk(age, sex, egfr, acr_mg_mmol, suspected_aki=suspected_aki)
    return {
        "status": res.status,
        "risk_2yr": res.risk_2yr,
        "risk_5yr": res.risk_5yr,
        "caveats": res.caveats,
        "valid_whatifs": res.valid_whatifs,
    }


def review_medicines_list(medicines_csv: str, egfr: float | None) -> dict:
    """Give generic, guideline-based medication information for a CKD patient (inform-and-route only).

    Flags medicines clinicians review by kidney function, gives sick-day-rules education, and — where
    appropriate — a GENERIC prompt that an SGLT2 inhibitor is usually considered at this eGFR. NEVER
    tells anyone to start, stop, or change a medicine or dose.

    Args:
        medicines_csv: The person's medicines as a comma-separated string (e.g. "metformin, ramipril").
        egfr: eGFR in ml/min/1.73m^2, or null.

    Returns:
        dict with flags (each category+note), sick_day_note, and an optional generic sglt2_prompt.
    """
    meds = [m.strip() for m in (medicines_csv or "").split(",") if m.strip()]
    review = review_medications(meds, egfr)
    return {
        "flags": review.flags,
        "sick_day_note": review.sick_day_note,
        "sglt2_prompt": review.sglt2_prompt,
    }


def check_referral_criteria(
    egfr: float | None,
    acr_mg_mmol: float | None,
    kfre_5yr: float | None,
    haematuria: bool,
    uncontrolled_bp_4plus_agents: bool,
) -> dict:
    """Flag NICE referral criteria for discussion with the GP (does not itself refer).

    Args:
        egfr: eGFR in ml/min/1.73m^2, or null.
        acr_mg_mmol: Urine ACR in mg/mmol, or null.
        kfre_5yr: 5-year KFRE risk as a fraction (e.g. 0.07), or null.
        haematuria: True if the person reports blood in the urine.
        uncontrolled_bp_4plus_agents: True if BP is uncontrolled on four or more agents.

    Returns:
        dict with flags (each a code + message). The clinician makes any referral.
    """
    ref = referral_criteria(egfr, acr_mg_mmol, kfre_5yr, haematuria, uncontrolled_bp_4plus_agents)
    return {"flags": ref.flags}


def prepare_appointment(
    visit_type: str,
    g_category: str | None,
    a_category: str | None,
    risk_band: str | None,
    egfr: float | None,
    acr_mg_mmol: float | None,
    hb_g_l: float | None,
    kfre_5yr: float | None,
    medicines_csv: str | None,
    new_symptoms_csv: str | None,
    suspected_aki_events_csv: str | None,
) -> dict:
    """Assemble a one-page summary and prioritised question list for a GP or renal-clinic visit.

    Args:
        visit_type: "gp" or "renal_clinic".
        g_category: KDIGO G category (e.g. "G3b"), or null.
        a_category: KDIGO A category (e.g. "A2"), or null.
        risk_band: green/amber/orange/red, or null.
        egfr: eGFR in ml/min/1.73m^2, or null.
        acr_mg_mmol: Urine ACR in mg/mmol, or null.
        hb_g_l: Haemoglobin in g/L, or null.
        kfre_5yr: 5-year KFRE risk as a fraction, or null.
        medicines_csv: Comma-separated medicines, or null.
        new_symptoms_csv: Comma-separated new/changed symptoms, or null.
        suspected_aki_events_csv: Comma-separated descriptions of suspected-AKI events, or null.

    Returns:
        dict with headline, current_picture, questions, and flags for the person to take along.
    """
    def _split(s: str | None) -> list[str]:
        return [x.strip() for x in (s or "").split(",") if x.strip()]

    s = build_appointment_summary(
        visit_type=visit_type,
        g_category=g_category,
        a_category=a_category,
        risk_band=risk_band,
        egfr=egfr,
        acr=acr_mg_mmol,
        hb=hb_g_l,
        kfre_5yr=kfre_5yr,
        medicines=_split(medicines_csv),
        new_symptoms=_split(new_symptoms_csv),
        suspected_aki_events=_split(suspected_aki_events_csv),
    )
    return {
        "visit_type": s.visit_type,
        "headline": s.headline,
        "current_picture": s.current_picture,
        "questions": s.questions,
        "flags": s.flags,
    }
