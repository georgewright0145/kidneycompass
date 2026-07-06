"""Deterministic escalation delivery — the safety guarantee on the OUTPUT side.

The escalation DECISION is already code (engines/escalation.py). This makes the DELIVERY code too:
an after_model_callback that, whenever a gate fired this turn (recorded in session state by the
tools), ensures the final response actually routes the person to clinical help — appending the
authoritative wording if the model failed to. So "always escalate" cannot be lost to model judgement
(e.g. the model asking for more data first). Course principle: escalation is code-checked.
"""

from __future__ import annotations

import re

from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_response import LlmResponse
from google.genai import types as genai_types

from .tools import PENDING_ESCALATION_KEY

# Same cues as the eval gate — if the model already routed the person, don't duplicate.
_ESCALATION_CUES = [
    r"\bcontact(?:ing)? your (?:gp|practice|doctor|care team|surgery|kidney team)\b",
    r"\b(?:call|ring|dial|contact) (?:nhs )?111\b",
    r"\bnhs 111\b",
    r"\bseek (?:medical|urgent|prompt) (?:help|care|attention|advice)\b",
    r"\bseek help promptly\b",
    r"\bgp practice\b",
    r"\bA&E\b|\baccident and emergency\b|\bemergency (?:department|care)\b",
]
_cues = [re.compile(p, re.IGNORECASE) for p in _ESCALATION_CUES]


def _already_escalates(text: str) -> bool:
    return any(rx.search(text) for rx in _cues)


def _is_final_text_response(llm_response: LlmResponse) -> tuple[bool, str]:
    """A final response = has text parts and no pending function calls."""
    content = getattr(llm_response, "content", None)
    if content is None or not getattr(content, "parts", None):
        return False, ""
    has_tool_call = any(getattr(p, "function_call", None) for p in content.parts)
    if has_tool_call:
        return False, ""
    text = " ".join(getattr(p, "text", "") or "" for p in content.parts)
    return (bool(text.strip()), text)


async def enforce_escalation_delivery(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> LlmResponse | None:
    """after_model_callback: guarantee a fired gate is delivered in the final response."""
    pending = callback_context.state.get(PENDING_ESCALATION_KEY)
    if not pending or not pending.get("escalate"):
        return None

    is_final, text = _is_final_text_response(llm_response)
    if not is_final:
        return None  # only enforce on the final, user-facing text turn

    if _already_escalates(text):
        # Model already routed the person; mark handled and leave the response as-is.
        callback_context.state[PENDING_ESCALATION_KEY] = None
        return None

    # The model produced a final answer WITHOUT escalating a fired gate. Append the authoritative
    # wording rather than trusting the model to have done it.
    wording = pending.get("suggested_wording") or (
        "Please contact your GP practice about this, or call NHS 111 if you feel unwell or unsure."
    )
    appended = (text.rstrip() + "\n\n" + wording).strip()
    callback_context.state[PENDING_ESCALATION_KEY] = None
    return LlmResponse(
        content=genai_types.Content(
            role="model",
            parts=[genai_types.Part.from_text(text=appended)],
        )
    )
