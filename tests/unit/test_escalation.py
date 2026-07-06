"""Failing-test-first for engines/escalation.py — traces to spec/escalation_spec.md.

The safety core. Recall over precision: when in doubt, escalate.
"""

from engines.escalation import PatientState, evaluate_escalation


def _codes(decision):
    return {r["code"] for r in decision.reasons}


class TestMustAlwaysEscalate:
    def test_suspected_aki_urgent(self):
        d = evaluate_escalation(PatientState(suspected_aki=True))
        assert d.escalate is True
        assert d.urgency == "urgent"
        assert "SUSPECTED_AKI" in _codes(d)

    def test_egfr_below_30(self):
        d = evaluate_escalation(PatientState(egfr=28, acr=40))
        assert d.escalate is True
        assert "EGFR_BELOW_30" in _codes(d)

    def test_acr_70_or_more(self):
        d = evaluate_escalation(PatientState(egfr=55, acr=85))
        assert d.escalate is True
        assert "ACR_70_OR_MORE" in _codes(d)

    def test_hb_anaemia(self):
        d = evaluate_escalation(PatientState(hb=108))
        assert d.escalate is True
        assert "HB_ANAEMIA" in _codes(d)

    def test_kfre_over_5pct(self):
        d = evaluate_escalation(PatientState(kfre_5yr=0.07))
        assert d.escalate is True
        assert "KFRE_OVER_5PCT" in _codes(d)

    def test_new_significant_symptom(self):
        d = evaluate_escalation(PatientState(significant_new_symptom=True))
        assert d.escalate is True
        assert "NEW_SIGNIFICANT_SYMPTOM" in _codes(d)


class TestNoEscalation:
    def test_stable_patient_routine(self):
        d = evaluate_escalation(PatientState(egfr=55, acr=10, hb=130))
        assert d.escalate is False
        assert d.urgency == "routine"


class TestUrgencyResolution:
    def test_urgent_wins(self):
        d = evaluate_escalation(PatientState(egfr=25, acr=90, suspected_aki=True))
        assert d.escalate is True
        assert d.urgency == "urgent"
        assert {"SUSPECTED_AKI", "EGFR_BELOW_30", "ACR_70_OR_MORE"} <= _codes(d)

    def test_egfr_below_30_alone_is_gp_soon(self):
        d = evaluate_escalation(PatientState(egfr=28, acr=40))
        assert d.urgency == "gp_soon"


class TestWording:
    def test_wording_present_and_non_prescriptive(self):
        d = evaluate_escalation(PatientState(suspected_aki=True))
        assert d.suggested_wording
        lowered = d.suggested_wording.lower()
        # must never issue a personalised prescribing instruction
        for banned in ["start taking", "stop taking", "increase your dose", "change your dose"]:
            assert banned not in lowered
