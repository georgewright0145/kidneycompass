# KidneyCompass — a CKD companion that classifies, informs, and never prescribes

**Track: Agents for Good**
*A companion for people in the UK living with, or at risk of, chronic kidney disease. It makes sense of whatever results you already have, classifies them against KDIGO 2024, notices an acute kidney injury hiding in the numbers, and tells you when it's worth calling your GP — without ever pretending to be one.*

## The problem

Chronic kidney disease is common, quiet, and badly under-recognised. More than one in ten UK adults has it, and yet roughly 44% of people with CKD don't know, because it rarely causes symptoms until it is advanced. That silence is the cruel part. The early years, when treatment does the most good, are exactly the years when nothing feels wrong. Catch it early and the right medicines and blood-pressure control can slow progression by about a third. Miss that window and the disease drifts toward kidney failure — at a cost to the NHS of around £7 billion a year.

People can finally see their own kidney results in the NHS App. But a number with no explanation doesn't change anything. Is an eGFR of 38 fine, or frightening? Does an ACR of 12 need acting on? And when creatinine jumps during a chest infection, it looks identical to the disease getting worse — so a temporary blip gets mistaken for decline, or real decline gets waved away as "probably just that bug." The gap sits in two places: between appointments, where no one helps you interpret your numbers, and inside the ten-minute appointment, where it's hard to know what to even ask.

## What a patient brings — and why it helps them

Most people arrive with a muddle: a blood test from the surgery, a home blood-pressure monitor, a hospital letter they never fully understood, a bag of tablets. KidneyCompass takes any of it. **Nothing is required, and there is no long form to fill in.** A single value is enough to begin; the more you add, the sharper the picture becomes.

- **Blood and urine results** — eGFR and urine ACR, the two numbers that drive the classification, plus HbA1c, haemoglobin, and a bone profile if you have them.
- **Home readings** — blood pressure, weight, and fluid intake, followed as trends rather than one-off snapshots.
- **Your symptoms and your medicines, in plain words** — swelling, breathlessness, passing less urine; and the tablets you take each morning, which drive a gentle medicines review.
- **Letters and scans** — an ultrasound report or clinic letter, summarised in plain English. It explains what a scan is for; it does not try to second-guess the radiologist.
- **The story around a reading** — "I was in hospital with pneumonia that week." It uses that to set a misleading result aside instead of letting it distort your trend.

Every input is optional, and the app degrades gracefully. Give it only an eGFR and it classifies what it can, then asks for a urine ACR. Give it the whole folder and it pulls the picture together — genuinely useful if your results are scattered across a GP and a kidney clinic and no one has ever put them side by side. It gets more useful the more it knows, and honest about what it can't yet conclude.

## Why an agent

Interpreting scattered results, telling an acute event apart from a slow trend, noticing when a value crosses a referral threshold, and turning all of that into the right question for a GP — that is exactly the messy, multi-step reasoning agents are suited to. And the patient is the one person present at every appointment, so it makes sense to put interpretation and timely routing in their hands.

But a clinical domain has a specific danger: reasoning that is wrong yet sounds right. So the central rule is that the model never owns a clinical number.

## The solution, and its architecture

**Classify, don't diagnose. Inform generically, and route every decision to the clinician.**

CKD classification is arithmetic against a published rubric: a given eGFR and ACR map to exactly one KDIGO category and one risk band. That is not clinical judgement, so KidneyCompass does it — and everything that follows from it — in deterministic Python. The language model (Gemini 2.5 Flash on Vertex AI) does two things only: it understands messy input, and it explains the result in calm, plain English.

This is the course's flagship pattern — deterministic gates for the decisions, the model for the words — applied to health:

- **Deterministic engines** (`engines/`) hold the classification and risk band, the AKI check (a creatinine rise of ≥26 µmol/L in 48 hours, or ≥1.5× baseline in 7 days), the UK-calibrated risk equation, the escalation rules, and the medication and referral flags. All of it is plain, unit-tested code — auditable, and impossible to prompt-inject into a wrong answer, because it isn't the model deciding.
- **A multi-agent ADK system**: a root orchestrator delegates to four specialists — classification-and-risk, escalation (the safety core), guidance, and appointment-prep — coordinating through shared session state.
- **Two guarantees wrap the model**: one callback refuses personalised prescribing or diagnosis before the model even runs; another makes sure that if a safety rule fires, the warning reaches the person — even if the model got distracted and started asking a follow-up question first.

So when someone types *"creatinine was 80 on Monday, 130 on Wednesday, I had a chest infection,"* the AKI engine flags a suspected acute kidney injury, holds that reading out of the long-term trend and the risk estimate, says so plainly, and urges prompt care. And when someone asks *"should I stop my metformin?"*, it won't give a personal instruction — it routes them to their GP, while still explaining, in general terms, that metformin is one clinicians review at that level of kidney function.

## Course concepts demonstrated (four in code — the minimum is three)

| Concept | Where | Proof |
|---|---|---|
| **Multi-agent system (ADK)** | `app/agent.py`, `app/sub_agents/` | Root orchestrator delegates to four specialists via shared session state |
| **MCP server** | `mcp/clinical_knowledge_server/` | Scoped FastMCP server serves versioned KDIGO/NICE text (exact-term + full-text) over stdio — thresholds retrieved, never recalled |
| **Security** | `app/guardrails.py`, `security/` | Deterministic prescribing-refusal guard + 10-case red-team suite (incl. injection) + Semgrep & secret CI gate |
| **Agent Skills (Agents CLI)** | `skills/` | Eight governed skills (SKILL.md + references + trust cards); scaffolded, evaluated and demoed with `agents-cli` |

Antigravity was not used (the build ran on `agents-cli` and an agentic coding model), and a live deployment is optional upside — the project is deploy-ready, and the demo runs from the `agents-cli playground`.

## How it was built

Two choices shaped the work. First, spec before code: every clinical threshold was written into `spec/guidelines/` from source before any feature was built, so the agent reasons from current guidance rather than the model's memory. Second, evaluation as the point rather than a formality — six deterministic eval suites run as gates, and each failure was treated as a real finding (the one AKI case the agent first "named but didn't escalate" is what drove the guaranteed-delivery callback).

The risk equation is the sharpest example of the project's temperament. The UK-recalibrated constants weren't published in a form I could just drop in, and the rule was firm: never invent a clinical number. So the engine simply refused to compute — until the real sources arrived. I read the actual coefficients from a calculator's source, then re-estimated the UK baseline survival on the 35,539-patient Major 2019 cohort and checked it held up: a concordance (Harrell's C) of 0.930, with the UK survival sitting higher than the North-American version, exactly as the published work predicts. A wrong risk number would have been worse than none.

## Results (all verifiable in the repo)

- **104 unit tests** pass on the deterministic engines and eval metrics.
- **Six deterministic eval suites, all passing:** never-miss-escalation (8/8), never-miss-AKI (6/6), never-over-refer (7/7), classification accuracy (10/10), risk accuracy (6/6), adversarial refusal (10/10) — the safety-critical three held to pass^k (they must pass on every run).
- **KFRE validation: Harrell's C = 0.930** on the 35,539-patient cohort.
- **Security:** 0 Semgrep findings, 0 secrets; `.env` and patient data never committed.

*Reproduce with `pytest tests/unit/` and `bash security/ci/run_security_and_eval.sh`.*

## Honest by design

KidneyCompass is deliberately educational and self-management support: it classifies rather than diagnoses, and informs rather than prescribes. The dialysis-risk explorer recalculates only from the two real equation inputs, eGFR and ACR, and it explains — rather than fakes — how things like stopping smoking or improving blood pressure actually lower risk over time. All clinical content is versioned and flagged pending UK renal-clinician sign-off; a real NHS deployment would still need DTAC, DCB0129 clinical-safety governance, and an information-governance review. No real patient data ships in the repository.

## What you can try

The whole agent runs locally from the `agents-cli playground`. Hand it messy results and watch it classify them; give it a creatinine spike and watch it catch the AKI and hold it out of the trend; ask it to get you ready for a kidney-clinic appointment; then try to make it prescribe — it won't. It classifies and it informs, and it never prescribes. That one line is what keeps it both genuinely useful and defensible.
