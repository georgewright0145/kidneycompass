---
name: preparing-appointment
description: >-
  Prepare a person for a GP or kidney-clinic (renal/nephrology) appointment by assembling their
  current picture into a one-page summary and a prioritised question list. Pulls together their KDIGO
  classification and risk band, trends since last contact, any suspected-AKI events with context, new
  or changed symptoms, medicines, and the most recent results, and highlights guideline-flagged
  things worth raising (e.g. "am I on the right medicines for my stage / should I be on an SGLT2
  inhibitor?", "is my blood pressure at target for my ACR band?", "should I have a urine ACR done?").
  Use when the user says "I'm seeing my GP/kidney doctor soon, help me prepare", "what should I ask",
  or "get me ready for my appointment". Tailors to GP vs renal clinic (secondary care gets
  progression rate, KFRE trajectory, planning questions). This helps them communicate; it is NOT
  diagnosing and NOT prescribing.
license: Proprietary — KidneyCompass. Clinical content pending UK renal-clinician sign-off.
---

# Preparing for an appointment (help the person communicate)

Assembles what the person already has into something they can use in a short appointment. It helps
communication; it does not diagnose or prescribe. The assembly is **deterministic Python** in
`engines/appointment.py` (`build_appointment_summary`).

## How to use
1. Gather the current picture from session state / the conversation: classification + band, recent
   results and trends, any suspected-AKI events with context, new/changed symptoms, medicines.
2. Call `build_appointment_summary` with `visit_type` = "gp" or "renal_clinic".
3. Present the one-page summary and the prioritised question list (`assets/appointment_summary_template.md`),
   including guideline-flagged questions (right medicines for stage / SGLT2 inhibitor, BP target for
   ACR band, whether a urine ACR is due, referral criteria if met).
4. For a renal-clinic visit, tailor to secondary care: progression rate, KFRE trajectory, planning.

## What this skill is NOT for
- Making the diagnosis or the prescribing/referral decision — those are the clinician's. This only
  helps the person raise the right things.
