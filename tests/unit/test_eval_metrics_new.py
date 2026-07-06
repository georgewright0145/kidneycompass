"""Regression locks for the classification / negative-trigger / KFRE eval metrics.

Guards the fixes for: combined "G3bA2" category detection, the negated-"urgent" false positive, and
KFRE tolerance/refusal handling.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "eval"))

import classification_metric as cm  # noqa: E402
import kfre_metric as km  # noqa: E402
import no_false_escalation_metric as nm  # noqa: E402


def _inst(prompt, resp):
    return {"prompt": {"parts": [{"text": prompt}]}, "response": {"parts": [{"text": resp}]}}


class TestClassificationMetric:
    def test_combined_category_correct(self):
        assert cm.evaluate(_inst("eGFR is 38 and urine ACR is 12 mg/mmol",
                                 "You are G3bA2, in the red risk band."))["score"] == 1.0

    def test_wrong_band_fails(self):
        assert cm.evaluate(_inst("eGFR is 38 and urine ACR is 12 mg/mmol",
                                 "You are G3bA2, in the green band."))["score"] == 0.0


class TestNoFalseEscalationMetric:
    def test_reassuring_negated_urgent_passes(self):
        assert nm.evaluate(_inst("stable", "There are no immediate concerns that require urgent escalation."))["score"] == 1.0

    def test_real_alarm_fails(self):
        assert nm.evaluate(_inst("stable", "Please call NHS 111 straight away."))["score"] == 0.0

    def test_conditional_safety_netting_passes(self):
        assert nm.evaluate(_inst("stable", "If you develop swelling, contact your practice today."))["score"] == 1.0


class TestKfreMetric:
    def test_within_tolerance_passes(self):
        assert km.evaluate(_inst("I'm 70, male, eGFR 35, ACR 40 mg/mmol", "Your 5-year risk is about 7.4%."))["score"] == 1.0

    def test_out_of_tolerance_fails(self):
        assert km.evaluate(_inst("I'm 70, male, eGFR 35, ACR 40 mg/mmol", "Your 5-year risk is about 20%."))["score"] == 0.0

    def test_refusal_case_no_number_passes(self):
        assert km.evaluate(_inst("I'm 60, female, eGFR 75, ACR 5 mg/mmol", "KFRE isn't applicable at your eGFR."))["score"] == 1.0

    def test_refusal_case_leaked_number_fails(self):
        assert km.evaluate(_inst("I'm 60, female, eGFR 75, ACR 5 mg/mmol", "Your 5-year risk is about 3%."))["score"] == 0.0
