# KidneyCompass

A patient-facing, natural-language **chronic kidney disease (CKD) companion for the UK / NHS**. It
classifies against **KDIGO 2024**, informs generically from **NICE NG203**, recognises acute kidney
injury hiding in the numbers, estimates dialysis risk honestly, and routes every clinical decision
back to the clinician.

> **Core principle: classify, don't diagnose. Inform generically, route the decision to the
> clinician.** It never issues a personalised instruction to start, stop, or change a medicine.

Kaggle 5-Day AI Agents Intensive capstone · **Track: Agents for Good** · Vertex AI + **Gemini 2.5
Flash** · ADK + `agents-cli`.

---

## 📋 For reviewers — start here

| | |
|---|---|
| **What it is** | A CKD companion where the LLM never owns a clinical number — every high-stakes decision is deterministic, audited Python. |
| **Writeup** | [`submission/WRITEUP.md`](submission/WRITEUP.md) (Agents for Good) |
| **Video script** | [`submission/VIDEO_SCRIPT.md`](submission/VIDEO_SCRIPT.md) |
| **See it work (no setup)** | [`submission/DEMO_TRANSCRIPTS.md`](submission/DEMO_TRANSCRIPTS.md) — real agent I/O for 6 scenarios |
| **Evidence the gates pass** | [`docs/EVALUATION.md`](docs/EVALUATION.md) — 104 unit tests + 6 pass^k eval suites |
| **Run it yourself** | `agents-cli install && agents-cli playground` (60-second verify below) |

### Course concepts demonstrated — map to the code (need 3; **4 built**)

| Concept | Built? | Where | One-line proof |
|---|---|---|---|
| **Multi-agent system (ADK)** | ✅ | [`app/agent.py`](app/agent.py) + [`app/sub_agents/`](app/sub_agents/) | Root orchestrator delegates to 4 specialist ADK agents via shared session state |
| **MCP server** | ✅ | [`mcp/clinical_knowledge_server/`](mcp/clinical_knowledge_server/) | FastMCP server serves versioned NICE/KDIGO text; consumed by the guidance agent over stdio |
| **Security** | ✅ | [`app/guardrails.py`](app/guardrails.py), [`security/`](security/) | Deterministic prescribing-refusal guard + 10-case red-team suite + Semgrep/secret CI gate |
| **Agent Skills (Agents CLI)** | ✅ | [`skills/`](skills/) | 8 governed skills (SKILL.md + references + trust cards); built/evaluated with `agents-cli` |
| Antigravity | — | — | Not used (built with `agents-cli` + Claude Code) |
| Deployability | ◐ | [`deploy` path in docs](#deployability) | Deploy-ready with reproducible steps; playground is the demo (deployment not required for judging) |

---

## The one design decision that matters

**Deterministic gates for the high-stakes logic; the LLM only handles language.** A clinical agent's
worst failure is *reasoning that is wrong but looks right*. So KDIGO classification, the AKI check,
the KFRE calculation, and the escalation gate are plain, unit-tested Python in
[`engines/`](engines/) — they cannot be hallucinated or prompt-injected into a wrong answer, because
they are code. The model (Gemini 2.5 Flash) only understands messy input and explains the
deterministic output in calm, plain English.

Two output-side guarantees wrap the model:
- **Do-not-answer guard** ([`app/guardrails.py`](app/guardrails.py), a `before_model_callback`)
  refuses personalised prescribing/diagnosis *before the model runs*.
- **Escalation delivery** ([`app/escalation_delivery.py`](app/escalation_delivery.py), an
  `after_model_callback`) guarantees any fired safety gate reaches the final response — even if the
  model tried to ask a follow-up first. Escalation is code-checked, not left to model judgement.

## What makes this different

- **Safety by construction, proven with evals.** Six deterministic eval suites run as `pass^k`
  gates (see [`docs/EVALUATION.md`](docs/EVALUATION.md)): never-miss-escalation, never-miss-AKI,
  never-over-refer, classification accuracy, risk accuracy, and adversarial refusal.
- **A clinical risk equation, empirically re-derived and validated.** The UK-recalibrated KFRE
  wasn't available as ready constants, and the rule was *never invent a clinical number*. So the
  engine refused to compute — until real sources arrived, then the UK baseline survival was
  re-estimated on the **35,539-patient Major 2019 cohort** (Breslow recalibration) and **validated:
  Harrell's C = 0.930**. Method + validation: [`spec/kfre_recalibration/RESULTS.md`](spec/kfre_recalibration/RESULTS.md).
- **Honest by design.** The dialysis-risk explorer only recalculates from real equation inputs
  (eGFR, ACR) and *explains* — rather than fakes — how smoking or BP act. All clinical content is
  versioned and flagged pending UK renal-clinician sign-off. No real patient data ships (the cohort
  CSV is gitignored; the secret scan is clean).

## Architecture

```
                        patient · natural language
                                   │
                 ┌─────────────────▼──────────────────┐
   before_model  │        Root Orchestrator           │  after_model
   guard (refuse │        (Gemini 2.5 Flash)          │  guarantee
   prescribing)  └─────────────────┬──────────────────┘  (escalation lands)
                     delegates (multi-agent ADK)
        ┌──────────────┬───────────┼───────────┬───────────────┐
        ▼              ▼           ▼            ▼
 Classification   Escalation    Guidance   Appointment
   & Risk        (safety core)              Prep
        └──────────────┴─────┬─────┴───────────┘
                             ▼
        Deterministic clinical engines (code — auditable, not prompt-injectable)
        classify · aki_check · kfre · escalation · guidance · appointment
                             ▼
        MCP clinical-knowledge server — versioned NICE NG203 / KDIGO text
```

## Repository guide

| Path | What's there |
|---|---|
| [`app/`](app/) | ADK agents: orchestrator, 4 sub-agents, tools, the two safety callbacks, MCP client |
| [`engines/`](engines/) | The deterministic clinical logic — the safety core |
| [`spec/guidelines/`](spec/guidelines/) | Versioned guideline text — the **only** source of clinical thresholds |
| [`spec/kfre_recalibration/`](spec/kfre_recalibration/) | The KFRE UK-recalibration method, results (C=0.930), reproducible script |
| [`skills/`](skills/) | 8 governed clinical skills (progressive disclosure + trust cards) |
| [`mcp/`](mcp/) | FastMCP clinical-knowledge server |
| [`tests/`](tests/) | 104 unit tests + 6 deterministic eval golden sets and metrics |
| [`security/`](security/) | Red-team refusal suite, skill cards, CI gate, posture writeup |
| [`docs/EVALUATION.md`](docs/EVALUATION.md) | Full evidence table for every gate |
| `KidneyCompass_PRD.md` / `..._Technical_Implementation_Plan.md` | Background: the vision and the build plan |

## Run it

```bash
agents-cli install     # project venv (google-adk 2.3.0, google-genai 2.10.0, python 3.13)
agents-cli playground  # interactive UI at http://127.0.0.1:8080/dev-ui/?app=app
# or one-shot:
agents-cli run "My eGFR is 38 and urine ACR is 12 mg/mmol — what does this mean?"
```

Environment (Vertex + ADC): `.env` pins `GOOGLE_CLOUD_LOCATION=us-east1`; model `gemini-2.5-flash`,
verified served there (see [`VERSIONS.md`](VERSIONS.md)). No API keys in the repo — auth is ADC.

## Verify in 60 seconds

```bash
# Offline, instant — the deterministic safety core + metrics:
.venv/bin/python -m pytest tests/unit/ -q            # 104 pass

# Full gate (needs Vertex ADC) — security scans + all 6 clinical eval suites:
bash security/ci/run_security_and_eval.sh
```

| Gate | Cases | Result |
|---|---|---|
| Unit tests (engines + metrics) | 104 | ✅ pass |
| `must_escalate` (never miss an alert) | 8 | ✅ mean 1.0 (pass^k) |
| `must_detect_aki` (never miss an AKI) | 6 | ✅ mean 1.0 (pass^k) |
| `must_not_escalate` (never over-refer) | 7 | ✅ mean 1.0 |
| `classification` accuracy | 10 | ✅ mean 1.0 |
| `kfre_accuracy` (±2pp of the engine) | 6 | ✅ mean 1.0 |
| `redteam_refusal` (adversarial + injection) | 10 | ✅ mean 1.0 |
| Semgrep SAST · detect-secrets (source) | — | ✅ 0 findings |

<a name="deployability"></a>
## Deployability

Deployment isn't required for judging, and the demo runs from the playground. The project is
**deploy-ready**: it scaffolds to Vertex AI Agent Engine with

```bash
agents-cli scaffold enhance . --deployment-target agent_runtime
agents-cli deploy
```

`Dockerfile` and `app/fast_api_app.py` are generated and committed; Sessions/Memory Bank are the
managed runtime. See [`security/README.md`](security/README.md) for the CI/eval-gate wiring.

## Known open items (deliberate for a capstone)

- Clinical thresholds are **bootstrapped from the PRD appendix** and the KFRE constants are
  **cohort-derived** — both flagged **pending UK renal-clinician sign-off**.
- Out of scope (PRD phases 2–3): custom web frontend, HealthKit/Health Connect ingestion, A2A
  primary/secondary-care federation (documented, not built), deep NHS integration.

*Educational and self-management support. It classifies and informs; it never diagnoses or prescribes.*
