"""Failing-test-first for engines/kfre.py — traces to spec/kfre_spec.md.

Current state: UK recalibration constants NOT supplied -> must refuse, never invent a number.
"""

from engines.kfre import kfre_risk


class TestConstantsUnavailable:
    def test_refuses_without_uk_constants(self):
        res = kfre_risk(age=70, sex="male", egfr=35, acr_mg_mmol=40)
        assert res.status == "constants_unavailable"
        assert res.risk_2yr is None and res.risk_5yr is None
        assert any("clinician" in c.lower() or "unavailable" in c.lower() for c in res.caveats)


class TestRefusalRulesHoldRegardless:
    def test_suspected_aki_is_unstable(self):
        res = kfre_risk(age=70, sex="male", egfr=35, acr_mg_mmol=40, suspected_aki=True)
        assert res.status == "unstable_value"
        assert res.risk_5yr is None

    def test_egfr_ge_60_not_applicable(self):
        res = kfre_risk(age=70, sex="female", egfr=75, acr_mg_mmol=5)
        assert res.status == "not_applicable"

    def test_missing_input_not_applicable(self):
        res = kfre_risk(age=None, sex="male", egfr=35, acr_mg_mmol=40)
        assert res.status == "not_applicable"


class TestValidWhatifsDeclared:
    def test_only_egfr_and_acr_are_whatifs(self):
        res = kfre_risk(age=70, sex="male", egfr=35, acr_mg_mmol=40)
        assert set(res.valid_whatifs) == {"egfr", "acr"}
