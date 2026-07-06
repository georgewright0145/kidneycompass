# KFRE — Kidney Failure Risk Equation (UK-recalibrated)

> **Source & status.** Bootstrapped from the KidneyCompass PRD (§4.4 and appendix "KFRE"), citing
> Tangri et al. and the UK external validation/recalibration (Major et al., *PLoS Medicine* 2019),
> the UKKA KFRE summary, and NICE (recommends the UK-calibrated version).
> **Version: `kfre-4var-uk` / 2026-07-06.**
>
> ✅ **CONSTANTS NOW LOADED (cohort-derived, pending clinician verification).** Coefficients &
> centering: Tangri 4-variable KFRE, transcribed from the ukidney.com calculator JS. UK baseline
> survival S₀ **re-estimated on the Major 2019 PLoS Medicine cohort** (Breslow recalibration):
> **S₀(2yr) = 0.98791, S₀(5yr) = 0.95741** (ACR floor 0.6 mg/mmol). Validated: Harrell's C = 0.930;
> UK S₀ higher than the non-UK Tangri values (0.975 / 0.9240), matching the finding that non-UK
> calibrations overestimate UK risk. Full method + validation: `spec/kfre_recalibration/RESULTS.md`.
> Still **pending UK renal-clinician verification** against the published Major 2019 S₀ figures.

## What KFRE predicts
2- and 5-year risk of **kidney replacement therapy** (dialysis or transplant) for CKD stages
**G3a–G5**.

## Inputs — 4-variable model
1. **Age** (years)
2. **Sex** (male / female)
3. **eGFR** (ml/min/1.73m²)
4. **ACR** (mg/mmol — UK units; the equation's original form uses mg/g, so **unit conversion is a
   safety-critical step** — see notes)

8-variable adds serum albumin, phosphate, bicarbonate, calcium. **KidneyCompass uses the 4-variable
UK-recalibrated version** (the version NICE recommends; non-UK calibrations overestimate UK risk).

## What is and isn't a valid "what-if"
- **Valid (real recalculation):** changing **eGFR** or **ACR** — the only modifiable inputs in KFRE.
  e.g. show risk if ACR improves from A3 into A2, or if eGFR stabilises.
- **NOT valid inputs:** **smoking, HbA1c, blood pressure, weight** are NOT KFRE inputs. The app must
  **not** fake a recalculation from them. They belong in a separate "factors you can influence"
  evidence panel (they act by reducing ACR / slowing eGFR decline over time).

## Refusal / safety rules (enforced in `kfre.py`)
- **Never run on unstable or suspected-AKI values** (an AKI-flagged eGFR/creatinine is held out).
- **Only run for eGFR consistent with G3a–G5** (eGFR < 60). For eGFR ≥ 60, KFRE is not applicable.
- **Refuse if UK constants are unavailable** (current state) — return status, never a fabricated number.

## Caveats (shown, not buried)
- KFRE does **not** model the competing risk of **death**; can **overestimate** in older/frailer people.
- eGFR/ACR have real **day-to-day variability** — the trend matters more than a single value.

## Referral link
A **5-year KFRE risk over 5%** is a NICE referral criterion (see `nice_ng203_management.md`).
Per the UKKA KFRE summary (`spec/kfre_recalibration/UKKA_KFRE_summary.pdf`), this **>5% threshold has
replaced the previous "eGFR < 30" referral trigger**, being more sensitive and specific for KRT.
Both remain flagged by the escalation gate; the clinician makes the referral.
