---
name: classifying-ckd
description: >-
  Classify chronic kidney disease against KDIGO 2024 from an eGFR and/or urine ACR (mg/mmol, UK
  units): work out the G category (G1-G5), the A category (A1-A3), the combined CGA category (e.g.
  G3bA2), the colour risk band (green/amber/orange/red), and how often NICE suggests monitoring.
  Use when the user gives kidney blood or urine numbers, asks "what does my eGFR/ACR mean", "what
  KDIGO stage am I", "what's my risk band", or "how often should I be monitored". NOT for acute
  creatinine spikes (use recognising-aki), NOT for dialysis-risk percentages (use
  estimating-kfre-risk), and NOT for deciding medication or referral. Classify, never diagnose.
license: Proprietary — KidneyCompass. Clinical content pending UK renal-clinician sign-off.
---

# Classifying CKD (KDIGO 2024)

Classification is arithmetic against a published rubric, not clinical judgement. The mapping is
**deterministic Python** in `engines/classify.py` (exposed as the `classify_ckd` tool). Always take
the category, band, and monitoring frequency from that engine — never estimate them yourself.

## How to use
1. Read the eGFR (ml/min/1.73m²) and ACR (**mg/mmol** — UK units; never treat as mg/g).
2. Call the deterministic classifier. It returns `g_category`, `a_category`, `risk_band`,
   `monitoring_per_year`, `meets_ckd_definition`, `notes`, `missing`.
3. Explain the CGA category (e.g. "G3bA2") and band in one plain sentence, state the monitoring
   frequency, and surface the notes (UK units, >3-month sustained caveat, missing-test prompt).

## Grounding
- Thresholds: `references/kdigo_thresholds.md` (from `spec/guidelines/kdigo_2024_classification.md`).
- Monitoring: `references/nice_monitoring.md`.

## What this skill is NOT for
- A sudden creatinine rise → **recognising-aki**.
- A dialysis-risk percentage or what-if → **estimating-kfre-risk**.
- Medication or referral decisions → route to the clinician (never personalise).

## Missing data
Every input is optional. With eGFR only, classify the G axis and prompt for a urine ACR; with ACR
only, classify the A axis. Never invent a category or a risk band from an absent axis.
