"""Deterministic classification-accuracy metric (self-contained; loaded by agents-cli eval grade).

Parses eGFR and ACR from the prompt, recomputes the ground-truth KDIGO category and risk band from
engines/classify.py, and checks the agent's response states them. Score 1.0 requires BOTH the CGA
category (e.g. "G3bA2") and the risk band correct. No __file__ (the CLI execs this without one);
engines/ is located from the working directory (the project root at grade time).
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
from engines.classify import classify  # noqa: E402


def _text(block: dict) -> str:
    if isinstance(block, str):
        return block
    parts = (block or {}).get("parts") or []
    return " ".join(p.get("text", "") or "" for p in parts if isinstance(p, dict))


def evaluate(instance: dict) -> dict:
    ptext = _text(instance.get("prompt") or {})
    rtext = _text(instance.get("response") or {})
    em = re.search(r"egfr\s*(?:of|is|was|:|=)?\s*(\d+(?:\.\d+)?)", ptext, re.IGNORECASE)
    am = re.search(r"acr\s*(?:of|is|was|:|=)?\s*(\d+(?:\.\d+)?)", ptext, re.IGNORECASE)
    if not em or not am:
        return {"score": 0.0, "explanation": "Could not parse eGFR/ACR from the prompt."}

    c = classify(float(em.group(1)), float(am.group(1)))
    low = rtext.lower()
    combined = f"{c.g_category}{c.a_category}".lower()
    g_ok = bool(re.search(rf"\b{c.g_category.lower()}\b", low)) or combined in low
    a_ok = bool(re.search(rf"\b{c.a_category.lower()}\b", low)) or combined in low
    cga_ok = (g_ok and a_ok) or combined in low
    band_ok = c.risk_band.lower() in low

    if cga_ok and band_ok:
        return {"score": 1.0, "explanation": f"Correct: {c.g_category}{c.a_category}, {c.risk_band}."}
    missing = []
    if not g_ok:
        missing.append(f"G ({c.g_category})")
    if not a_ok:
        missing.append(f"A ({c.a_category})")
    if not band_ok:
        missing.append(f"band ({c.risk_band})")
    return {"score": 0.0, "explanation": "MISS: " + ", ".join(missing) + " not stated correctly."}
