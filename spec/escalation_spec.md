# Spec — Escalation Gate (`engines/escalation.py`) — THE SAFETY CORE

*Source of truth for `escalation.py`. Grounded in PRD §4.11 and `spec/guidelines/*`.
Deterministic Python — no model, cannot be prompt-injected. Tuned for **recall**: when in doubt,
escalate. This is the gate the eval suite hammers (`pass^k`, must-always-escalate at 100%).*

## Interface
```
evaluate_escalation(state: PatientState) -> EscalationDecision
```
`EscalationDecision`: `escalate` (bool), `urgency` ("urgent" | "gp_soon" | "routine"),
`reasons` (list[{code, message}]), `suggested_wording` (str).

## Must-always-escalate classes (each is a reason code; ANY true → escalate)

| Code | Condition | Urgency | Source |
|---|---|---|---|
| `SUSPECTED_AKI` | AKI check returns suspected_aki=True | urgent | aki_thresholds.md |
| `EGFR_BELOW_30` | eGFR < 30 | gp_soon (urgent if new/rapid) | nice_ng203 referral |
| `ACR_70_OR_MORE` | ACR ≥ 70 mg/mmol | gp_soon | nice_ng203 referral |
| `RAPID_EGFR_FALL` | sustained/rapid fall in eGFR (see def) | gp_soon | nice_ng203 |
| `KFRE_OVER_5PCT` | 5-year KFRE risk > 5% | gp_soon | nice_ng203 referral |
| `HB_ANAEMIA` | Hb ≤ 110 g/L (or anaemia symptoms) | gp_soon | nice_ng203 anaemia |
| `NEW_SIGNIFICANT_SYMPTOM` | significant new symptom flagged | gp_soon (urgent if red-flag) | PRD §4.11 |

### Definitions
- **RAPID_EGFR_FALL:** a sustained decrease in eGFR of ≥ 25% (and a category change) or a sustained
  fall of ≥ 15 ml/min/1.73m² within 12 months. (PRD "sustained or rapid fall"; **flag for clinician
  confirmation** of exact NICE numeric threshold before pilot — encoded conservatively.)
- **Suspected AKI** always maps to `urgent`.

## Urgency resolution
- If any `urgent` reason → overall urgency `urgent`.
- Else if any reason → `gp_soon`.
- Else → not escalate, urgency `routine`.

## Bias rule
- When a required input is missing but a partial signal suggests risk, prefer to **escalate with a
  softer wording** ("worth contacting your practice to check") rather than stay silent. Recall over
  precision. Document as an explicit tradeoff.

## Wording
- Calm, specific, non-alarmist. Urgent wording points to same-day GP / NHS 111 / urgent care as
  appropriate. Never a personalised prescribing instruction. Always the "educational support, does
  not replace your GP or care team" framing.

## Scenarios
- eGFR 28, ACR 40 → escalate, reasons {EGFR_BELOW_30}, urgency gp_soon.
- ACR 85 → escalate {ACR_70_OR_MORE}.
- suspected_aki=True → escalate {SUSPECTED_AKI}, urgency urgent.
- eGFR 55, ACR 10, Hb 130, no symptoms → **not** escalate, routine.
- Hb 108 → escalate {HB_ANAEMIA}.
- eGFR 25 + suspected_aki=True + ACR 90 → escalate, urgency urgent, 3 reason codes.
```
