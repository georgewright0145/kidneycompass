# UK KFRE recalibration — method, results, validation

*Reproduces the constants in `engines/kfre.py` (`UK_KFRE_CONSTANTS`). Pending UK renal-clinician
verification against the published Major 2019 baseline-survival values.*

## Method
- **Coefficients & centering:** the original **Tangri 4-variable KFRE**, transcribed from the
  **ukidney.com KFRE calculator's JavaScript source** (a real source — not model memory):
  ```
  PI = -0.2201·(age/10 − 7.036) + 0.2467·(male − 0.5642)
       − 0.5567·(eGFR/5 − 7.222) + 0.4510·(ln(ACR_mg/g) − 5.137)
  risk(t) = 1 − S0(t) ^ exp(PI)
  ```
  ACR is converted mg/mmol → mg/g (×8.8403). Sex: male = 1, female = 0.
- **UK recalibration:** the coefficients are held **fixed** as a linear-predictor offset and the
  **baseline survival S0 is re-estimated on the UK cohort** (Major et al. 2019, *PLoS Medicine*) via
  the **Breslow estimator**. Death is treated as censoring for the KRT outcome (the standard KFRE
  competing-risk limitation). Undetectable ACR (recorded 0) is floored at 0.6 mg/mmol.

## Cohort
Major et al. 2019 primary-care CKD cohort: **n = 35,539**, **568 KRT events**, 9,447 competing
deaths, eGFR 10–59 (all G3a–5), up to ~12 years follow-up. **Real patient-level data — not committed
to this repo** (synthetic-only policy). Run `recalibrate.py <csv>` against your local copy to reproduce.

## Results (ACR floor 0.6 mg/mmol)
| Quantity | UK-recalibrated | Non-UK Tangri |
|---|---|---|
| S0(2yr) | **0.98791** | 0.97500 |
| S0(5yr) | **0.95741** | 0.92400 |

The UK baseline survival is **higher** (lower baseline risk) than the North American values — exactly
the published finding that non-UK calibrations **overestimate** UK risk (UKKA / NICE).

## Validation
- **Discrimination — Harrell's C = 0.930.** Matches published KFRE performance (~0.90–0.93). Because
  C depends only on the linear predictor, this confirms the coefficients were transcribed correctly.
- **Calibration (5-year, by predicted-risk decile) — predicted vs observed (Kaplan–Meier):**
  the top decile (where the >5% referral decision lives) predicts **12.9%** vs observed **14.2%**;
  decile 9 predicts 1.8% vs 1.8%. Good agreement at the clinically important high-risk end.
- **Robustness:** S0(5yr) varies only 0.9572–0.9579 across ACR floors 0.3–1.13 mg/mmol; C ≈ 0.929–0.931.

## Caveats / open items
- These constants are **cohort-derived**; they should be **verified by a UK renal clinician against
  the published Major 2019 baseline-survival figures** before any real-world use.
- In-sample calibration (derived and validated on the same cohort) is optimistic for the middle
  deciles; discrimination and the high-risk calibration are the load-bearing checks here.
- Referral nuance confirmed by the UKKA summary: a **5-year KFRE > 5%** has **replaced eGFR < 30** as
  the referral trigger (more sensitive/specific for KRT).
