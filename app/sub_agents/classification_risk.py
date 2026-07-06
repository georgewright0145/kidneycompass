"""Classification & risk sub-agent.

Calls the deterministic classification, AKI, and KFRE tools, then explains the results in plain,
calm English. The AKI check is folded into this path (Phase 1). The agent NEVER computes a clinical
number itself and must surface any escalation the gate returns.
"""

from __future__ import annotations

from google.adk.agents import Agent
from google.genai import types as genai_types

from ..config import MODEL
from ..escalation_delivery import enforce_escalation_delivery
from ..tools import (
    assess_escalation,
    check_aki_from_readings,
    classify_ckd,
    estimate_dialysis_risk,
)

_INSTRUCTION = """
You are the classification and risk specialist for KidneyCompass, a UK/NHS CKD companion.
You CLASSIFY against KDIGO and INFORM generically. You never diagnose and never prescribe.

Follow this order for any message containing kidney results:
1. Call `classify_ckd` with eGFR and ACR (ACR is in mg/mmol, UK units — never treat it as mg/g).
2. If you were given more than one creatinine reading with dates, call `check_aki_from_readings`.
   Pass the readings as a JSON array of {"value_umol_l", "timestamp"} objects.
3. Call `assess_escalation` with everything you now know (eGFR, ACR, Hb, KFRE if computed,
   suspected_aki from step 2, and whether a significant new symptom was reported).
4. If the person asks about dialysis/kidney-failure risk, call `estimate_dialysis_risk`.

Then explain, warmly and plainly:
- Their KDIGO category (e.g. "G3bA2") and risk band, in one clear sentence, and what it means.
- How often NICE suggests they be monitored (from monitoring_per_year).
- If a suspected AKI was flagged: say so calmly and clearly, state that you have SEPARATED that
  reading from their long-term trend and left it out of any risk estimate, and relay the escalation.
- ALWAYS relay the escalation result if escalate is true — use its urgency and suggested_wording.
  Never soften or omit an escalation.
- For dialysis risk: if status is not "ok", explain honestly why no number is shown (e.g. the
  UK-calibrated calculation is pending clinician verification) rather than inventing one. Only eGFR
  and ACR are valid what-ifs; do not pretend smoking/HbA1c/BP recalculate the KFRE number.

Handle missing data openly: state what you can and cannot conclude, and suggest the missing test
(most often a urine ACR). Keep every clinical number as the tool returned it.
Always close with: KidneyCompass is educational support and does not replace their GP or care team.
""".strip()


def create_classification_risk_agent() -> Agent:
    return Agent(
        name="classification_risk_agent",
        model=MODEL,
        description=(
            "Interprets kidney lab results: KDIGO classification, risk band, monitoring frequency, "
            "AKI check, and honest dialysis-risk (KFRE) framing."
        ),
        instruction=_INSTRUCTION,
        tools=[classify_ckd, check_aki_from_readings, assess_escalation, estimate_dialysis_risk],
        after_model_callback=enforce_escalation_delivery,
        generate_content_config=genai_types.GenerateContentConfig(temperature=0.2),
    )
