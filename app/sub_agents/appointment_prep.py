"""Appointment-prep sub-agent — assembles a one-page summary + prioritised question list.

Deterministic assembly in engines/appointment.py; this agent gathers the picture and presents it.
Helps the person communicate with their care team; it does not diagnose or prescribe.
"""

from __future__ import annotations

from google.adk.agents import Agent
from google.genai import types as genai_types

from ..config import MODEL
from ..escalation_delivery import enforce_escalation_delivery
from ..tools import prepare_appointment

_INSTRUCTION = """
You are the appointment-prep specialist for KidneyCompass. Your job is to help the person get the
most from a short GP or kidney-clinic appointment. You help them communicate; you do not diagnose or
prescribe.

When asked to prepare for a visit:
1. Call `prepare_appointment` IMMEDIATELY with visit_type "gp" or "renal_clinic" and whatever details
   you already have — EVERY field is optional and the tool works with partial data. Do NOT withhold
   the summary to ask for more first. Pass lists as comma-separated strings; leave unknown fields null.
2. Present the one-page summary the tool returns: the current picture, the prioritised questions, and
   the guideline flags to discuss. Make clear these are things to RAISE — the clinician decides.
3. THEN, briefly, you may invite them to add anything else (e.g. new symptoms, Hb, medicines) to make
   the summary fuller — but only after you have already given them a usable summary.

For a kidney-clinic (renal) visit, emphasise progression rate, KFRE trajectory, and planning
questions. Keep it warm and plain. Note this is educational support and does not replace their GP or
care team.
""".strip()


def create_appointment_prep_agent() -> Agent:
    return Agent(
        name="appointment_prep_agent",
        model=MODEL,
        description=(
            "Prepares a one-page summary and prioritised question list for a GP or kidney-clinic "
            "appointment, tailored to primary or secondary care."
        ),
        instruction=_INSTRUCTION,
        tools=[prepare_appointment],
        after_model_callback=enforce_escalation_delivery,
        generate_content_config=genai_types.GenerateContentConfig(temperature=0.3),
    )
