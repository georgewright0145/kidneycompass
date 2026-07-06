"""Tests for the clinical-knowledge retrieval (mcp/clinical_knowledge_server/knowledge.py)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "mcp" / "clinical_knowledge_server"))

from knowledge import GuidelineIndex  # noqa: E402

IDX = GuidelineIndex()


def test_index_loads_all_guideline_files():
    srcs = {s["source"] for s in IDX.sources()}
    assert "kdigo_2024_classification.md" in srcs
    assert "aki_thresholds.md" in srcs
    assert "nice_ng203_management.md" in srcs
    # versions are captured, not blank
    assert all(s["version"] for s in IDX.sources())


def test_exact_lookup_acr_referral_threshold():
    res = IDX.search("70 mg/mmol", mode="exact")
    assert res.passages
    joined = " ".join(p["text"] for p in res.passages).lower()
    assert "70 mg/mmol" in joined


def test_lookup_aki_creatinine_threshold():
    res = IDX.search("creatinine rise 26 within 48 hours", mode="auto")
    assert res.passages
    top = res.passages[0]["text"].lower()
    assert "26" in top and "48" in top


def test_lookup_metformin():
    res = IDX.search("metformin eGFR", mode="auto")
    assert any("metformin" in p["text"].lower() for p in res.passages)


def test_results_carry_source_and_version():
    res = IDX.search("SGLT2 inhibitor", mode="auto")
    assert res.passages
    for p in res.passages:
        assert p["source"].endswith(".md")
        assert p["version"]


def test_no_match_returns_note_not_invention():
    res = IDX.search("zzzxqq aardvarkium bloopnix", mode="auto")
    assert res.passages == []
    assert "not" in res.note.lower()
