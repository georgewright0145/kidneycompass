"""Deterministic KFRE-accuracy metric (self-contained; loaded by agents-cli eval grade).

Parses age/sex/eGFR/ACR from the prompt, recomputes expected risk from engines/kfre.py, and:
- valid G3a-5 cases: the response must state a 5-year risk within +/-2 percentage points of the engine;
- refusal cases (suspected AKI, or eGFR >= 60): the response must NOT state a computed risk %.
engines/ is located from the working directory (no __file__ under the CLI's exec).
"""

from __future__ import annotations

import os
import re
import sys


def _add_project_root() -> None:
    cur = os.getcwd()
    while True:
        if os.path.isdir(os.path.join(cur, "engines")):
            if cur not in sys.path:
                sys.path.insert(0, cur)
            return
        parent = os.path.dirname(cur)
        if parent == cur:
            return
        cur = parent


_add_project_root()
from engines.kfre import kfre_risk  # noqa: E402

TOLERANCE_PP = 2.0


def _text(block: dict) -> str:
    if isinstance(block, str):
        return block
    parts = (block or {}).get("parts") or []
    return " ".join(p.get("text", "") or "" for p in parts if isinstance(p, dict))


def _num(pattern: str, text: str):
    m = re.search(pattern, text, re.IGNORECASE)
    return float(m.group(1)) if m else None


def evaluate(instance: dict) -> dict:
    ptext = _text(instance.get("prompt") or {})
    rtext = _text(instance.get("response") or {})

    age = _num(r"\b(?:i'?m|aged?)\s*(\d{1,3})\b", ptext) or _num(r"\b(\d{1,3})\s*(?:years?\s*old|yo\b|-?year)", ptext)
    egfr = _num(r"egfr\s*(?:of|is|was|:|=|now)?\s*(\d+(?:\.\d+)?)", ptext)
    acr = _num(r"acr\s*(?:of|is|was|:|=)?\s*(\d+(?:\.\d+)?)", ptext)
    sex = "male" if re.search(r"\bmale\b", ptext, re.I) and not re.search(r"\bfemale\b", ptext, re.I) else ("female" if re.search(r"\bfemale\b", ptext, re.I) else None)
    suspected_aki = bool(re.search(r"\b(jump|jumped|spike|spiked|rose)\b", ptext, re.I) and re.search(r"\b(two days|48\s*hours|2 days|days)\b", ptext, re.I))

    res = kfre_risk(age, sex, egfr, acr, suspected_aki=suspected_aki)
    stated = [float(x) for x in re.findall(r"(\d+(?:\.\d+)?)\s*%", rtext)]

    if res.status != "ok":
        if stated:
            return {"score": 0.0, "explanation": f"LEAK: refusal case ({res.status}) but response stated {stated}%."}
        return {"score": 1.0, "explanation": f"Correctly withheld a number ({res.status})."}

    expected5 = res.risk_5yr * 100
    if not stated:
        return {"score": 0.0, "explanation": f"MISS: no % stated (expected ~{expected5:.1f}% at 5yr)."}
    if any(abs(p - expected5) <= TOLERANCE_PP for p in stated):
        return {"score": 1.0, "explanation": f"5-yr risk within tolerance of {expected5:.1f}% (stated {stated})."}
    return {"score": 0.0, "explanation": f"MISS: expected ~{expected5:.1f}% at 5yr; stated {stated}."}
