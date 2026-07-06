"""Tests for engines/kfre.py — traces to spec/kfre_spec.md.

UK-recalibrated constants are now loaded (coefficients from the ukidney.com calculator; UK baseline
survival recalibrated on the Major 2019 cohort). Computes for valid G3a-5 inputs; still refuses on
unstable/AKI values, eGFR >= 60, and missing inputs; only eGFR and ACR are valid what-ifs.
"""

import math

from engines.kfre import UK_KFRE_CONSTANTS, kfre_risk


class TestComputesForValidInputs:
    def test_computes_ok(self):
        r = kfre_risk(age=70, sex="male", egfr=35, acr_mg_mmol=40)
        assert r.status == "ok"
        assert r.risk_2yr is not None and r.risk_5yr is not None
        assert 0.0 <= r.risk_2yr <= r.risk_5yr <= 1.0  # 5-yr risk >= 2-yr risk

    def test_matches_calculator_linear_predictor(self):
        # Cross-check against the exact ukidney.com formula for a known case.
        age, egfr, acr = 70, 35, 40
        acr_mgg = acr * 8.8403
        pi = (-0.2201 * (age / 10 - 7.036) + 0.2467 * (1 - 0.5642)
              - 0.5567 * (egfr / 5 - 7.222) + 0.4510 * (math.log(acr_mgg) - 5.137))
        expected_5yr = 1 - 0.95741 ** math.exp(pi)
        r = kfre_risk(age=age, sex="male", egfr=egfr, acr_mg_mmol=acr)
        assert abs(r.risk_5yr - expected_5yr) < 1e-6

    def test_female_differs_from_male(self):
        m = kfre_risk(70, "male", 35, 40).risk_5yr
        f = kfre_risk(70, "female", 35, 40).risk_5yr
        assert m > f  # male coefficient is positive

    def test_uk_s0_higher_than_non_uk(self):
        # Sanity: UK recalibration gives higher baseline survival (lower baseline risk) than Tangri.
        assert UK_KFRE_CONSTANTS["s0_5yr"] > 0.9240
        assert UK_KFRE_CONSTANTS["s0_2yr"] > 0.9750


class TestValidWhatifs:
    def test_improving_acr_lowers_risk(self):
        worse = kfre_risk(70, "male", 35, 40).risk_5yr
        better = kfre_risk(70, "male", 35, 20).risk_5yr
        assert better < worse

    def test_stabilising_egfr_lowers_risk(self):
        lower = kfre_risk(70, "male", 25, 40).risk_5yr
        higher = kfre_risk(70, "male", 40, 40).risk_5yr
        assert higher < lower

    def test_only_egfr_and_acr_are_whatifs(self):
        r = kfre_risk(70, "male", 35, 40)
        assert set(r.valid_whatifs) == {"egfr", "acr"}


class TestRefusalRulesHold:
    def test_suspected_aki_is_unstable(self):
        r = kfre_risk(age=70, sex="male", egfr=35, acr_mg_mmol=40, suspected_aki=True)
        assert r.status == "unstable_value"
        assert r.risk_5yr is None

    def test_egfr_ge_60_not_applicable(self):
        assert kfre_risk(70, "female", 75, 5).status == "not_applicable"

    def test_missing_input_not_applicable(self):
        assert kfre_risk(None, "male", 35, 40).status == "not_applicable"


class TestCaveatsAlwaysAttached:
    def test_competing_death_and_variability_caveats(self):
        r = kfre_risk(70, "male", 35, 40)
        blob = " ".join(r.caveats).lower()
        assert "death" in blob and ("vary" in blob or "variab" in blob or "trend" in blob)
