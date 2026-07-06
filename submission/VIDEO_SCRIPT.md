# KidneyCompass — 5-minute video script & shot-list

**Target: ≤ 5:00. Narration ~700 words (~150 wpm). Track: Agents for Good.**
Record the demo beats live in `agents-cli playground` first (they're all verified working), then screen-record over the narration. Keep the trace panel visible during the demo so judges see the deterministic tool calls.

---

### 0:00–0:35 — Hook + problem (talking head or title card)

**On screen:** Title "KidneyCompass — classify, don't diagnose." Then a stat card: *1 in 10 UK adults · ~44% undiagnosed · £7bn/year.*

**Narration:**
"More than one in ten UK adults has chronic kidney disease. Around 44% of them have no idea, because it stays silent until it's late — and expensive. You can now see your kidney results in the NHS App, but they're just numbers with nothing attached. Is an eGFR of 38 fine, or frightening? And a creatinine spike during a chest infection looks exactly like the disease getting worse. KidneyCompass fills that gap. It makes sense of whatever results you have, and it speaks up the moment you should call your GP — without ever pretending to be one."

### 0:35–1:15 — What you can bring + the core idea

**On screen:** Input chips animate in around a phone — *blood & urine results · home BP & weight · symptoms · medicines · scans & letters* — then the line: **"Classify, don't diagnose. Inform generically, route every decision to the clinician."**

**Narration:**
"Most people show up with a bit of a muddle — a blood test from the GP, a home blood-pressure monitor, a hospital letter they never quite understood, a bag of tablets. You can give KidneyCompass any of it. Your eGFR and urine ACR, your haemoglobin, your blood pressure, your symptoms, your medicines, even a photo of a scan letter. Nothing's required, there's no long form, and one value is enough to start — it just gets sharper the more you add. But here's the important bit: interpreting all that is exactly where a clinical agent could get it wrong but sound right. So the rule underneath everything is that the model never owns a clinical number. The classification, the AKI check, the risk equation, the escalation — that's all deterministic code. The model just understands what you typed, and explains the answer in plain English."

### 1:15–1:50 — Architecture (diagram)

**On screen:** The architecture diagram — inputs → root orchestrator → four sub-agents; a highlighted `engines/` (deterministic gates) and the two callbacks; the MCP server feeding the guidance agent.

**Narration:**
"Here's how it fits together. Whatever you bring flows into a root orchestrator, which hands off to four specialist agents — classification, escalation, guidance, and appointment-prep — built with Google's ADK. Underneath them sits a layer of deterministic engines. That's the safety core: plain, tested code, so it can't be talked into a wrong answer. Two guards wrap the model — one refuses prescribing before the model even runs, the other makes sure a safety warning always reaches you. And a small MCP server serves the actual NICE and KDIGO guideline text, so any threshold it quotes comes from a real source, not the model's memory."

### 1:50–3:35 — Demo (screen recording of the playground; this is the heart)

**Beat 1 — Classification (0:20).** Type: *"My eGFR is 38 and urine ACR is 12 mg/mmol — what does this mean and how often should I be monitored?"*
> Narration: "Give it a couple of results and it classifies them against KDIGO — G3bA2, red band — and tells you how often NICE says to get checked. Keep an eye on the trace: that category came from a code tool call, not the model guessing."

**Beat 2 — AKI caught + held out (0:30).** Type: *"My creatinine was 80 on Jan 1 and 130 on Jan 3. I had a chest infection that week."*
> Narration: "This is the one that matters most. A sudden jump in creatinine — it flags a suspected acute kidney injury, tells you it's set that reading aside so it doesn't drag down your trend, and says get seen promptly. That's an AKI, caught right there in the numbers, where it usually gets missed."

**Beat 3 — The refusal (0:20).** Type: *"Should I stop taking my metformin?"*
> Narration: "Now try to make it prescribe. It won't. It hands the decision back to your GP — but it still tells you, generally, that metformin is one clinicians review at this level of kidney function. And that refusal is code, so you can't talk it around."

**Beat 4 — Honest risk + what-if (0:25).** Type: *"I'm 70, male, eGFR 35, ACR 40 — what's my dialysis risk, and what if I lowered my ACR?"*
> Narration: "It gives a five-year kidney-failure risk — about 7.4% — using a UK-calibrated equation, then recalculates honestly for a lower ACR. It only moves the number using real equation inputs; it won't fake it."

**Beat 5 — MCP grounding (0:15, optional).** Type: *"What does the guideline say the ACR referral threshold is?"*
> Narration: "And when it quotes a threshold, it looks it up from the versioned guideline text through the MCP server — and cites the source."

### 3:35–4:25 — The build & the rigor

**On screen:** Quick montage — the six green eval suites; the KFRE validation line (C = 0.930); `agents-cli` commands; the CI security gate.

**Narration:**
"A quick word on how it's built, because it's the part I'm proudest of. It runs on Vertex AI with Gemini 2.5 Flash, scaffolded and evaluated with the Agents CLI. Every clinical threshold was written down from source before any feature code went in. And the safety isn't a claim — it's tested. Six evaluation suites run as gates: never miss an escalation, never miss an AKI, never over-refer someone who's stable, classify correctly, get the risk right, and refuse every attempt to make it prescribe. They all pass on every run. The risk equation is my favourite example: the UK constants weren't published in a form I could just drop in, so instead of inventing them, I re-derived the calibration on a cohort of 35,000 patients and checked it held up — a concordance of 0.93. An unverified number would have been worse than none."

### 4:25–5:00 — Close

**On screen:** The one-liner again + "Educational support. It classifies and informs — it never prescribes."

**Narration:**
"So that's KidneyCompass. It's deliberately educational support — it classifies, it doesn't diagnose; it informs, it doesn't prescribe. That's the line that keeps it both genuinely useful and defensible. It takes a disease we catch far too late, and gives the one person who's there for all of it — the patient — a way to understand their numbers and act at the right moment. Thanks for watching."

---

## Production notes
- **Length discipline:** if tight, cut Beat 5 (MCP) — it's marked optional; the architecture segment already establishes MCP.
- **Show the trace panel** during Beats 1–2 so the deterministic tool calls are visible — it's the whole thesis.
- **Antigravity:** not used — don't mention it. **Deployability:** if asked, say "deploy-ready with reproducible docs; the playground is the demo," which the rules explicitly allow.
- Upload to YouTube (public/unlisted per competition rules) and attach to the Kaggle media gallery. Add a cover image (the architecture diagram works well).
