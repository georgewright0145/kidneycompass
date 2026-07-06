"""Guards the must-escalate metric detector against the actual wording engines/escalation.py emits.

Regression lock for the -ing form bug ("worth contacting your GP practice") that made the metric
under-count real escalations.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "eval"))

from escalation_metric import evaluate  # noqa: E402

from engines.escalation import PatientState, evaluate_escalation  # noqa: E402


def _instance(text: str) -> dict:
    return {"response": {"role": "model", "parts": [{"text": text}]}}


def test_detects_engine_urgent_wording():
    d = evaluate_escalation(PatientState(suspected_aki=True))
    assert evaluate(_instance(d.suggested_wording))["score"] == 1.0


def test_detects_engine_gp_soon_wording():
    d = evaluate_escalation(PatientState(egfr=28, acr=40))
    assert d.urgency == "gp_soon"
    assert evaluate(_instance(d.suggested_wording))["score"] == 1.0


def test_detects_contacting_ing_form():
    assert evaluate(_instance("It would be worth contacting your GP practice to discuss this."))["score"] == 1.0


def test_non_escalation_scores_zero():
    text = "Your results look stable and within a reassuring range. Keep up your usual routine."
    assert evaluate(_instance(text))["score"] == 0.0
