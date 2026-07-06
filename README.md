# KidneyCompass

A patient-facing, natural-language **chronic kidney disease (CKD) companion for the UK / NHS**. It
classifies against **KDIGO 2024**, informs generically from **NICE NG203**, recognises acute kidney
injury, estimates dialysis risk honestly, and routes every clinical decision back to the clinician.

> **Core principle: classify, don't diagnose. Inform generically, route the decision to the
> clinician.** It never issues a personalised instruction to start, stop, or change a medicine.

Built for the Google 5-Day AI Agents Intensive capstone on **Vertex AI + Gemini 2.5 Flash** with the
`agents-cli` / ADK toolchain. See `KidneyCompass_PRD.md` (the "what") and
`KidneyCompass_Technical_Implementation_Plan.md` (the "how").

## The one design decision that matters

**Deterministic gates for the high-stakes logic; the LLM only handles language.** KDIGO
classification, the AKI check, the KFRE calculation, and the escalation gate are plain, tested Python
in `engines/` — they cannot be hallucinated or prompt-injected into a wrong answer, because they are
code. The model understands messy input and explains the deterministic output in calm, plain English.

Two output-side guarantees back this up:
- **Do-not-answer guard** (`app/guardrails.py`, a `before_model_callback`) refuses personalised
  prescribing/diagnosis *before the model runs*.
- **Escalation delivery** (`app/escalation_delivery.py`, an `after_model_callback`) guarantees any
  fired safety gate reaches the final response, even if the model tried to ask for more data first.

## Architecture

```
Root orchestrator (LlmAgent, do-not-answer guard)
├── classification_risk_agent   → classify_ckd · check_aki · estimate_dialysis_risk · assess_escalation
├── escalation_agent            → assess_escalation                     (the safety core's voice)
├── guidance_agent              → review_medicines · check_referral · [MCP] lookup_guideline
└── appointment_prep_agent      → prepare_appointment

engines/     deterministic clinical logic (classify, aki_check, kfre, escalation, guidance, appointment)
skills/      8 governed clinical skills (SKILL.md + references + trust cards)
spec/        architect specs + spec/guidelines/ (versioned guideline text — the only source of thresholds)
mcp/         FastMCP clinical-knowledge server (exact-term + full-text guideline lookup, stdio)
evals/       must-escalate / must-detect-AKI / refusal golden sets (deterministic, pass^k)
security/    red-team refusal suite, skill cards, CI gate
```

Course concepts: **multi-agent ADK**, **agent skills**, **security & evaluation** (all built), plus
**MCP** (built, 4th concept). A2A is documented as the phase-3 primary/secondary-care federation.

## Run it

```bash
agents-cli install                       # create the project venv (google-adk 2.3.0, gemini-2.5-flash)
agents-cli playground                     # interactive UI  — the submittable demo artifact
agents-cli run "eGFR 38, ACR 12 mg/mmol — what does this mean?"   # one-shot
```

Environment (Vertex + Gemini, ADC): `.env` pins `GOOGLE_CLOUD_LOCATION=us-east1` and the model is
`gemini-2.5-flash` (verified served there — see `VERSIONS.md`).

## Verify (the gates)

```bash
.venv/bin/python -m pytest tests/unit/ -q          # 89 deterministic-engine + metric tests
bash security/ci/run_security_and_eval.sh          # SAST + secrets + must-escalate / must-detect-AKI / refusal (pass^k)
```

| Gate | Result |
|---|---|
| Unit tests | 89 pass |
| must_escalate (8) · must_detect_aki (6) · refusal (10) | mean 1.0 each (pass^k) |
| Semgrep SAST · detect-secrets (source) | 0 findings |

## Known open items (deliberate for a capstone)

- Clinical thresholds are **bootstrapped from the PRD appendix**, pending UK renal-clinician sign-off.
- **UK KFRE recalibration constants not yet supplied** — `engines/kfre.py` refuses to compute a risk
  rather than invent one (`UK_KFRE_CONSTANTS` slot ready).
- Deployment to Agent Engine is optional upside; the local `agents-cli playground` is the demo.
- Out of scope (PRD phases 2–3): web frontend, HealthKit/Health Connect ingestion, A2A federation,
  deep NHS integration.
