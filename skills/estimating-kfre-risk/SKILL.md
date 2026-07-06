---
name: estimating-kfre-risk
description: >-
  Estimate a person's 2- and 5-year risk of kidney failure (needing dialysis or a transplant) using
  the UK-calibrated 4-variable Kidney Failure Risk Equation (KFRE) from age, sex, eGFR, and ACR, for
  CKD stages G3a-G5. Use when the user asks about their dialysis risk, "how likely am I to need
  dialysis", "what's my kidney-failure risk", or wants a what-if ("what if my ACR improves"). Only
  eGFR and ACR are valid what-if inputs — the skill explains honestly that smoking, HbA1c and blood
  pressure are NOT equation inputs and act by lowering ACR / slowing eGFR decline instead. Refuses on
  unstable/AKI values, on eGFR ≥ 60, and until the clinician-verified UK constants are loaded (it
  shows an honest "not available" rather than a fabricated number). NOT for staging (classifying-ckd)
  or acute spikes (recognising-aki). Inform honestly; never invent a number.
license: Proprietary — KidneyCompass. Clinical content pending UK renal-clinician sign-off.
---

# Estimating KFRE risk (UK-calibrated, honest by design)

The honesty of this feature matters more than the feature. The calculation is **deterministic
Python** in `engines/kfre.py` (exposed as the `estimate_dialysis_risk` tool).

## How to use
1. Gather age, sex, eGFR, ACR (mg/mmol). Confirm the value is stable (not AKI-affected).
2. Call the deterministic estimator. It returns `status`, `risk_2yr`, `risk_5yr`, `caveats`,
   `valid_whatifs`.
3. Explain by status:
   - `ok` → give the 2- and 5-year risk, then the caveats (no competing-death risk; day-to-day
     variability — the trend matters more than one value).
   - `constants_unavailable` → say honestly that the UK-calibrated calculation is pending
     clinician verification, so no number is shown. **Do not invent one.**
   - `unstable_value` / `not_applicable` → explain why (AKI-affected, or eGFR ≥ 60).
4. What-ifs: only **eGFR** and **ACR** are real recalculations. If asked about smoking/HbA1c/BP,
   explain from the evidence that these lower ACR / slow eGFR decline over time — do NOT fake a
   KFRE recalculation from them.

## Grounding
- `references/kfre_notes.md` (from `spec/guidelines/kfre.md`): inputs, caveats, valid what-ifs, and
  the current constants-pending status.

## What this skill is NOT for
- KDIGO staging → **classifying-ckd**. Acute creatinine spikes → **recognising-aki**.
- A 5-year KFRE risk over 5% is a NICE referral criterion — flag it; the clinician refers.
