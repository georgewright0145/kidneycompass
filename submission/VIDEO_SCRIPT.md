# KidneyCompass — 5-minute video script & shot-list

**Target: ≤ 5:00. Narration ~700 words (~150 wpm). Track: Agents for Good.**
Record the demo beats live in `agents-cli playground` first (they're all verified working), then screen-record over the narration. Keep the trace panel visible during the demo so judges see the deterministic tool calls.

---

### 0:00–0:35 — Hook + problem (talking head or title card)

**On screen:** Title "KidneyCompass — classify, don't diagnose." Then a stat card: *1 in 10 UK adults · ~44% undiagnosed · £7bn/year.*

**Narration:**
"More than one in ten UK adults has chronic kidney disease — and about 44% of them don't know it, because it's silent until it's late and expensive. People can now see their kidney blood tests in the NHS App, but as raw numbers with no meaning. A creatinine spike during a chest infection looks exactly like the disease getting worse. KidneyCompass closes that gap: it takes whatever results a person has, tells them what they mean, and speaks up the moment a clinician is needed — without ever pretending to be one."

### 0:35–1:05 — Why an agent + the core idea

**On screen:** One line animates in: **"Classify, don't diagnose. Inform generically, route every decision to the clinician."**

**Narration:**
"Why an agent? Because interpreting scattered results, separating an acute event from a chronic trend, and turning that into the right question for a GP is exactly the multi-step reasoning agents are good at. But a clinical agent has one dangerous failure mode: reasoning that's wrong but looks right. So the central decision is this — the model never owns a clinical number. Classification, the AKI check, the risk equation, the escalation gate — all of it is deterministic Python. The model only understands messy input and explains the result in plain English."

### 1:05–1:45 — Architecture (diagram)

**On screen:** The architecture diagram — root orchestrator → four sub-agents; a box highlighting `engines/` (deterministic gates) and the two callbacks; the MCP server feeding the guidance agent.

**Narration:**
"Here's the shape. A root orchestrator delegates to four specialist agents — classification, escalation, guidance, and appointment-prep — built with Google's ADK. Underneath sits a layer of deterministic engines: they're plain, unit-tested code, so they're auditable and can't be prompt-injected into a wrong answer. Two guarantees wrap the model: one callback refuses prescribing requests *before* the model runs; another guarantees any safety escalation reaches the user, even if the model gets distracted. A scoped MCP server serves the versioned NICE and KDIGO guideline text, so thresholds come from curated sources, never model memory."

### 1:45–3:35 — Demo (screen recording of the playground; this is the heart)

**Beat 1 — Classification (0:20).** Type: *"My eGFR is 38 and urine ACR is 12 mg/mmol — what does this mean and how often should I be monitored?"*
> Narration: "It classifies against KDIGO — G3bA2, red band — and gives the NICE monitoring interval. Watch the trace: the category came from a deterministic tool call, not the model."

**Beat 2 — AKI caught + held out (0:30).** Type: *"My creatinine was 80 on Jan 1 and 130 on Jan 3. I had a chest infection that week."*
> Narration: "Now the important one. A sudden creatinine rise — the app flags a suspected acute kidney injury, tells the person it's separated that reading from their long-term trend and risk estimate so it isn't misread as decline, and escalates urgently. This is the signature of an AKI, caught in the numbers."

**Beat 3 — The refusal (0:20).** Type: *"Should I stop taking my metformin?"*
> Narration: "Try to make it prescribe, and it won't. It refuses the personal instruction and routes you to your GP — while still explaining, generically, that metformin is one clinicians review at this kidney function. That refusal is deterministic code, so it can't be talked around."

**Beat 4 — Honest risk + what-if (0:25).** Type: *"I'm 70, male, eGFR 35, ACR 40 — what's my dialysis risk, and what if I lowered my ACR?"*
> Narration: "It gives a five-year kidney-failure risk — about 7.4% — using a UK-calibrated equation, then recalculates honestly for a lower ACR. It only moves the number using real equation inputs; it won't fake it."

**Beat 5 — MCP grounding (0:15, optional).** Type: *"What does the guideline say the ACR referral threshold is?"*
> Narration: "And when it quotes a threshold, it looks it up from the versioned guideline text through the MCP server — and cites the source."

### 3:35–4:25 — The build & the rigor

**On screen:** Quick montage — the six green eval suites; the KFRE validation line (C = 0.930); `agents-cli` commands; the CI security gate.

**Narration:**
"How was it built? Spec-driven and green-first, on Vertex AI with Gemini 2.5 Flash, using the Agents CLI to scaffold, evaluate, and run it. Every clinical threshold was written from source into a spec folder before any feature code. Safety is proven, not asserted: six deterministic evaluation suites run as gates — must-always-escalate, must-detect-AKI, must-not-over-refer, classification and risk accuracy, and a red-team refusal suite — all passing on every run, alongside a security scan. And the risk equation? The UK constants weren't published in plain form, so rather than invent them, I re-derived the UK calibration on a 35,000-patient cohort and validated it — a concordance of 0.93. A wrong risk number would be worse than none."

### 4:25–5:00 — Close

**On screen:** The one-liner again + "Educational support. It classifies and informs — it never prescribes."

**Narration:**
"KidneyCompass is deliberately educational self-management support — it classifies rather than diagnoses, and informs rather than prescribes, which is what keeps it both useful and defensible. It's an agent for good aimed at a disease the system chronically under-catches: giving patients interpretation, early recognition of the things that matter, and the confidence to act at the right moment. Thanks for watching."

---

## Production notes
- **Length discipline:** if tight, cut Beat 5 (MCP) — it's marked optional; the architecture segment already establishes MCP.
- **Show the trace panel** during Beats 1–2 so the deterministic tool calls are visible — it's the whole thesis.
- **Antigravity:** not used — don't mention it. **Deployability:** if asked, say "deploy-ready with reproducible docs; the playground is the demo," which the rules explicitly allow.
- Upload to YouTube (public/unlisted per competition rules) and attach to the Kaggle media gallery. Add a cover image (the architecture diagram works well).
