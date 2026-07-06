"""Escalation sub-agent — the safety core's voice.

The decision is made by the deterministic `assess_escalation` gate (Python, un-injectable). This
agent's only job is to call it and deliver the result in calm, specific, non-alarmist language.
It handles turns where a person reports symptoms or asks "should I be worried?".
"""

from __future__ import annotations

from google.adk.agents import Agent
from google.genai import types as genai_types

from ..config import MODEL
from ..escalation_delivery import enforce_escalation_delivery
from ..tools import assess_escalation

_INSTRUCTION = """
You are the escalation specialist for KidneyCompass. Safety is your only job.

Always call `assess_escalation` with whatever is known (eGFR, ACR, Hb, KFRE, suspected_aki, and
whether a significant new symptom was reported). The tool's decision is AUTHORITATIVE:
- If escalate is true: deliver its suggested_wording. Match the urgency:
  - "urgent": tell them to seek help promptly — GP today, or NHS 111 if the practice is closed or
    they feel very unwell.
  - "gp_soon": suggest contacting their GP practice to discuss.
- If escalate is false: reassure calmly, without being falsely reassuring, and say what would be
  worth watching for.

Never invent a threshold, never diagnose, and never give a personalised instruction to start, stop,
or change a medicine — route any such decision to the GP. Keep the tone warm and low-anxiety.
Always note that this is educational support and does not replace their GP or care team.
""".strip()


def create_escalation_agent() -> Agent:
    return Agent(
        name="escalation_agent",
        model=MODEL,
        description=(
            "Decides and voices when to contact the GP or seek urgent care, using the deterministic "
            "escalation gate. Handles reported symptoms and 'should I be worried?' questions."
        ),
        instruction=_INSTRUCTION,
        tools=[assess_escalation],
        after_model_callback=enforce_escalation_delivery,
        generate_content_config=genai_types.GenerateContentConfig(temperature=0.1),
    )
