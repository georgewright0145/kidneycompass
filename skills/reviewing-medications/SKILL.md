---
name: reviewing-medications
description: >-
  Give generic, guideline-based medication information for someone with CKD: flag medicines
  clinicians review by kidney function (metformin around eGFR 45 and usually stopped below 30;
  nitrofurantoin avoided below eGFR 45; DOACs dose-adjusted; gabapentinoids accumulate), explain
  sick-day rules (the SADMANS group often paused during acute dehydrating illness), note generically
  where a guideline treatment such as an SGLT2 inhibitor is usually considered at their eGFR, and
  caution on OTC NSAIDs. Use when the user lists their medicines, asks "which of my medicines matter
  for my kidneys", "what are sick-day rules", or "should I be on a kidney-protecting medicine".
  INFORM AND ROUTE ONLY — never tell anyone to start, stop, or change a medicine or dose; that is
  always the GP's or pharmacist's decision. Personalised prescribing requests are refused upstream.
license: Proprietary — KidneyCompass. Clinical content pending UK renal-clinician sign-off.
---

# Reviewing medications (inform and route, never prescribe)

The rule that keeps this safe: **inform generically, route every decision to the clinician.** The
flags are **deterministic Python** in `engines/guidance.py` (`review_medications`).

## How to use
1. Take the medicines list and (if known) the eGFR.
2. Call `review_medications`. It returns dose-review `flags` (each with a generic note), the
   `sick_day_note`, and — only when eGFR is ~20–45 and they are not already on one — an
   `sglt2_prompt`.
3. Relay the flags as "worth a medicines review with your GP or pharmacist", the sick-day education,
   and any SGLT2 prompt as a generic "usually considered — ask your GP", reassuring on the expected
   small eGFR dip on starting one.

## Grounding
- `references/renal_meds.md` (from `spec/guidelines/nice_ng203_management.md`).

## Hard boundary
Never issue a personalised start/stop/dose instruction and never diagnose. "Should I stop my
metformin?" → refuse and route to the GP (handled by the do-not-answer guard). This skill only ever
says a medicine is *worth reviewing*, or that a treatment is *generically* recommended at a stage.
