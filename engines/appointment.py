"""Appointment-prep assembly — deterministic. Grounded in PRD §4.8 and spec/guidelines/.

Assembles the person's current picture into a one-page summary and a prioritised, guideline-informed
question list, tailored for a GP or a renal-clinic visit. It helps the person communicate; it does
not diagnose or prescribe. All clinical flags come from the deterministic engines.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .guidance import referral_criteria, review_medications


@dataclass
class AppointmentSummary:
    visit_type: str
    headline: str
    current_picture: list[str] = field(default_factory=list)
    questions: list[str] = field(default_factory=list)
    flags: list[str] = field(default_factory=list)


def build_appointment_summary(
    visit_type: str,
    g_category: str | None = None,
    a_category: str | None = None,
    risk_band: str | None = None,
    egfr: float | None = None,
    acr: float | None = None,
    hb: float | None = None,
    kfre_5yr: float | None = None,
    medicines: list[str] | None = None,
    new_symptoms: list[str] | None = None,
    suspected_aki_events: list[str] | None = None,
) -> AppointmentSummary:
    """Build a one-page summary + prioritised question list for a GP or renal-clinic visit."""
    visit = "renal_clinic" if str(visit_type).lower().startswith("ren") else "gp"
    medicines = medicines or []
    new_symptoms = new_symptoms or []
    suspected_aki_events = suspected_aki_events or []

    cga = (f"{g_category}{a_category}" if g_category and a_category else (g_category or a_category or "not yet classified"))
    summary = AppointmentSummary(
        visit_type=visit,
        headline=f"Preparing for your {'kidney clinic' if visit == 'renal_clinic' else 'GP'} appointment",
    )

    # Current picture
    if cga != "not yet classified":
        band = f", {risk_band} risk band" if risk_band else ""
        summary.current_picture.append(f"KDIGO classification: {cga}{band}.")
    if egfr is not None:
        summary.current_picture.append(f"Latest eGFR: {egfr} ml/min/1.73m^2.")
    if acr is not None:
        summary.current_picture.append(f"Latest urine ACR: {acr} mg/mmol (UK units).")
    if hb is not None:
        summary.current_picture.append(f"Latest haemoglobin: {hb} g/L.")
    if medicines:
        summary.current_picture.append("Current medicines: " + ", ".join(medicines) + ".")
    for ev in suspected_aki_events:
        summary.current_picture.append(f"Suspected AKI event held out of the trend: {ev}.")
    for sym in new_symptoms:
        summary.current_picture.append(f"New/changed symptom: {sym}.")

    # Guideline-informed questions (generic; the clinician decides)
    q = summary.questions
    q.append("Am I on the right medicines for my stage of kidney function?")
    review = review_medications(medicines, egfr)
    if review.sglt2_prompt:
        q.append("Should I be on an SGLT2 inhibitor (a kidney-protecting medicine) at my level of kidney function?")
    for f in review.flags:
        summary.flags.append(f["note"])
    if acr is not None:
        target = "below 130/80" if acr >= 70 else "below 140/90"
        q.append(f"Is my blood pressure at target for my ACR band (aim {target} in clinic)?")
    q.append("Should I have a urine ACR done, or repeated, to check for kidney damage?")

    # Referral flags
    ref = referral_criteria(egfr, acr, kfre_5yr)
    for f in ref.flags:
        summary.flags.append(f["message"] + " Worth asking whether a referral is appropriate.")

    if visit == "renal_clinic":
        q.append("How fast is my kidney function changing (my progression rate)?")
        q.append("What does my kidney-failure risk trajectory (KFRE) look like over time?")
        q.append("What should we be planning for at this stage?")

    return summary
