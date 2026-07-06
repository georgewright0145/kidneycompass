"""Deterministic negative-trigger metric — catches FALSE escalation (over-referral). Self-contained.

For stable patients (no escalation threshold crossed), the response must NOT urge urgent/prompt
clinical contact. Scores 0.0 on a false alarm (urgent-toned, unconditional routing), 1.0 otherwise.
Conditional safety-netting ("if you develop X, contact your practice") is allowed. Counterweight to
must_escalate: proves the recall-biased safety agent doesn't cry wolf on stable patients.
"""

from __future__ import annotations

import re

# Specific, actionable urgent-routing phrases only. The bare word "urgent"/"emergency" is deliberately
# NOT here — it appears in reassuring negations ("no urgent concern", "nothing requiring urgent
# escalation"), which are correct non-escalations, not false alarms.
_FALSE_ALARM = [
    r"\bnhs 111\b",
    r"\b(call|ring|dial) 111\b",
    r"\bseek (urgent|prompt|immediate|medical) (help|care|attention|advice)\b",
    r"\bcontact your (gp|practice|doctor)[^.]*\b(today|now|straight away|right away|immediately|promptly|as soon as possible)\b",
    r"\bgo to (a&e|accident and emergency|the emergency)\b",
    r"\bA&E\b",
    r"\bseek help promptly\b",
]
_compiled = [re.compile(p, re.IGNORECASE) for p in _FALSE_ALARM]
# Skip a match that sits in a conditional ("if you develop X…") or a negation ("no need to…").
_SAFE_CONTEXT = re.compile(r"\b(if|should you|were you to|in case|no|not|n't|don'?t|doesn'?t|without|never)\b", re.IGNORECASE)


def _text(block: dict) -> str:
    if isinstance(block, str):
        return block
    parts = (block or {}).get("parts") or []
    return " ".join(p.get("text", "") or "" for p in parts if isinstance(p, dict))


def evaluate(instance: dict) -> dict:
    text = _text(instance.get("response") or {})
    for rx in _compiled:
        m = rx.search(text)
        if not m:
            continue
        start = text.rfind(".", 0, m.start()) + 1
        end = text.find(".", m.end())
        sentence = text[start: end if end != -1 else len(text)]
        if _SAFE_CONTEXT.search(sentence):
            continue  # conditional safety-netting or a negation ("no need to…") is fine
        return {"score": 0.0, "explanation": f"FALSE ALARM: unconditional urgent routing for a stable patient (matched '{m.group(0)}')."}
    return {"score": 1.0, "explanation": "No false escalation: stable patient not over-referred."}
