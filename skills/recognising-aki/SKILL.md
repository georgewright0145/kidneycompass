---
name: recognising-aki
description: >-
  Recognise suspected acute kidney injury (AKI) from timestamped creatinine (or eGFR) readings using
  the KDIGO / NHS "Think Kidneys" thresholds: a rise of ≥26 µmol/L within 48 hours, or a rise to
  ≥1.5× the person's baseline within 7 days. Use when the user reports two or more creatinine values
  with dates, mentions a recent illness/dehydration alongside a jump in their numbers, or asks
  whether a sudden change is serious. This is a first-class safety check that ALWAYS escalates on a
  hit and separates the acute spike from the long-term CKD trend and the dialysis-risk estimate. NOT
  for stable long-term staging (use classifying-ckd); urine-output criteria are not used (community
  setting). Detect and route urgently; never diagnose.
license: Proprietary — KidneyCompass. Clinical content pending UK renal-clinician sign-off.
---

# Recognising AKI (KDIGO / Think Kidneys)

AKI is a medical emergency hiding inside the same numbers the app tracks. Detection is
**deterministic Python** in `engines/aki_check.py` (exposed as the `check_aki_from_readings` tool).

## How to use
1. Collect the creatinine readings with their dates/times and, if known, the usual stable baseline.
2. Call the deterministic AKI check. It returns `suspected_aki`, `criterion`
   (`abs_rise_48h` | `ratio_1_5x_7d`), `detail`, `flagged_reading_ts`, `baseline_used`.
3. On a hit: say so calmly and urgently, state that the flagged reading has been **separated from
   the long-term trend and left out of the dialysis-risk estimate**, ask whether they were unwell
   around that date, and **always escalate** (contact GP today / NHS 111).
4. Remind that after an AKI, kidney function should be re-checked and monitored (NICE: ≥3 years).

## Grounding
- Thresholds: `references/aki_thresholds.md` (from `spec/guidelines/aki_thresholds.md`).

## What this skill is NOT for
- Stable long-term KDIGO staging → **classifying-ckd**.
- Urine-output criteria (hospital/catheter only) — not implemented; rely on creatinine/eGFR.
- It never diagnoses AKI; it flags a *suspected* AKI and routes to prompt clinical assessment.
