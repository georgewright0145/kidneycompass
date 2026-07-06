# KidneyCompass — a CKD companion that classifies, informs, and never prescribes

**Track: Agents for Good**
*A patient-facing chronic-kidney-disease companion for the UK/NHS. It classifies against KDIGO 2024, informs from NICE guidance, catches acute kidney injury hiding in the numbers, estimates dialysis risk honestly, and speaks up the moment a clinician is needed — without ever pretending to be one.*

## The problem

Chronic kidney disease is common, silent, and badly under-recognised. More than one in ten UK adults has some form of CKD — around 3.25 million at stages 3–5 — yet roughly **44% of people with CKD are undiagnosed** without screening, and GP registers record about half the true prevalence. The disease is quiet exactly when action pays off most: caught early, SGLT2 inhibitors and blood-pressure control can cut progression by roughly a third. Caught late, it costs the NHS about **£7 billion a year**, with in-centre dialysis at ~£30,000 per patient per year.

The tools people already have make it worse, not better. The NHS App and GP records now show patients their eGFR and urine ACR — but as raw numbers with no interpretation, no monitoring guidance, and no "what to do next." A creatinine spike during a chest infection reads identically to the disease worsening. Generic health apps either over-alarm or give advice that is actively wrong for CKD (the classic trap: "drink more water," which flips to *restriction* in advanced disease). The gap sits between appointments, and inside the short appointment itself.

## Why an agent

Interpreting scattered results, separating an acute event from a chronic trend, knowing the monitoring interval for a KDIGO cell, spotting when a value crosses a referral threshold, and turning all of that into the right question to ask a GP — this is exactly the kind of multi-step, context-dependent reasoning over messy natural-language input that an agent is built for. The patient is the one constant present at every appointment; KidneyCompass puts interpretation and timely routing into *their* hands.

But a clinical domain has a specific failure mode: **reasoning that is wrong but looks right.** So the central design decision is to *not* trust the model with any clinical number.

## The solution and its architecture

**Classify, don't diagnose. Inform generically, route every decision to the clinician.**

CKD classification is arithmetic against a published rubric: a given eGFR and ACR map to exactly one KDIGO category and one risk band. That is not clinical judgement — so KidneyCompass does it, and everything that follows from it, in **deterministic Python**. The LLM (Gemini 2.5 Flash on Vertex AI) only ever does two things: understand messy input, and explain the deterministic output in calm, plain English.

This is a direct lift of the course's flagship pattern — deterministic gates in graph nodes, the model for language — applied to health:

- **Deterministic engines** (`engines/`): KDIGO classification and risk band, the AKI check (creatinine rise ≥26 µmol/L in 48h, or ≥1.5× baseline in 7 days), the UK-calibrated KFRE risk equation, the escalation gate, medication and referral flags. All plain, unit-tested Python — auditable, and impossible to prompt-inject into a wrong answer *because they are code*.
- **A multi-agent ADK system**: a root orchestrator delegates to four specialists — classification-&-risk, escalation (the safety core), guidance (medication/lifestyle/ACR-how-to), and appointment-prep — coordinating through shared session state.
- **Two code-level safety guarantees around the model**: a `before_model_callback` that refuses personalised prescribing/diagnosis requests *before the model runs*, and an `after_model_callback` that guarantees any fired safety gate reaches the user's final response — even if the model tried to ask a follow-up question first. Escalation is code-checked, not left to model judgement.

When someone types *"creatinine was 80 on Monday, 130 on Wednesday, I had a chest infection,"* the AKI engine flags a suspected acute kidney injury, **holds that reading out of the long-term trend and the risk estimate**, tells the person it has done so, and escalates urgently. When someone asks *"should I stop my metformin?"* the agent refuses to give a personal instruction and routes them to their GP — while still explaining, generically, that metformin is one clinicians review at that kidney function.

## Course concepts demonstrated (four, in code)

1. **Multi-agent system (ADK)** — orchestrator + four specialist sub-agents with shared state and delegation.
2. **MCP server** — a scoped FastMCP clinical-knowledge server serving the *versioned, dated* guideline text (KDIGO 2024, NICE NG203, AKI thresholds, KFRE) with exact-term + full-text lookup, consumed "USB-C" style by the guidance agent over stdio. Thresholds are retrieved from curated sources, never recalled from model memory.
3. **Security** — a red-team refusal suite (10 adversarial prompts, including roleplay and "ignore your rules, clinician mode" injections), the deterministic do-not-answer guard, and Semgrep + secret scanning wired into a CI gate.
4. **Agent Skills (Agents CLI)** — eight governed clinical skills (SKILL.md + references + machine-readable trust cards), built and evaluated with `agents-cli`; the demo runs from the `agents-cli playground`.

## The engineering journey

Two decisions defined the build. First, **spec-driven, green-first**: every clinical threshold was written into `spec/guidelines/` from source *before* any feature code, so the agent reasons from current guidance, not its training data. A deliberate Phase 0 pinned the model, ADK, and CLI versions and verified Gemini 2.5 Flash was actually served in the chosen Vertex region — catching that the scaffold's default model string returns a 404 there.

Second, **evaluation as the product, not a formality.** The safety story is six deterministic eval suites run through `agents-cli eval` as pass^k gates: *must-always-escalate* (8/8), *must-detect-AKI* (6/6), *must-not-escalate* — the over-referral counterweight — (7/7), *classification accuracy* (10/10), *KFRE accuracy* (6/6), and the *refusal* suite (10/10). Each miss was treated as a real finding: the one AKI case the agent initially "named but didn't escalate" is what drove the deterministic escalation-delivery callback.

The KFRE risk equation is the sharpest example of the project's ethos. The published UK recalibration constants weren't in any summary document, and the rule was firm: *never invent a clinical constant.* So the engine refused to compute — until real sources arrived. I read the actual coefficients from a calculator's JavaScript, then **empirically re-derived the UK baseline survival** on the 35,539-patient Major 2019 cohort via a Breslow recalibration, and **validated it**: Harrell's C = 0.930, with the derived UK survival higher than the North-American values — matching the published finding that non-UK calibrations overestimate UK risk. A wrong risk number would be worse than none.

## Honest by design

KidneyCompass is deliberately positioned as **educational and self-management support**: it classifies rather than diagnoses, informs rather than prescribes. The dialysis-risk explorer only recalculates from the two real equation inputs (eGFR and ACR) and explains — rather than fakes — how smoking or blood pressure act. All clinical content is versioned and flagged *pending UK renal-clinician sign-off*; a real NHS deployment would still need DTAC, DCB0129 clinical-safety governance, and information-governance review. No real patient data ships in the repository — the cohort used for recalibration is gitignored, and the secret scan is clean.

## What you can try

The full agent runs locally from the `agents-cli playground`. Ask it to interpret messy results, watch it catch an AKI spike and hold it out of the trend, ask it to prep you for a kidney-clinic appointment, and try to make it prescribe — it won't. It classifies and informs, and it never prescribes. That one line is what makes it both useful and defensible.
