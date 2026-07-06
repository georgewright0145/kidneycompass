# KFRE — Kidney Failure Risk Equation (UK-recalibrated)

> **Source & status.** Bootstrapped from the KidneyCompass PRD (§4.4 and appendix "KFRE"), citing
> Tangri et al. and the UK external validation/recalibration (Major et al., *PLoS Medicine* 2019),
> the UKKA KFRE summary, and NICE (recommends the UK-calibrated version).
> **Version: `kfre-4var-uk` / 2026-07-06.**
>
> ⚠️ **HARD DEPENDENCY — NOT YET SUPPLIED.** The exact UK **recalibration constants** (baseline
> survival S₀ at 2 and 5 years, and the centering / coefficient values) are **not in the PRD** and
> must be provided by the user before `kfre.py` computes any risk. Until then `kfre.py` MUST refuse
> to compute and return `status: "constants_unavailable"`. **Do not invent constants.**

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
