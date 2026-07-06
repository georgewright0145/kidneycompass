"""Deterministic do-not-answer guard for the prescribing / diagnosis class.

Runs as a before_model_callback: it inspects the incoming user turn with plain Python (regex), so
the refusal cannot be prompt-injected away — it never reaches the model when a personalised
prescribing / dose-change / diagnosis request is detected. Routes the decision back to the clinician.

This is the security analogue of the clinical do-not-answer class (PRD 4.11, plan section 4).
"""

from __future__ import annotations

import re

from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types as genai_types

from .config import DISCLAIMER

# Patterns that indicate a request for a PERSONALISED prescribing / dosing / diagnosis decision.
# Deliberately high-recall: when a turn looks like "tell me what to take / should I stop my drug /
# what's my diagnosis", we refuse and route to the clinician.
_PRESCRIBE_PATTERNS = [
    r"\bshould i (start|stop|take|come off|change|increase|decrease|reduce|double|halve)\b",
    r"\b(can|should) i stop taking\b",
    r"\bwhat dose\b|\bwhat'?s the (right|correct) dose\b|\bhow much .* should i take\b",
    r"\bprescribe\b|\bwrite me a prescription\b",
    r"\b(increase|decrease|double|halve|adjust|change) (my|the) dose\b",
    r"\bcan i take (more|less|another)\b",
    r"\bshould i be on\b.*\?",  # borderline; "should I be on X" -> route to GP (generic ok, personalised no)
    r"\bwhat medication should i\b|\bwhich (drug|medicine|medication) should i (take|use)\b",
    r"\bdiagnose me\b|\bwhat'?s my diagnosis\b|\bdo i have (kidney|renal) (failure|disease)\b",
    r"\bstop my (metformin|ramipril|lisinopril|insulin|diuretic|water tablet|blood pressure|bp)\b",
]

_REFUSAL = (
    "I can't advise you personally on starting, stopping, or changing a medicine or dose, and I "
    "can't diagnose — those are decisions for your GP, pharmacist, or kidney team, who know your "
    "full picture. What I can do is give you general, guideline-based information and help you "
    "prepare to raise this with them. For example, I can explain which medicines clinicians often "
    "review at a given level of kidney function, or what the guidelines say is usually considered "
    "at your stage, so you can have that conversation.\n\nIf you feel acutely unwell or unsure, "
    "contact your GP practice or call NHS 111.\n\n" + DISCLAIMER
)

_compiled = [re.compile(p, re.IGNORECASE) for p in _PRESCRIBE_PATTERNS]


def _latest_user_text(llm_request: LlmRequest) -> str:
    for content in reversed(llm_request.contents or []):
        if getattr(content, "role", None) == "user":
            parts = getattr(content, "parts", None) or []
            return " ".join(getattr(p, "text", "") or "" for p in parts)
    return ""


def is_prescribing_request(text: str) -> bool:
    """Deterministic check — True if the text asks for a personalised prescribing/diagnosis decision."""
    return any(rx.search(text) for rx in _compiled)


async def do_not_answer_guard(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> LlmResponse | None:
    """before_model_callback: short-circuit prescribing/diagnosis requests with a routed refusal."""
    text = _latest_user_text(llm_request)
    if is_prescribing_request(text):
        callback_context.state["do_not_answer_triggered"] = True
        return LlmResponse(
            content=genai_types.Content(
                role="model",
                parts=[genai_types.Part.from_text(text=_REFUSAL)],
            )
        )
    return None
