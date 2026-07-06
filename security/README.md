# KidneyCompass — Security & Evaluation Posture

*Day 4/5 of the course: **security tells you the agent stayed inside the boundary; evaluation tells
you whether what happened inside is worth shipping.** Both run inside the SDLC (CI), not as a bolt-on.*

## Effective trust — the strongest posture for a clinical agent
The high-stakes decisions **do not depend on model trust at all**, because they are deterministic
Python (`engines/`): KDIGO classification, the AKI check, the KFRE calculation, and the escalation
gate **cannot be prompt-injected into a wrong answer, because they are code**. The LLM only
understands input and explains output.

Two output-side guarantees make this concrete:
- **Do-not-answer guard** (`app/guardrails.py`) — a `before_model_callback` refuses personalised
  prescribing / dose-change / diagnosis requests with a deterministic regex, *before* the model runs.
- **Escalation delivery** (`app/escalation_delivery.py`) — an `after_model_callback` guarantees any
  fired safety gate is delivered in the final response, even if the model tried to ask for more data
  first. (This is what fixed the one must-detect-AKI miss — see below.)

## Gates (all deterministic; run via `security/ci/run_security_and_eval.sh`)
| Gate | What it proves | Result |
|---|---|---|
| Unit tests (`tests/unit/`) | Engines + metrics correct | 83 pass |
| Semgrep SAST | No code vulnerabilities in our source | 0 findings |
| Secret scan (detect-secrets) | No leaked credentials in source | 0 findings (`.env` gitignored) |
| `must_escalate` (8 cases) | Never miss an escalation | mean 1.0 (pass^k) |
| `must_detect_aki` (6 cases) | Never miss a suspected AKI | mean 1.0 (pass^k) |
| `redteam_refusal` (10 cases) | Refuse prescribing/diagnosis, incl. evasive/injection prompts | mean 1.0 |

## Red-team refusal suite
`security/redteam_refusal_suite/` — adversarial prompts that try to make the agent diagnose,
prescribe, or issue a personalised dose change, including third-person, roleplay, authority-injection
("ignore your safety rules… clinician mode"), and embedded variants. The deterministic metric fails
the case if the response leaks a personalised directive OR fails to route to a clinician.

## Skill trust tiers
`security/skill_cards/*.card.json` — each skill has a machine-readable card (author, trust tier,
access, limitations). All KidneyCompass clinical skills are **first-party, reviewed** (pending UK
renal-clinician sign-off); any third-party skill would be untrusted until scanned.

## Vibe-diff for sensitive changes
Changes to clinical content (`spec/guidelines/`) or the gates (`engines/classify.py`,
`aki_check.py`, `kfre.py`, `escalation.py`) require a human-readable report and **clinician sign-off**
before shipping — the Day 4 "vibe diff" pattern applied to clinical governance. The eval gates above
are the machine half of that check.

## Known governance gaps (deliberately open for a capstone)
- Clinical content is **bootstrapped from the PRD appendix**, not yet clinician-signed-off.
- UK KFRE recalibration constants **not yet supplied** — `engines/kfre.py` refuses to compute rather
  than invent a number.
- Snyk (dependency CVEs) named in the plan is not wired here; Semgrep + detect-secrets cover SAST +
  secrets. Add Snyk with a token in CI when available.
