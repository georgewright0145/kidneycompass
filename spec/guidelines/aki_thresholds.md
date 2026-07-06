# AKI Thresholds — KDIGO / NHS "Think Kidneys"

> **Source & status.** Bootstrapped verbatim from the KidneyCompass PRD (§4.3 and appendix "AKI
> thresholds"), citing NHS England "Think Kidneys" and the KDIGO AKI criteria. **Pending UK
> renal-clinician sign-off.** Version: `aki-kdigo-thinkkidneys` / 2026-07-06. Verify against
> thinkkidneys.nhs.uk.

## Detection criteria (community setting — creatinine / eGFR only)
A suspected-AKI flag fires if **either**:

1. **Rise in serum creatinine ≥ 26 µmol/L within 48 hours**, OR
2. **Rise in serum creatinine to ≥ 1.5× the person's baseline within 7 days**
   (equivalently, an abrupt fall in eGFR).

The person's **usual stable value** is the baseline (the most recent stable creatinine before the
change; see `spec/aki_spec.md` for how baseline is selected).

**Urine-output criteria are NOT usable outside hospital** (they apply only to catheterised hospital
patients). The app relies solely on the creatinine/eGFR criteria above.

## Staging (magnitude — informational)
KDIGO stages AKI 1–3 by magnitude. For KidneyCompass the flag is binary (suspected AKI: yes/no)
and always escalates; staging is recorded for context but not required to escalate.

## Consequences of a suspected-AKI hit
- **Always escalate** (must-always-escalate class) in calm, urgent language: AKI needs prompt
  clinical assessment.
- **Separate acute from chronic:** the suspected-AKI reading is **held out of the long-term CKD
  trend and out of the KFRE estimate.** The app states explicitly that it has done this.
- **Prompt for context:** "were you unwell around this date?" (links to result-context, PRD §4.5).
- **Post-AKI monitoring:** after an AKI, kidney function should be re-checked and monitored;
  **NICE advises monitoring for at least 3 years post-AKI.** AKI is a risk factor for later CKD.
