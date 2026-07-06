# KFRE notes (reference for estimating-kfre-risk)

Canonical source: `spec/guidelines/kfre.md`. Pending UK renal-clinician sign-off.

## Model
UK-recalibrated **4-variable** KFRE (Tangri; UK recalibration Major et al. 2019). Predicts 2- and
5-year risk of kidney replacement therapy for **G3a–G5**. NICE recommends the UK-calibrated version;
non-UK calibrations overestimate UK risk.

## Inputs
Age · Sex · eGFR · ACR (mg/mmol). The published equation uses ACR in mg/g → unit conversion is a
safety-critical step, unit-tested once constants exist.

## Valid what-ifs
Only **eGFR** and **ACR** (the equation's modifiable inputs). Smoking, HbA1c, blood pressure and
weight are **NOT** inputs — never fake a recalculation from them; explain they act by lowering ACR
and slowing eGFR decline.

## Refusal rules (engine-enforced)
- Never on suspected-AKI / unstable values.
- Not applicable at eGFR ≥ 60.
- **Constants currently unavailable** → return an honest status, never a fabricated number.

## Caveats (always shown)
- Does not model competing risk of death; can overestimate in older/frailer people.
- eGFR/ACR vary day to day — the trend matters more than a single value.

## Referral
5-year KFRE risk **> 5%** is a NICE referral criterion — flag for discussion with the GP.
