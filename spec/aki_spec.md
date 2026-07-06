# Spec — AKI Check (`engines/aki_check.py`)

*Source of truth for `aki_check.py`. Grounded in `spec/guidelines/aki_thresholds.md`.
Deterministic Python — no model.*

## Interface
```
check_aki(readings: list[CreatinineReading], baseline: float | None = None) -> AkiResult
```
`CreatinineReading`: `{value_umol_l: float, timestamp: datetime}`.
`AkiResult`: `suspected_aki` (bool), `criterion` (str|None: "abs_rise_48h" | "ratio_1_5x_7d"),
`detail` (str), `flagged_reading_ts` (datetime|None), `baseline_used` (float|None).

## Baseline selection
- If `baseline` passed explicitly, use it.
- Else baseline = the earliest reading in the window that is not itself part of the acute rise
  (simplest correct rule for the slice: the person's most recent **stable** value prior to the
  candidate. For the engine, use the minimum of prior readings as the reference stable value; the
  detailed baseline model is documented as a limitation).

## Scenarios (both criteria; either fires)

### Criterion 1 — absolute rise ≥ 26 µmol/L within 48h
- baseline 80 at t0; reading 106 at t0+47h → **suspected AKI** (rise 26, criterion `abs_rise_48h`).
- baseline 80 at t0; reading 105 at t0+47h → rise 25 → **no** AKI on criterion 1.
- baseline 80 at t0; reading 120 at t0+49h → outside 48h window → not criterion 1 (check criterion 2).

### Criterion 2 — ≥ 1.5× baseline within 7 days
- baseline 100 at t0; reading 150 at t0+6d → ratio 1.5 → **suspected AKI** (`ratio_1_5x_7d`).
- baseline 100 at t0; reading 149 at t0+6d → ratio 1.49 → **no** AKI on criterion 2.
- baseline 100 at t0; reading 160 at t0+8d → outside 7d window → not criterion 2.

### No AKI
- Stable readings within normal variation (e.g. 90 → 95 over 30 days) → `suspected_aki=False`.
- Single reading, no baseline → cannot assess → `suspected_aki=False`, detail "insufficient data".

### Consequences (enforced by callers, asserted in integration)
- On a hit: the flagged reading is **held out of the CKD trend and out of KFRE** (the classification/
  KFRE path must exclude `flagged_reading_ts`).
- Always routes to escalation (must-always-escalate; see `escalation_spec.md`).
- Output text must state that the reading was separated from the chronic trend.

## Units
- creatinine in **µmol/L**. Urine-output criteria are **not** implemented (community setting).
```
