"""Failing-test-first for engines/aki_check.py — traces to spec/aki_spec.md."""

from datetime import datetime, timedelta

from engines.aki_check import CreatinineReading, check_aki

T0 = datetime(2026, 1, 1, 8, 0, 0)


def _r(value, hours=0, days=0):
    return CreatinineReading(value_umol_l=value, timestamp=T0 + timedelta(hours=hours, days=days))


class TestCriterion1AbsRise48h:
    def test_rise_26_within_48h_flags(self):
        res = check_aki([_r(80), _r(106, hours=47)], baseline=80)
        assert res.suspected_aki is True
        assert res.criterion == "abs_rise_48h"

    def test_rise_25_does_not_flag(self):
        res = check_aki([_r(80), _r(105, hours=47)], baseline=80)
        assert res.suspected_aki is False

    def test_rise_26_outside_48h_not_criterion1(self):
        # 40 rise but at 49h; ratio 120/80=1.5 within 7d -> criterion 2 fires instead
        res = check_aki([_r(80), _r(120, hours=49)], baseline=80)
        assert res.suspected_aki is True
        assert res.criterion == "ratio_1_5x_7d"


class TestCriterion2Ratio7d:
    def test_ratio_1_5_within_7d_flags(self):
        res = check_aki([_r(100), _r(150, days=6)], baseline=100)
        assert res.suspected_aki is True
        assert res.criterion == "ratio_1_5x_7d"

    def test_ratio_1_49_does_not_flag(self):
        res = check_aki([_r(100), _r(149, days=6)], baseline=100)
        assert res.suspected_aki is False

    def test_ratio_1_5_outside_7d_does_not_flag(self):
        res = check_aki([_r(100), _r(160, days=8)], baseline=100)
        assert res.suspected_aki is False


class TestNoAki:
    def test_stable_readings(self):
        res = check_aki([_r(90), _r(95, days=30)], baseline=90)
        assert res.suspected_aki is False

    def test_single_reading_insufficient(self):
        res = check_aki([_r(100)])
        assert res.suspected_aki is False
        assert "insufficient" in res.detail.lower()


class TestFlaggedReadingSeparated:
    def test_flagged_reading_timestamp_returned(self):
        res = check_aki([_r(80), _r(150, days=2)], baseline=80)
        assert res.suspected_aki is True
        assert res.flagged_reading_ts == T0 + timedelta(days=2)
