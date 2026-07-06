"""Tests for engines/guidance.py — inform-and-route medication flags + NICE referral flags."""

from engines.guidance import referral_criteria, review_medications


class TestMedicationReview:
    def test_metformin_flagged(self):
        r = review_medications(["Metformin 500mg"], egfr=32)
        cats = {f["category"] for f in r.flags}
        assert "metformin" in cats

    def test_multiple_meds_flagged_once_each(self):
        r = review_medications(["ramipril", "furosemide", "apixaban", "gabapentin"], egfr=40)
        cats = {f["category"] for f in r.flags}
        assert {"ACEi/ARB", "diuretic", "DOAC", "gabapentinoid"} <= cats

    def test_sglt2_prompt_in_band_when_not_on_it(self):
        r = review_medications(["ramipril"], egfr=35)
        assert r.sglt2_prompt is not None

    def test_no_sglt2_prompt_if_already_on_it(self):
        r = review_medications(["dapagliflozin"], egfr=35)
        assert r.sglt2_prompt is None

    def test_no_sglt2_prompt_out_of_band(self):
        assert review_medications(["ramipril"], egfr=70).sglt2_prompt is None

    def test_sick_day_note_always_present(self):
        assert "SADMANS" in review_medications([], egfr=None).sick_day_note

    def test_never_issues_personalised_instruction(self):
        r = review_medications(["metformin"], egfr=25)
        for f in r.flags:
            low = f["note"].lower()
            assert "stop taking" not in low and "you should stop" not in low


class TestReferralCriteria:
    def test_egfr_below_30(self):
        codes = {f["code"] for f in referral_criteria(28, 10, None).flags}
        assert "EGFR_BELOW_30" in codes

    def test_acr_70(self):
        codes = {f["code"] for f in referral_criteria(50, 85, None).flags}
        assert "ACR_70_OR_MORE" in codes

    def test_kfre_over_5pct(self):
        codes = {f["code"] for f in referral_criteria(50, 10, 0.08).flags}
        assert "KFRE_OVER_5PCT" in codes

    def test_a3_with_haematuria(self):
        codes = {f["code"] for f in referral_criteria(50, 40, None, haematuria=True).flags}
        assert "A3_WITH_HAEMATURIA" in codes

    def test_stable_no_flags(self):
        assert referral_criteria(55, 10, 0.01).flags == []
