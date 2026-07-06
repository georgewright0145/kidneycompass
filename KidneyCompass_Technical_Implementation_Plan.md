# KidneyCompass — Technical Implementation Plan

*Companion to the KidneyCompass PRD. Grounds the build in the Google 5-Day AI Agents Intensive whitepapers (Day 1 New SDLC / vibe coding, Day 2 Agent Tools & Interoperability, Day 3 Agent Skills, Day 4 Security & Evaluation, Day 5 Spec-Driven Production). Build stack: GCP + Vertex AI Agent Engine, Antigravity (agentic IDE), the `google-agents-cli`, and an agentic coding model (Claude / Fable) as the executor. This document is written to be handed to the executor.*

---

## 0. How to use this document

This is the build spec. The executor (Fable) should treat the PRD as the "what" and this plan as the "how." Two rules apply throughout, both taken straight from the course:

- **Spec-driven, not vibe-only** (Day 1 / Day 5). Humans are architects who write the specs (test specs, escalation specs, eval sets); the agent does the heavy lifting of writing the code against them. Do not free-build past the spec.
- **Beware the version-cutoff trap** (Day 5, explicit warning). Coding models fall back to training-cutoff versions (for example suggesting an old Gemini string). Before writing any code, confirm the current model names on Vertex, the current `google-agents-cli` version, and the current ADK version, and pin them. Feed the current NICE NG203 / KDIGO 2024 source text into the spec folder so the agent reasons from current guidance, not its training data.

Credentials for GCP, Vertex, and any MCP servers will be provided at the point each is needed.

---

## 1. Agents-for-Good framing

CKD is a societal-scale problem: more than one in ten UK adults, roughly 44% undiagnosed without screening, around £7 billion a year to the UK, and a disease that is silent until it is expensive and irreversible. KidneyCompass is an "agent for good" because it puts interpretation, early recognition, and timely routing into the hands of the patient, the one party present between every appointment, without pretending to be a clinician. The societal value is earlier detection and better-managed risk factors at population scale, for a condition the system chronically under-recognises.

---

## 2. Course concepts demonstrated (the submission needs at least three)

The 3–4 hour build (section 6) implements three concepts end to end: **multi-agent ADK, agent skills, and security/evaluation.** MCP is the first stretch (a fourth concept), and A2A is documented as the intended federation pattern rather than built. All five are discussed in the writeup, which is where naming a scoped-out concept deliberately reads as judgement rather than omission.

1. **Multi-agent systems with ADK** (Day 1, Day 2, Day 5) — *built.* An orchestrator with specialist sub-agents, using ADK's graph-based workflow and multi-agent delegation, coordinated through shared session state.
2. **Agent Skills** (Day 3) — *built.* A governed clinical skills library (SKILL.md + scripts + references) using progressive disclosure, with the description field as the routing algorithm.
3. **Security and evaluation** (Day 4, Day 5) — *built.* A do-not-answer red-team refusal suite for the prescribing class, a must-always-escalate / must-detect-AKI golden set through the `agents-cli eval run` gate, a Semgrep + git-secrets scan, and deterministic gates that cannot be prompt-injected because they are code.
4. **MCP servers** (Day 2) — *stretch.* A minimal clinical-knowledge MCP server exposing a guideline-lookup tool, consumed "USB-C" style.
5. **A2A** (Day 2) — *documented.* The cross-boundary delegation pattern for the phase-3 primary/secondary-care federation.

---

## 3. Target architecture

### 3.1 The core pattern: deterministic gates in graph nodes, LLM for language
This is the single most important design decision, and it is a direct lift of the Day 4 expense-triage lab. In that lab, expenses under £100 are auto-approved in plain Python (bypassing the LLM), and anything above routes to a human via the request-input API. KidneyCompass applies the same shape to a clinical domain:

- The **high-stakes logic runs as deterministic business logic inside ADK graph nodes**: KDIGO classification (eGFR + ACR → category and risk band), the AKI check (timestamped creatinine change against thresholds), the KFRE calculation (UK-calibrated), and the escalation decision. These are Python, not model judgement, so they are auditable and cannot hallucinate.
- The **LLM handles language only**: understanding messy natural-language input, and explaining the deterministic outputs in plain, calm English.
- **Escalation is the human-in-the-loop route.** When a gate fires (suspected AKI, eGFR < 30, ACR ≥ 70, and so on), the graph routes to an escalation node that produces the "contact your GP / seek urgent care" output with suggested wording. This is the clinical analogue of the expense agent's human-review branch.

State the mapping explicitly in the writeup: it is the course's flagship pattern applied to an agent for good.

### 3.2 Multi-agent topology
An ADK root orchestrator with LLM-driven delegation to specialist sub-agents. Coordination is through shared session state for the common path, MCP for tool and knowledge access, and A2A reserved for the cross-boundary federation case (see note).

- **Orchestrator (root LlmAgent).** Owns the conversation, routes to sub-agents, holds session state, and enforces the do-not-answer class before anything else runs.
- **Intake & normalisation agent.** Parses labs, home BP, HbA1c, Hb, bone profile, meds, symptoms, fluid, and uploaded documents. Normalises units (ACR in mg/mmol), attaches timestamps and any context note, writes to session state. Uses the document/OCR MCP tool for uploaded letters.
- **Classification & risk agent.** Calls the deterministic classification, monitoring-frequency, and KFRE engines (graph nodes). Returns the KDIGO category, risk band, monitoring interval, and the 5-year risk with valid ACR/eGFR what-ifs.
- **AKI & data-quality agent.** Runs the deterministic AKI check against timestamps and baseline, separates suspected-AKI readings from the chronic trend and from KFRE, and drives the "were you unwell?" context capture.
- **Guidance agent.** Medication (inform-and-route flags, sick-day education, additional-medication prompts), lifestyle (from the lifestyle skill and its references), and the "how to do an ACR correctly" education. Retrieves from the clinical-knowledge MCP server.
- **Escalation agent.** The deterministic escalation gate plus the human-in-the-loop output. This is the safety core and is evaluated hardest.
- **Appointment-prep agent.** Assembles the summary, the prioritised question list, and the one-page output, tailored for a GP or a renal-clinic visit.

**A2A note.** For the capstone slice, sub-agents coordinate through shared session state and MCP, which is the simplest correct pattern (Day 5). A2A ("factory radio," Day 2) is the right layer for the phase-3 primary/secondary-care federation, where a secondary-care agent would be a separate deployed agent the orchestrator delegates to across a boundary. Build it as an explicit A2A boundary only if there is time; otherwise document it as the intended federation pattern, which still demonstrates understanding of the concept.

### 3.3 Agent skills library
Each clinical capability is a skill (Day 3): a directory with a SKILL.md whose description is the routing algorithm, plus `scripts/` for deterministic work, `references/` for guideline text loaded on demand, and `assets/` for output templates. Progressive disclosure keeps only the short descriptions in context until a skill triggers.

Skills to build (kebab-case names, gerund where natural):
- `classifying-ckd` — eGFR + ACR → KDIGO category and risk band; `scripts/classify.py` holds the deterministic mapping; `references/kdigo_thresholds.md` and `references/nice_monitoring.md`.
- `recognising-aki` — timestamped creatinine-change check; `scripts/aki_check.py`; `references/aki_thresholds.md`.
- `estimating-kfre-risk` — UK-calibrated KFRE; `scripts/kfre.py` (4-variable, UK recalibration constants); `references/kfre_notes.md` (inputs, caveats, what is and isn't a valid what-if).
- `reviewing-medications` — renal dose-review flags and sick-day rules; `references/renal_meds.md`; inform-and-route only.
- `advising-lifestyle` — targeted lifestyle guidance; `references/ukka_exercise_lifestyle.md` (from the UKKA guideline), `references/kidney_care_uk.md`.
- `explaining-acr-test` — how to collect an ACR correctly.
- `preparing-appointment` — GP and renal-clinic prep; `assets/appointment_summary_template.md`.
- `finding-cases` — NICE testing risk factors → "ask your GP for an eGFR and ACR."

Each SKILL.md description front-loads trigger keywords and states explicitly what the skill is not for. Note the course finding that a badly written skill can perform worse than no skill, so descriptions and anti-triggers get real attention, and skills are evaluated under co-loaded conditions.

### 3.4 MCP tool layer
Consume MCP servers rather than hardwiring tools (Day 2).

- **Clinical-knowledge MCP server** (custom, scoped tightly). Serves the versioned, dated, clinician-reviewed guideline content (KDIGO 2024, NICE NG203/TAs, UKKA lifestyle, AKI thresholds, KFRE calibration). Exposes two retrieval modes in parallel, not as a cascade: exact-term / full-text for anything that must match precisely (thresholds, ACR in mg/mmol, drug names) and vector for natural-language questions. Scope the server to this project only.
- **Data-store MCP.** For patient values, timestamps, and context notes. Default to Vertex AI Agent Engine's durable Sessions and Memory Bank (course-aligned, least moving parts). If you prefer a queryable store, use the MCP Toolbox for Databases over BigQuery.
- **Document / OCR MCP.** For parsing uploaded results letters and ultrasound reports.

### 3.5 Deterministic engines (the safety core)
Plain, tested Python behind the graph nodes and the skill scripts:
- `classify.py` — KDIGO CGA mapping and risk band.
- `aki_check.py` — creatinine rise ≥ 26 µmol/L within 48h, or ≥ 1.5× baseline within 7 days; returns a suspected-AKI flag and holds the reading out of the trend.
- `kfre.py` — UK-recalibrated 4-variable KFRE; refuses to run on unstable / suspected-AKI values; exposes only ACR and eGFR as recalculable what-ifs.
- `escalation.py` — the threshold ruleset; returns escalate / do-not-escalate plus a reason code. This is the gate the eval suite hammers.

### 3.6 Data & memory
Vertex AI Agent Engine Sessions for conversation state and Memory Bank for durable per-user memory (classification history, values with timestamps, context notes, medicines, data-completeness). This is the Day 5 Tier-3 "custom ADK agent on Agent Engine" path, which is the correct tier here because the app needs cross-run memory and the worst case of getting it wrong is high.

### 3.7 Web frontend
A thin web app (the capstone interface). Keep the agent logic server-side on Agent Engine; the frontend is a conversational UI plus simple result-entry and a summary view. A2UI (Day 2, "generative display window") is an option for rendering structured outputs like the classification card or the appointment summary, but it is optional for the slice. Use Antigravity's built-in isolated-browser subagent to run and verify the UI end to end.

---

## 4. Security and evaluation (Day 4)

Treat this as first-class, not a final gate. The course frame: **security tells you the agent stayed inside the boundary; evaluation tells you whether what happened inside is worth shipping.** Both run inside the SDLC via CI, not at the end.

**Effective trust, applied.** The high-stakes decisions do not depend on model trust at all, because they are deterministic. That is the strongest possible security posture for a clinical agent: the classification, AKI, KFRE, and escalation gates cannot be prompt-injected into a wrong answer, because they are code.

**Static scanning and supply chain.** Wire Snyk and Semgrep for code vulnerabilities and git-secrets for credential leaks into CI. Scan dependencies and check provenance to guard against slop-squatting (hallucinated malicious package names). Every generated dependency is scanned before it lands.

**Skill trust tiers and skill cards.** Give each skill a trust tier and a machine-readable skill card (author, access, limitations). The clinical skills are first-party and reviewed; treat any third-party skill as untrusted until scanned. The skill inspector checks for code vulnerabilities and prompt injection.

**Do-not-answer red-team suite.** A scripted adversarial set that tries to make the agent diagnose, prescribe, or issue a personalised dose change, and confirms it refuses and routes to the clinician every time. This is the security analogue of the clinical do-not-answer class.

**Policy gate in front of tool calls.** A policy-server pattern (Day 5) that checks every tool call, in particular anything that would write to a record or emit a clinical directive, so the agent cannot act outside its authority.

**Trajectory evaluation.** Instrument with OpenTelemetry for full traces (Day 4). Score the path, not just the output: a correct "contact your GP" reached through a wrong tool sequence still fails. Also track iteration count, latency, and cost, since a correct answer reached via ten self-repair loops is a weaker result than one reached cleanly.

**Golden sets and the coverage gate.** Build labelled eval sets: a must-always-escalate set, a must-detect-AKI set, a classification set with UK-unit and unstable-value edge cases, and a KFRE set. Run them through `agents-cli eval run` as a CI gate. `pass^k` on the escalation and AKI skills: they must fire on every run, not most.

**Vibe diff for sensitive changes.** For changes to the clinical content or the gates, produce a human-readable security/eval report and require clinician sign-off before it ships. This is the Day 4 "vibe diff" approval pattern applied to clinical governance.

**Red / blue / green in CI.** Red team attacks (the refusal suite), blue/green observes and fixes, all inside the pipeline so security is part of development rather than a bolt-on.

---

## 5. Repo structure and scaffolding

Bootstrap with the course toolchain:

```
uvx google-agents-cli setup        # installs the seven skills into the coding agent
agents-cli scaffold                # spec-driven project generation
```

Target layout:

```
kidneycompass/
├── spec/                          # the architect-written specs (source of truth)
│   ├── escalation_spec.md         # every must-escalate rule, in Gherkin-style scenarios
│   ├── classification_spec.md
│   ├── aki_spec.md
│   ├── kfre_spec.md
│   └── guidelines/                # current NICE NG203 / KDIGO 2024 source text (RAG, anti-cutoff)
├── agents/
│   ├── orchestrator/agent.py
│   ├── intake/agent.py
│   ├── classification_risk/agent.py
│   ├── aki_dataquality/agent.py
│   ├── guidance/agent.py
│   ├── escalation/agent.py
│   └── appointment_prep/agent.py
├── engines/                       # deterministic Python (graph-node logic)
│   ├── classify.py
│   ├── aki_check.py
│   ├── kfre.py
│   └── escalation.py
├── skills/                        # agentskills.io structure
│   ├── classifying-ckd/
│   ├── recognising-aki/
│   ├── estimating-kfre-risk/
│   ├── reviewing-medications/
│   ├── advising-lifestyle/
│   ├── explaining-acr-test/
│   ├── preparing-appointment/
│   └── finding-cases/
├── mcp/
│   ├── clinical_knowledge_server/ # scoped custom MCP server
│   └── config/                    # MCP consumption config
├── evals/
│   ├── must_escalate.evalset.json
│   ├── must_detect_aki.evalset.json
│   ├── classification.evalset.json
│   └── kfre.evalset.json
├── security/
│   ├── redteam_refusal_suite/
│   ├── skill_cards/
│   └── ci/                        # snyk, semgrep, git-secrets config
├── web/                           # thin conversational frontend
└── deploy/                        # Agent Engine config, CI actions
```

---

## 6. Build sequence — the 4-hour build, green-first

The constraint is roughly four hours of agentic-coder time. The right read is that the code volume is achievable: because every clinical threshold is already specified in the PRD and this plan, Fable implements rather than researches, and `agents-cli` automates the scaffold, eval, and deploy boilerplate. So aim for the fuller build, not a token slice.

The real risk in a timed agent build is not feature count, it is the environment and deployment loop: a version-cutoff mismatch, an ADK/CLI scaffold mismatch, a model that isn't available in the chosen Vertex region, or an Antigravity deploy that loops instead of erroring. So the sequencing rule is **green-first**: reach a working, demoable agent early, then treat everything after as upside. Deployment stays off the critical path, and the demo runs from the local `agents-cli playground`, which is the submittable artifact alongside the code link.

**Phase 0 — de-risk the environment first (~20 min), before any feature code.**
- Confirm and pin the current model, `agents-cli`, and ADK versions. Do not accept training-cutoff defaults.
- Verify the chosen Gemini Flash is actually available in your Vertex region before committing to it. This is the failure that has cost time before.
- Scaffold with `agents-cli`; drop the guideline thresholds from this plan into `spec/guidelines/`.

**Phase 1 — GREEN checkpoint: a working agent you could submit (~90 min).**
- Deterministic engines with a failing test first: `classify.py`, `aki_check.py`, `kfre.py`, `escalation.py`.
- Root orchestrator + classification-risk sub-agent + escalation sub-agent, with the engines wired as deterministic graph nodes and the AKI check folded into the classification path. Gemini Flash for language; the gates use no model.
- Three skills: `classifying-ckd`, `recognising-aki`, `estimating-kfre-risk`.
- One `must_escalate` evalset through `agents-cli eval run`.
- Run it in `agents-cli playground`. At this point you have a demoable artifact and three course concepts. Everything below is upside.

**Phase 2 — harden and widen (~60 min).**
- Security: the do-not-answer red-team refusal file (tries to make it prescribe, confirms it refuses and routes), a `must_detect_aki` evalset, and a Semgrep + git-secrets scan.
- More skills: `reviewing-medications`, `advising-lifestyle`, then `explaining-acr-test`, `preparing-appointment`, `finding-cases` if quick.
- The guidance and appointment-prep sub-agents.

**Phase 3 — upside, in order (~30 min onward).**
- MCP (fourth concept): a minimal FastMCP clinical-knowledge server exposing a single guideline-lookup tool, consumed by the guidance path.
- Deploy: `agents-cli deploy` to Agent Engine, then smoke-test. Only now, because it is the flaky step. If it loops, stop and submit from the playground.

**Record the video** against whatever green state you reached: a patient entering messy results, the KDIGO classification and risk band, an AKI spike caught and held out of the trend, a refusal on "should I stop my metformin," and an escalation firing.

**Not in the four hours (name these in the writeup as scoped-out):** the custom web frontend (the playground is the UI), the primary/secondary A2A federation, HealthKit / Health Connect (PRD phase 2), and deeper NHS integration (PRD phase 3).

---

## 7. Deployment and observability

- **Deploy** with `agents-cli deploy` to Vertex AI Agent Engine (reuse the existing GCP project; clean up the orphaned reasoning-engine resources first). Durable Sessions and Memory Bank are the runtime.
- **Observability**: OpenTelemetry traces for every run, surfaced for the trajectory evals and for the missed-escalation / missed-AKI review described in the PRD monitoring plan.
- **CI**: eval gate and security scans run on every change; the clinical-content and gate changes require the vibe-diff sign-off.

---

## 8. Execution notes for the coding agent (Fable)

- Confirm current versions before coding (models, `agents-cli`, ADK). Do not accept training-cutoff defaults. Cross-check any version string.
- Reason from the guideline text in `spec/guidelines/`, not from training data, for any clinical threshold. If a threshold isn't in the spec, stop and ask rather than inventing one.
- Never let the LLM own a clinical number. Classification, AKI, KFRE, and escalation are deterministic Python; the model explains, it does not decide.
- Keep the MCP server scoped to this project with least privilege.
- Write the failing test first for any gate behaviour, keep it in the repo, and fix only the root cause.
- Do not generate real patient data. Use a synthetic golden set for evals and the demo.

---

## 9. Decisions (locked)

1. **Model.** Cheapest capable model where it fits: the deterministic gates use no model at all (free and instant), and the current Gemini Flash handles all language. Move to a larger model only if an eval shows Flash failing a specific task.
2. **Scope.** Aim for the fuller build in section 6, sequenced green-first, with deployment off the critical path and the demo run from the `agents-cli playground`.
3. **A2A.** Not built. Coordinate through shared session state; document A2A as the phase-3 primary/secondary federation pattern (grounded in Day 5: shared session state for simple coordination, A2A for cross-boundary delegation).
4. **Data store.** Quickest: ADK session state locally, and Agent Engine managed Sessions / Memory Bank if the deploy stretch is reached. No separate database for the build.
5. **Synthetic data.** Confirmed: synthetic patient data only, for evals and the demo. No real patient data anywhere.
