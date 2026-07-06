"""Deterministic guidance helpers — medication dose-review flags and referral-criteria flags.

Grounded in spec/guidelines/nice_ng203_management.md. These INFORM and ROUTE; they never issue a
personalised start/stop/dose instruction. The LLM explains; these functions decide what to flag.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Renal dose-review medicines: (canonical name, aliases, the guideline note). Inform-and-route only.
_RENAL_REVIEW_MEDS = [
    ("metformin", ["metformin"],
     "Metformin is reviewed around eGFR 45 and is usually stopped below eGFR 30 — worth a medicines "
     "review with your GP or pharmacist."),
    ("nitrofurantoin", ["nitrofurantoin"],
     "Nitrofurantoin is generally avoided below eGFR 45 — worth a medicines review."),
    ("DOAC", ["apixaban", "rivaroxaban", "edoxaban", "dabigatran", "doac"],
     "Direct oral anticoagulants are dose-adjusted by kidney function — worth a medicines review."),
    ("gabapentinoid", ["gabapentin", "pregabalin"],
     "Gabapentinoids can accumulate when kidney function is reduced — worth a medicines review."),
    ("ACEi/ARB", ["ramipril", "lisinopril", "enalapril", "perindopril", "losartan", "candesartan",
                  "irbesartan", "valsartan"],
     "ACE inhibitors and ARBs are foundational in CKD but are among the 'sick-day' medicines often "
     "paused during acute dehydrating illness — any change should be agreed with your clinician."),
    ("diuretic", ["furosemide", "bumetanide", "bendroflumethiazide", "indapamide", "spironolactone"],
     "Diuretics are among the 'sick-day' medicines often paused during acute dehydrating illness — "
     "discuss any change with your clinician."),
    ("SGLT2 inhibitor", ["dapagliflozin", "empagliflozin", "canagliflozin", "sglt2"],
     "SGLT2 inhibitors are a 'sick-day' medicine often paused during acute dehydrating illness; a "
     "small, expected eGFR dip on starting one is normal and not a cause for alarm."),
    ("NSAID", ["ibuprofen", "naproxen", "diclofenac", "nsaid"],
     "NSAIDs can be hard on the kidneys; over-the-counter use is worth checking with a pharmacist."),
]

SADMANS_NOTE = (
    "Several common medicines (ACE inhibitors and ARBs, diuretics/water tablets, SGLT2 inhibitors, "
    "metformin, NSAIDs — sometimes called the 'SADMANS' group) are often withheld TEMPORARILY during "
    "an acute dehydrating illness (vomiting, diarrhoea, fevers) and restarted after recovery. This "
    "should be agreed with a clinician. If you are acutely unwell or unsure, contact your practice "
    "or NHS 111."
)


@dataclass
class MedicationReview:
    flags: list[dict] = field(default_factory=list)         # {category, matched, note}
    sick_day_note: str = ""
    sglt2_prompt: str | None = None


def review_medications(medicines: list[str], egfr: float | None) -> MedicationReview:
    """Flag medicines a clinician reviews at a given kidney function. Inform-and-route only."""
    review = MedicationReview(sick_day_note=SADMANS_NOTE)
    seen = set()
    for med in medicines:
        m = (med or "").strip().lower()
        if not m:
            continue
        for category, aliases, note in _RENAL_REVIEW_MEDS:
            if any(alias in m for alias in aliases) and category not in seen:
                review.flags.append({"category": category, "matched": med, "note": note})
                seen.add(category)

    # Generic additional-medication prompt: SGLT2i is supported across eGFR ~20-45 (KDIGO 2024).
    on_sglt2 = "SGLT2 inhibitor" in seen
    if egfr is not None and 20 <= egfr <= 45 and not on_sglt2:
        review.sglt2_prompt = (
            "Guidelines suggest an SGLT2 inhibitor (such as dapagliflozin or empagliflozin) is "
            "usually considered at your level of kidney function, to help protect the kidneys. This "
            "is general information — whether it is right for you is a decision for your GP or kidney "
            "team, so it is worth asking them."
        )
    return review


# --- Referral-criteria flags (NICE NG203). Flag the criterion; the clinician makes the referral. ---
@dataclass
class ReferralFlags:
    flags: list[dict] = field(default_factory=list)  # {code, message}


def referral_criteria(
    egfr: float | None,
    acr: float | None,
    kfre_5yr: float | None,
    haematuria: bool = False,
    uncontrolled_bp_4plus_agents: bool = False,
) -> ReferralFlags:
    """Flag NICE referral criteria for discussion with the GP (does not itself refer)."""
    out = ReferralFlags()
    if kfre_5yr is not None and kfre_5yr > 0.05:
        out.flags.append({"code": "KFRE_OVER_5PCT",
                          "message": "A 5-year kidney-failure risk over 5% is a NICE referral criterion."})
    if egfr is not None and egfr < 30:
        out.flags.append({"code": "EGFR_BELOW_30",
                          "message": "An eGFR below 30 is a NICE referral criterion."})
    if acr is not None and acr >= 70:
        out.flags.append({"code": "ACR_70_OR_MORE",
                          "message": "An ACR of 70 mg/mmol or more is a NICE referral criterion."})
    if acr is not None and acr > 30 and haematuria:
        out.flags.append({"code": "A3_WITH_HAEMATURIA",
                          "message": "A3 albuminuria with blood in the urine is a NICE referral criterion."})
    if uncontrolled_bp_4plus_agents:
        out.flags.append({"code": "UNCONTROLLED_BP",
                          "message": "Blood pressure uncontrolled on four or more agents is a NICE referral criterion."})
    return out
