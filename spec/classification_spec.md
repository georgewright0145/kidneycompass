# Spec — KDIGO Classification & Monitoring (`engines/classify.py`)

*Source of truth for `classify.py`. Grounded in `spec/guidelines/kdigo_2024_classification.md`.
Deterministic Python — no model. Every threshold traces to the guideline file.*

## Interface
```
classify(egfr: float | None, acr: float | None) -> Classification
```
`Classification` fields: `g_category` (str|None), `a_category` (str|None), `risk_band`
(green|amber|orange|red|None), `monitoring_per_year` (int|None), `meets_ckd_definition` (bool),
`notes` (list[str]), `missing` (list[str]).

## Scenarios

### G-category mapping (inclusive lower bound)
- eGFR 95 → G1; 90 → G1; 89 → G2; 60 → G2; 59 → G3a; 45 → G3a; 44 → G3b; 30 → G3b; 29 → G4;
  15 → G4; 14 → G5; 5 → G5.

### A-category mapping (mg/mmol; A2 boundary inclusive, A3 strictly > 30)
- ACR 2.9 → A1; 3 → A2; 30 → A2; 30.1 → A3; 70 → A3.

### Risk band (from the heat-map table)
- G1/A1 → (not CKD by definition unless other damage) — see below.
- G3a/A2 → orange. G3b/A1 → orange. G3a/A1 → amber. G3b/A2 → red. G4/any → red. G5/any → red.
- G2/A2 → amber. G1/A3 → orange. G3a/A3 → red.

### Monitoring frequency (per year, from band)
- green → 1; amber → 1; orange → 2; red → 2 (≥2). G4/G5 red → 3 (the "two or more, 3–4 at most
  severe" guidance; encode G4/G5 as 3).

### Missing-data behaviour (everything optional; never invent)
- eGFR present, ACR absent → classify on **G axis only**; `a_category=None`, `risk_band=None`
  (heat-map needs both axes); `missing=["acr"]`; note prompting for a urine ACR.
- ACR present, eGFR absent → classify on **A axis only**; `missing=["egfr"]`.
- Both absent → all None; `missing=["egfr","acr"]`; no classification invented.

### CKD-definition edge
- eGFR ≥ 60 AND ACR < 3 (A1) AND no other damage marker → `meets_ckd_definition=False`; note that
  this does not by itself meet the CKD definition (needs sustained >3 months + damage). Still report
  G/A categories descriptively.
- eGFR < 60 OR ACR ≥ 3 → `meets_ckd_definition=True` (subject to >3-month sustained caveat, noted).

### Units
- ACR is **mg/mmol**. If a caller passes a value that looks like mg/g (e.g. absurdly large), that is
  the intake agent's normalisation job, NOT classify's — classify trusts mg/mmol. Note the unit in output.
```
