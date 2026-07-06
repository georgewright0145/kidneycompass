"""Reproduce the UK KFRE baseline-survival recalibration + validation.

Usage:  python spec/kfre_recalibration/recalibrate.py /path/to/kfre_plosmed_v2_0.csv [acr_floor_mmol]

The cohort CSV (Major et al. 2019 PLoS Medicine) is REAL patient-level data and is deliberately NOT
committed to this repo (synthetic-only policy). Point this script at your local copy to reproduce the
constants baked into engines/kfre.py (UK_KFRE_CONSTANTS).

Method: coefficients/centering are the Tangri 4-variable KFRE (from the ukidney.com calculator JS).
They are held FIXED as a linear-predictor offset; only the baseline survival S0 is re-estimated on
the UK cohort via the Breslow estimator (this is what "UK recalibration" means). Death is treated as
censoring for the kidney-replacement-therapy (KRT) outcome — the standard KFRE competing-risk caveat.
"""

import csv
import math
import sys

import numpy as np

MG_MMOL_TO_MG_G = 8.8403
B = {"age_per10": -0.2201, "male": 0.2467, "egfr_per5": -0.5567, "ln_acr_mgg": 0.4510}
C = {"age_per10": 7.036, "male": 0.5642, "egfr_per5": 7.222, "ln_acr_mgg": 5.137}


def prognostic_index(age, male, egfr, acr_mgg):
    return (B["age_per10"] * (age / 10 - C["age_per10"])
            + B["male"] * (male - C["male"])
            + B["egfr_per5"] * (egfr / 5 - C["egfr_per5"])
            + B["ln_acr_mgg"] * (np.log(acr_mgg) - C["ln_acr_mgg"]))


def main(csv_path: str, acr_floor: float = 0.6) -> None:
    rows = list(csv.DictReader(open(csv_path)))
    age = np.array([float(r["age"]) for r in rows])
    egfr = np.array([float(r["epi_egfr"]) for r in rows])
    male = 1.0 - np.array([float(r["female"]) for r in rows])
    acr = np.clip(np.array([float(r["acr_mgmmol"]) for r in rows]), acr_floor, None) * MG_MMOL_TO_MG_G
    esrd = np.array([int(r["esrd"]) for r in rows])
    time_yr = np.array([float(r["time"]) for r in rows]) / 365.25

    pi = prognostic_index(age, male, egfr, acr)
    w = np.exp(pi)

    # Breslow baseline cumulative hazard with PI as offset.
    order = np.argsort(time_yr)
    t_s, e_s, w_s = time_yr[order], esrd[order], w[order]
    suffix_w = np.cumsum(w_s[::-1])[::-1]

    def H0(t):
        return float(np.sum(np.where((e_s == 1) & (t_s <= t), 1.0 / suffix_w, 0.0)))

    s0_2, s0_5 = math.exp(-H0(2.0)), math.exp(-H0(5.0))

    # Harrell's C (discrimination).
    ev = np.where(esrd == 1)[0]
    conc = disc = ties = 0
    for i in ev:
        comp = time_yr > time_yr[i]
        pj = pi[comp]
        conc += int(np.sum(pi[i] > pj)); disc += int(np.sum(pi[i] < pj)); ties += int(np.sum(pi[i] == pj))
    c_stat = (conc + 0.5 * ties) / (conc + disc + ties)

    print(f"n={len(rows)}  KRT_events={int(esrd.sum())}  acr_floor={acr_floor} mg/mmol")
    print(f"UK S0(2yr)={s0_2:.5f}  UK S0(5yr)={s0_5:.5f}  (non-UK Tangri: 0.97500 / 0.92400)")
    print(f"Harrell's C = {c_stat:.4f}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], float(sys.argv[2]) if len(sys.argv) > 2 else 0.6)
