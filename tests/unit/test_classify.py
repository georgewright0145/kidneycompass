"""Failing-test-first for engines/classify.py — traces to spec/classification_spec.md."""

import pytest

from engines.classify import classify


class TestGCategory:
    @pytest.mark.parametrize(
        "egfr,expected",
        [
            (95, "G1"), (90, "G1"), (89, "G2"), (60, "G2"),
            (59, "G3a"), (45, "G3a"), (44, "G3b"), (30, "G3b"),
            (29, "G4"), (15, "G4"), (14, "G5"), (5, "G5"),
        ],
    )
    def test_g_category_inclusive_lower_bound(self, egfr, expected):
        assert classify(egfr, None).g_category == expected


class TestACategory:
    @pytest.mark.parametrize(
        "acr,expected",
        [(2.9, "A1"), (3, "A2"), (30, "A2"), (30.1, "A3"), (70, "A3")],
    )
    def test_a_category_boundaries(self, acr, expected):
        assert classify(None, acr).a_category == expected


class TestRiskBand:
    @pytest.mark.parametrize(
        "egfr,acr,band",
        [
            (50, 10, "orange"),   # G3a/A2
            (40, 1, "orange"),    # G3b/A1
            (50, 1, "amber"),     # G3a/A1
            (40, 10, "red"),      # G3b/A2
            (20, 1, "red"),       # G4/A1
            (10, 1, "red"),       # G5/A1
            (70, 10, "amber"),    # G2/A2
            (95, 50, "orange"),   # G1/A3
            (50, 50, "red"),      # G3a/A3
        ],
    )
    def test_risk_band(self, egfr, acr, band):
        assert classify(egfr, acr).risk_band == band


class TestMonitoring:
    @pytest.mark.parametrize(
        "egfr,acr,per_year",
        [
            (50, 1, 1),   # amber -> 1
            (50, 10, 2),  # orange -> 2
            (40, 10, 2),  # red (G3b) -> 2
            (20, 1, 3),   # red G4 -> 3
            (10, 50, 3),  # red G5 -> 3
        ],
    )
    def test_monitoring_per_year(self, egfr, acr, per_year):
        assert classify(egfr, acr).monitoring_per_year == per_year


class TestMissingData:
    def test_egfr_only_classifies_g_axis_no_band(self):
        c = classify(50, None)
        assert c.g_category == "G3a"
        assert c.a_category is None
        assert c.risk_band is None
        assert "acr" in c.missing

    def test_acr_only_classifies_a_axis(self):
        c = classify(None, 40)
        assert c.a_category == "A3"
        assert c.g_category is None
        assert "egfr" in c.missing

    def test_both_absent_invents_nothing(self):
        c = classify(None, None)
        assert c.g_category is None and c.a_category is None
        assert c.risk_band is None
        assert set(c.missing) == {"egfr", "acr"}


class TestCkdDefinition:
    def test_normal_values_do_not_meet_definition(self):
        c = classify(95, 1)  # G1/A1
        assert c.meets_ckd_definition is False

    def test_low_egfr_meets_definition(self):
        assert classify(50, 1).meets_ckd_definition is True

    def test_high_acr_meets_definition(self):
        assert classify(95, 40).meets_ckd_definition is True
