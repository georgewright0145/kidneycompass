"""Tests for engines/appointment.py — deterministic appointment-prep assembly."""

from engines.appointment import build_appointment_summary


def test_gp_summary_basics():
    s = build_appointment_summary(
        "gp", g_category="G3b", a_category="A2", risk_band="red", egfr=38, acr=12,
        medicines=["metformin"],
    )
    assert s.visit_type == "gp"
    assert any("G3bA2" in line for line in s.current_picture)
    assert any("urine ACR" in q for q in s.questions)
    # metformin should surface a medicines-review flag
    assert any("metformin" in f.lower() for f in s.flags)


def test_sglt2_question_when_in_band():
    s = build_appointment_summary("gp", egfr=35, acr=40, medicines=["ramipril"])
    assert any("SGLT2" in q for q in s.questions)


def test_bp_target_reflects_acr_band():
    high = build_appointment_summary("gp", egfr=40, acr=80)
    low = build_appointment_summary("gp", egfr=40, acr=10)
    assert any("130/80" in q for q in high.questions)
    assert any("140/90" in q for q in low.questions)


def test_renal_clinic_adds_secondary_care_questions():
    s = build_appointment_summary("renal_clinic", g_category="G4", a_category="A3", egfr=20, acr=90)
    assert s.visit_type == "renal_clinic"
    assert any("progression rate" in q for q in s.questions)
    assert any("KFRE" in q or "trajectory" in q for q in s.questions)
    # eGFR<30 and ACR>=70 should raise referral flags
    assert any("referral" in f.lower() for f in s.flags)


def test_never_prescribes():
    s = build_appointment_summary("gp", egfr=25, acr=90, medicines=["metformin", "ramipril"])
    blob = " ".join(s.questions + s.flags + s.current_picture).lower()
    for banned in ["stop taking", "start taking", "increase your dose", "you should stop"]:
        assert banned not in blob
