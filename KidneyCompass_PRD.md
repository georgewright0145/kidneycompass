# KidneyCompass — Product Requirements Document (UK / NHS) — v3

*A chronic kidney disease (CKD) patient companion for the NHS and UK primary care. Classification framework: KDIGO 2024 (CGA staging and risk heat-map). Management framework: NICE NG203 (2021, updated Nov 2024), NICE TA775 and TA942.*

**In one line:** a natural-language app that helps people in the UK who live with, or are at risk of, chronic kidney disease pull together whatever results and readings they have, understand where those numbers place them, know how often to monitor and what to raise, prepare for appointments, and act at the right moment. It follows KDIGO for classification and NICE for management, and it never prescribes or stands in for the care team.

---

## Core design principle — read this first

**Classify, don't diagnose. Give generic information, and route the decision to the clinician.**

CKD classification is numerical and deterministic: a given eGFR and ACR map to exactly one KDIGO category and one cell of the risk heat-map. That is arithmetic against a published rubric, not clinical judgement. KidneyCompass does that classification and everything that follows deterministically from it: the monitoring frequency for the category, the generic risk-factor and lifestyle guidance, and generic guideline-based statements about what is usually indicated at that stage. Where guidelines point to an additional medication, it says so generically and hands the decision back to the clinician (for example: *"guidelines suggest an SGLT2 inhibitor is usually recommended at your level of kidney function; additional medication may be needed, so please speak to your GP."*). It never issues a personalised instruction to start, stop, or change a dose. That one line, inform generically and route the prescribing decision to a clinician, is what keeps the product both useful and defensible.

---

## 1\. Working backwards press release

### Headline

KidneyCompass helps people catch a silent disease, and manage it, while the NHS can still change its course.

### Sub-headline

A conversational app that pulls together whatever kidney results and readings a person has, classifies their CKD against KDIGO, tells them how often to monitor and what to raise, spots an acute kidney injury hiding in the trend, and speaks up the moment something needs a clinician. It informs and routes; it does not prescribe.

### Problem statement

Chronic kidney disease is common in the UK, silent until late, and under-recognised by patients and clinicians alike. More than one in ten UK adults has some form of CKD, around 3.25 million at stages 3–5, yet a large share don't know. A UK primary-care screening study of people aged 60 and over found CKD in roughly 18% of that group, and that about 44% of everyone living with CKD was undiagnosed without screening. It is under-recorded in the system too, with GP-register prevalence (\~4%) sitting well below the true figure (\~8.5%). The disease is quiet exactly when action pays off most, and the tools that could help, the NHS App and GP online records, show people raw numbers with no meaning attached. Kidney disease already costs the UK around £7 billion a year, most of it NHS spend, and the bill rises steeply once someone reaches kidney failure. The gap sits between appointments, and inside the short appointment itself, where patients struggle to know what matters and what to ask.

### Solution description

KidneyCompass is a patient-facing app with a natural-language interface. People bring whatever they have: eGFR and urine ACR, home blood-pressure readings, HbA1c, haemoglobin, a bone profile, an ultrasound report, their medicines list, symptoms, fluid intake, even smartwatch data. Every input is optional; the app works with what it's given and gets more useful as more arrives. It classifies the person's CKD against the KDIGO categories and risk heat-map, explains it in plain English, tells them how often NICE suggests they should be monitored, and gives targeted risk-factor and lifestyle guidance from trusted UK sources. It recognises the signature of an acute kidney injury in a sudden creatinine change and separates it from the long-term trend. It estimates their five-year risk of needing dialysis and shows, honestly, which factors they can influence. It lets them add context to a result ("I was in hospital with pneumonia"), prepares them for GP and renal-clinic appointments, and, for people under both a GP and a kidney specialist, brings both sets of results into one place. And it watches: when something crosses a threshold that needs a clinician, it says so clearly. It classifies and informs, and it never prescribes.

### Customer quotes

*(Illustrative, for the press-release format.)*

"I had a folder of results that meant nothing to me. It told me I was at what KDIGO calls G3bA2, in the amber risk band, that I should be checked twice a year, and that it was worth asking whether I should be on one of the newer kidney medicines. I walked into my appointment knowing what to ask." — *CKD patient, illustrative*

"It flagged that my creatinine spike lined up with the week I had pneumonia, and told me it had left that reading out of my trend. That's the kind of thing that gets misread as my kidneys getting worse." — *CKD patient, illustrative*

### Getting started

1. Download the app and answer a few short questions. Do you have a CKD diagnosis or risk factors like diabetes, high blood pressure, or cardiovascular disease? What results or readings do you have to hand?  
2. Enter or photograph whatever you have, or import from the NHS App or GP online records. Nothing is required; add what you can.  
3. See your plain-English KDIGO classification and risk band, with how often you should be monitored.  
4. Ask it to prep you before your next GP or kidney-clinic appointment.  
5. From then on it watches with you, and tells you when it's time to contact your practice.

---

## 2\. Customer problem statement

### The problem in detail

CKD is defined as a sustained reduction in kidney function (eGFR below 60 ml/min/1.73m²) and/or kidney damage (ACR of 3 mg/mmol or more), lasting more than three months. KDIGO classifies it by cause, GFR category (G1–G5), and albuminuria category (A1–A3), and places the combination on a risk heat-map running from low (green) to very high (red). The defining feature, and the core problem, is that CKD is largely asymptomatic until its final stages, while the risk of kidney failure, cardiovascular events, and death rises from the early categories. That produces a blind spot on both sides of the consulting-room door.

- **Patients don't know, and can't interpret what they can see.** About 44% of people with CKD are undiagnosed without screening. Those who are diagnosed can now see their eGFR and ACR in the NHS App or GP records, but a number with no interpretation changes nothing.  
- **Primary care under-records and under-manages it.** Register prevalence (\~4%) is roughly half true prevalence (\~8.5%). In one urban analysis fewer than half of people meeting CKD criteria were coded, and about 30% of those on registers had suboptimal management, meaning uncontrolled or unknown blood pressure.  
- **Clinician awareness and confidence lag.** UK qualitative research has repeatedly found GPs reluctant to apply the CKD label, especially at stage 3, with wide variation in understanding. Studies of advanced CKD found GPs had little hands-on experience and wanted clearer referral guidance, and researchers built a dedicated questionnaire specifically to measure primary-care confidence and knowledge in CKD relative to other conditions. (See the appendix.)  
- **Acute events get misread as chronic decline.** A creatinine spike during an illness can look like the disease worsening if nobody separates the acute from the chronic, skewing both the trend and any risk estimate.  
- **Two gaps: between appointments, and inside them.** Nothing helps patients stay engaged with their numbers between contacts, and nothing helps them get the most from a short appointment when they do. For people under both a GP and a renal clinic, results are scattered across two systems.

### Current limitations

The NHS App and GP records show raw numbers with no interpretation, no monitoring guidance, and no "what to do next." Symptom-based awareness fails by design, because waiting for symptoms means waiting until it's late. Generic health apps either over-alarm or under-alert, and their one-size-fits-all advice can be actively wrong for CKD, with fluid intake the classic trap. Nothing bridges "here are my scattered results" to "here's your KDIGO classification, how often to monitor, what's worth raising, and when to ring the practice."

### Customer impact

Caught late or left to drift, CKD progresses faster toward kidney failure, drives more cardiovascular events, and carries a real quality-of-life and mental-health burden in advanced disease, at heavy NHS cost. In-centre haemodialysis is roughly £30,000 per patient per year, and dialysis alone costs the NHS over £1 billion annually. The counterfactual is endorsed by both NICE and KDIGO: early, active management works. SGLT2 inhibitors cut the risk of CKD progression by roughly a third irrespective of diabetes, and ACE inhibitors, ARBs, and blood-pressure control remain foundational. The impact of the current gap is avoidable progression: changeable outcomes missed because no one was watching the quiet signals or helping the patient act on them.

---

## 3\. Success metrics

### Customer experience

Comprehension: the share of active users who can correctly state their KDIGO category, risk band, and monitoring frequency. Confidence to act: self-reported confidence in knowing when to contact the GP, at baseline versus 30 and 90 days. Appointment value: the share of users who use appointment prep before a visit, and how useful they found it. Case-finding: for at-risk, undiagnosed users, the share prompted to request an eGFR and ACR who then report having been tested. And the safety-critical measure, escalation quality: appropriate escalations confirmed sensible on clinical review, and above all missed escalations, including missed AKI, which is the metric the product is optimised against.

### Business and system metrics

Activation, retention (D30 and D90), the share logging at least one value a month, education and lifestyle-module engagement, and a recommendation score. Data-completeness handling is its own metric: the share of sessions that deliver a useful result despite partial data. Agent quality is tracked through escalation precision and recall, AKI-detection recall, do-not-answer adherence, refusal correctness on out-of-scope prescribing requests, and classification accuracy against a labelled set. A UK-relevant efficiency signal: reduction in duplicate blood tests for co-managed patients, and appropriate (not excess) referrals surfaced.

### Long-term indicators

The share of engaged users with controlled or improving BP and ACR trends, and time-to-contact after a flagged value. Further out, and dependent on NHS partnership and clinical study, the aim is slower eGFR decline and delayed progression, plus earlier and better-informed appointments that reduce downstream cost.

---

## 4\. Requirements

### 4.1 Data model and inputs — everything is optional

The app is built around a sparse, mixed data model. **No input is mandatory.** Each one adds value, the app degrades gracefully, and it states what it can and cannot conclude from what it has. Every reading carries a **timestamp** (needed for trends and AKI detection) and can carry a **context note** (see 4.5).

**Laboratory results**

- **eGFR** (ml/min/1.73m²): the G axis, and the primary driver of classification, monitoring, medication-review flags, and AKI detection.  
- **Urine ACR** (mg/mmol, UK units): the A axis. The earliest marker; drives BP targets, referral thresholds, and the risk estimate.  
- **HbA1c** (mmol/mol): glycaemic control for people with diabetes, tracked with an individualised-target framing and a note that HbA1c becomes less reliable in advanced CKD.  
- **Haemoglobin** (g/L): anaemia tracking. An eGFR under 60 makes a renal cause plausible, and Hb at or below about 110 g/L, or anaemia symptoms, is a "raise with your GP" signal.  
- **Bone profile** (calcium, phosphate, PTH, vitamin D): relevant mainly in later CKD (G4/G5, eGFR under 30), tracked and explained generically, with escalation on out-of-range values.

**Home and vitals**

- **Home blood-pressure readings**: trend tracking against the generic NICE targets for the person's ACR band, with the caveat that home and clinic readings differ and targets are clinic-based.  
- **Weight, fluid intake**: trend context. Fluid guidance stays generic and trusted-source-based (see 4.7).

**Devices**

- **Smartwatch and wearable data**: resting and active heart rate, activity, sleep, and where available BP and SpO2. Used for lifestyle context and trend signals, never as a clinical measurement of record. Automated ingestion via Apple HealthKit and Android Health Connect is phase 2 (see section 7).

**Patient-reported**

- **Symptom log**: free-text and structured symptoms (fatigue, breathlessness, swelling, reduced urine output, and so on), feeding the escalation engine and appointment prep.  
- **Medicines list**: drives the medication module (4.6).

**Documents**

- **Ultrasound report** and other letters: captured, with key findings summarised in plain English and escalation on findings NICE treats as significant. The app explains what an ultrasound is for; it does not reinterpret the radiologist.

### 4.2 Classification and risk framework (KDIGO, numerical not diagnostic)

Map eGFR and ACR to the KDIGO CGA category and place the person on the risk heat-map: green (low risk), amber (moderately increased), orange (high), red (very high). Translate the cell into plain English. State the monitoring frequency that NICE recommends for that category (roughly annual at lower-risk cells, rising to two or more times a year at higher-risk cells), tailored where the person's data supports it. Link to the generic risk-factor guidance for the cell (BP, glycaemia, albuminuria, lipids, lifestyle). Keep ACR in UK units (mg/mmol) as the display, cross-referencing mg/g where a KDIGO threshold is quoted (for example ACR 20 mg/mmol equals about 200 mg/g). Handle missing data openly: if only eGFR is present, classify on the G axis and prompt for a urine ACR. Never invent a category from absent data.

### 4.3 AKI recognition

Acute kidney injury is a medical emergency that hides inside the same numbers the app already tracks, so it is handled as a first-class, deterministic check rather than left to the trend.

- **Detection uses timestamps and change over time**, against the KDIGO / NHS "Think Kidneys" thresholds: a rise in creatinine of 26 µmol/L or more within 48 hours, or a rise to 1.5 times or more of the person's baseline within 7 days (equivalently, an abrupt fall in eGFR). The person's usual stable value is the baseline. Urine-output criteria are not usable outside hospital, so the app relies on the creatinine/eGFR criteria.  
- **On a hit, it escalates**, in plain, calm, urgent language, because AKI needs prompt clinical assessment. It is one of the must-always-escalate classes in the eval suite.  
- **It separates the acute from the chronic.** A suspected-AKI reading is flagged and held out of the long-term CKD trend and out of the five-year risk estimate, so a spike during illness is not misread as the disease worsening. The app says explicitly that it has done this.  
- **It prompts for context** ("were you unwell around this date?") and links to the result-context feature (4.5), and it reminds the person that after an AKI, kidney function should be re-checked and monitored (NICE advises monitoring for at least three years post-AKI).

### 4.4 Five-year kidney-failure (dialysis) risk and modifiable-factor explorer

This estimates the risk of needing dialysis or a transplant, and shows honestly what a person can influence. The honesty of the design matters more than the feature.

- **Baseline estimate** uses the Kidney Failure Risk Equation (KFRE), which predicts 2- and 5-year risk of kidney replacement therapy for CKD stages G3a–G5 from four inputs: **age, sex, eGFR, and ACR**. The app uses the **UK-recalibrated** KFRE, because the original North American calibration overestimates risk in UK patients, and it never runs the estimate on unstable or suspected-AKI values.  
- **Valid what-ifs stay inside the equation.** The only modifiable inputs in KFRE are eGFR and ACR, so the interactive slider shows how risk changes if ACR improves (for example from the A3 into the A2 band) or if eGFR stabilises. That is a real recalculation.  
- **Smoking, HbA1c, and blood pressure are not KFRE inputs**, so the app does not fake a recalculation from them. Instead, a clearly separated "factors you can influence" panel explains, from the evidence, how stopping smoking, improving glycaemic and blood-pressure control, losing excess weight, and starting an SGLT2 inhibitor act by reducing ACR and slowing eGFR decline, which is how they move the risk over time. The app is explicit about which part is a calculation and which part is an evidence-based explanation.  
- **Caveats are shown, not buried**: KFRE does not account for the competing risk of death and can overestimate in older or frailer people, and eGFR/ACR have real day-to-day variability, so the trend matters more than one value.

### 4.5 Data quality: result context, "unwell" flagging, and how to test correctly

Kidney numbers are easy to misread when a value was taken at the wrong moment, so the app treats data quality as a feature.

- **Add context to any result.** The person can annotate a reading in natural language ("in hospital with pneumonia", "bad UTI that week", "did a hard workout the day before"). The app uses this to explain an odd value, to hold illness- or AKI-affected readings out of the trend and the risk estimate, and to prompt a repeat once things have settled.  
- **Flag readings likely to be skewed.** If a value coincides with illness, dehydration, or (for ACR) the specific factors below, the app says the result may not reflect the person's true baseline and suggests confirming when well.  
- **How to do an ACR correctly** (education, because ACR is the early marker and is often collected wrongly): a first-morning urine sample is preferred; avoid vigorous exercise in the 24 hours before; do not collect during a period, a urinary tract infection, a fever, or other acute illness, as these falsely raise it. A single raised ACR is not a diagnosis: a new result between 3 and 70 mg/mmol should be confirmed on a repeat first-morning sample, while a result of 70 mg/mmol or more does not need repeating. The app frames this as helping the person get a reliable test through their GP, not as a home diagnostic.

### 4.6 Medication module (inform and route, never prescribe)

Using the optional medicines list and the person's eGFR, the app gives generic, guideline-based information, never a personalised instruction.

- **Renal dose-review flags.** For medicines clinicians review by kidney function (metformin, reviewed around eGFR 45 and usually stopped below 30; nitrofurantoin, generally avoided below eGFR 45; direct oral anticoagulants, renally dose-adjusted; gabapentinoids, which accumulate), it flags: *"this medicine is one clinicians review at your level of kidney function, so it's worth a medicines review with your GP or pharmacist."* It does not tell the person to change or stop anything.  
- **Sick-day rules education.** Generic education that several common medicines (ACE inhibitors and ARBs, diuretics, SGLT2 inhibitors, metformin, NSAIDs, the "SADMANS" group) are often withheld temporarily during acute dehydrating illness and restarted after recovery, and that this should be agreed with a clinician. Paired with "if you're acutely unwell or unsure, contact your practice or NHS 111." This dovetails with AKI recognition (4.3).  
- **Additional-medication prompts.** Where guidelines point to a treatment the person may not be on, most notably an SGLT2 inhibitor (KDIGO 2024 supports use across essentially the whole eGFR 20–45 band regardless of albuminuria, reflected in UK practice and NICE TA775/TA942), it says so generically and routes to the GP, and reassures on the expected, non-alarming eGFR dip on starting one.  
- **Nephrotoxin and OTC caution.** Generic education to be careful with over-the-counter NSAIDs.

### 4.7 Targeted lifestyle modification (trusted UK sources)

Guidance is targeted to the person's category and drivers but generic in content, drawn from and attributed to the UK Kidney Association *Exercise and Lifestyle in CKD* clinical practice guideline, Kidney Care UK, and NICE. Framing is honest about the evidence, which matters for credibility.

- **Physical activity** (UKKA, adapted from the UK Chief Medical Officers' guidance for this often older, frailer group): some activity is better than none; build toward 150 minutes of moderate activity a week; strength, balance and flexibility work on at least two days; break up long sedentary periods. The proven benefits in CKD are lower blood pressure, better physical function, and better quality of life. The app does not claim exercise directly slows eGFR decline, because the guideline finds that evidence mixed.  
- **Smoking cessation** is the single strongest lifestyle lever for progression (a grade 1A recommendation) and is surfaced accordingly, with signposting to NHS cessation support.  
- **Weight, alcohol, and diet basics**: maintain a healthy weight (both under- and overweight raise risk), keep alcohol within national limits, and follow individualised, professionally supervised dietary advice on salt, potassium and phosphate by severity. No low-protein diets.  
- The framing throughout: "slowing or preventing progression to dialysis" rests mainly on smoking cessation and risk-factor control (BP, glycaemia, albuminuria, SGLT2 inhibitors), with activity adding clear quality-of-life and cardiovascular benefit. All of it is general information from these sources, deferring to the person's care team.

### 4.8 Appointment prep — primary and secondary care

On a prompt like *"I'm seeing my GP soon, help me prepare"* (or the renal clinic), the app assembles the person's current picture: KDIGO classification and risk band, trends since last contact, any suspected-AKI events with context, new or changed symptoms, medicines, and the most recent results, working with whatever data exists. It highlights what's changed and what's worth raising, including guideline-flagged items ("am I on the right medicines for my stage, should I be on an SGLT2 inhibitor?", "is my blood pressure at target for my ACR band?", "should I have a urine ACR done?"). It generates a prioritised question list and a one-page summary. For a renal-clinic visit it tailors the prep to secondary care (for example progression rate, KFRE trajectory, and planning questions). This helps the person communicate; it is not diagnosing.

### 4.9 Primary and secondary care data integration (later-stage CKD)

For people co-managed by a GP and a kidney specialist, the patient is the one constant who attends both, so the app lets them hold both sets of results in one place.

- **One reconciled view** of primary- and secondary-care results, so a test done in clinic isn't repeated at the surgery, and a trend visible in one system isn't missed by the other.  
- **Referral-criteria flagging.** When NICE referral thresholds are met (for example a five-year KFRE risk over 5%, eGFR below 30, ACR of 70 mg/mmol or more, or a sustained rapid fall in eGFR), the app notes that a secondary-care referral may be worth discussing with the GP. It flags the criterion; the clinician makes the referral.  
- **Reducing avoidable tests** is an explicit goal, alongside making sure a crucial trend spanning both settings is not lost.  
- Deep, automated integration with GP and hospital systems (GP Connect, shared care records) is a later phase; in phase 1 the patient assembles the view from what they can access.

### 4.10 Case-finding — helping catch CKD

For users who aren't diagnosed but report NICE testing risk factors (diabetes, hypertension, cardiovascular disease, prior AKI, family history, relevant long-term medicines), the app prompts them to ask their GP for an eGFR and a urine ACR. This is classification and case-finding, not diagnosis: it routes people toward the test and the clinician who diagnoses, and it is a direct contribution to catching CKD earlier.

### 4.11 Escalation engine (the safety core)

A curated set of thresholds and red flags, mapped to KDIGO and NICE, that produces a calm, specific prompt to contact the GP or seek urgent care, with suggested wording. Must-always-escalate classes include suspected AKI, eGFR falling below 30, ACR reaching 70 mg/mmol or more, a sustained or rapid fall in eGFR, a rising five-year KFRE, significant new symptoms, and Hb at or below anaemia thresholds. The engine is tuned for recall and gated deterministically: the decision to escalate is code-checked, not left to model judgement, and when in doubt it errs toward "contact your practice." An explicit do-not-answer class covers diagnosis, individualised prescribing, and acute clinical judgement.

### 4.12 Technical requirements

The model is the 10% and the harness is the 90%. Gemini 2.5 Flash is the base model, and reliability lives in retrieval, guardrails, evaluation, and deployment.

Deployment runs on Vertex AI Agent Engine with a thin web front end, reusing the existing GCP project. UK data residency and NHS information governance are assessed before any real-world pilot.

Retrieval runs in parallel, not as a cascade. Exact-term and full-text retrieval handles anything that must match precisely (lab and medicine names, KDIGO category and ACR thresholds in **mg/mmol**, NICE referral criteria, KFRE inputs, AKI thresholds), alongside vector retrieval for natural-language questions. UK units are a safety-critical exact-match concern: the app must never silently treat mg/mmol as mg/g.

Deterministic engines sit under the soft model layer for the high-stakes decisions: KDIGO classification, the AKI check, the KFRE calculation (UK-calibrated), and the escalation gate are all rule-based, with the model explaining rather than deciding. The clinical content (KDIGO 2024, NICE NG203 and the technology appraisals, the UKKA lifestyle guideline, KFRE calibration, AKI thresholds, and trusted-source lifestyle material) is versioned, dated, exact-term indexed, and clinician-reviewed, with a defined refresh process, because guidance moves.

State persists classification, values and their timestamps, context notes, medicines, and data-completeness, so trends and AKI are detectable and interpretation is personalised. The evaluation suite uses trajectory-aware scoring on escalation, AKI and triage; a golden set with a must-always-escalate class scored `pass^k`; positive and negative trigger tests; regression checks; and a labelled classification and KFRE test set including UK-unit and unstable-value edge cases. Observability logs every classification, AKI, and escalation decision per session for clinical review. Data handling is UK GDPR-compliant for special-category health data, with encryption in transit and at rest, access controls, and a documented clinical-safety and security posture.

### 4.13 UX requirements

Warm, plain-English, low-anxiety, and neither alarmist nor falsely reassuring. Escalation copy is calm and specific. A persistent "educational support, does not replace your GP or care team" framing runs throughout without undermining real escalations. Accessibility is built for an older demographic (large text, high contrast, simple flows) and aligned to NHS content and accessibility standards. Data completeness and any held-out (AKI/illness) readings are shown honestly, so the person can see what the app is basing things on.

---

## 5\. FAQ

**Is this diagnosing me?** No, it's classifying. CKD classification is arithmetic: your eGFR and ACR map to one KDIGO category and risk band. The app does that, tells you the monitoring frequency and generic guidance that follow, and routes every clinical decision, from confirming a diagnosis to prescribing, back to your GP.

**How does the dialysis-risk tool work, and can it show what happens if I stop smoking?** The risk number comes from the Kidney Failure Risk Equation, which uses age, sex, eGFR and ACR (UK-calibrated). You can see how the risk changes if your ACR or eGFR improves, because those are in the equation. Smoking and HbA1c are not equation inputs, so the app won't pretend to recalculate the risk from them. Instead it explains, from the evidence, how stopping smoking and improving blood-sugar and blood-pressure control lower your ACR and slow decline, which is how they change your risk over time.

**What happens if a reading was taken while I was ill?** Tell the app (or it may ask). It will hold that reading out of your long-term trend and your risk estimate, explain why, and suggest re-checking when you've recovered. The same logic powers its acute kidney injury check, which looks for a sudden creatinine rise against your usual level and tells you to seek prompt care.

**How does it handle medicines safely?** It informs generically and routes decisions: it flags medicines clinicians review at your kidney function, educates on sick-day rules, and notes generically where a guideline-recommended treatment may be indicated. It never issues a personalised start, stop, or dose instruction.

**How is it kept up to date with guidelines?** The clinical content is versioned, dated, and clinician-reviewed against KDIGO 2024 and NICE (NG203 and the relevant appraisals), with a defined refresh process. Guidance changes: the expansion of SGLT2 inhibitors to essentially all adults with eGFR 20–45 is exactly why versioning is built in.

**Why is fluid advice so cautious?** Because "drink more water" is wrong for some people with CKD; in advanced disease or fluid overload the advice flips to restriction. So fluid guidance stays generic, comes from trusted sources, and escalates rather than personalising.

**What's the regulatory position?** It is deliberately positioned as educational and self-management support, because it classifies rather than diagnoses and informs rather than prescribes. A real NHS deployment would still need proper review: MHRA/UKCA medical-device assessment where intended use crosses into "device" territory (the classification, AKI, KFRE and escalation logic would be scrutinised here), the NHS Digital Technology Assessment Criteria (DTAC), clinical-safety standards DCB0129 and DCB0160 with a named Clinical Safety Officer, and the NICE Evidence Standards Framework for digital health technologies.

### Key decisions

Classify with KDIGO, manage with NICE, in UK units. Give generic information and route decisions to the clinician. Treat every input as optional and degrade gracefully. Make the AKI check, the KFRE calculation, and the escalation gate deterministic, with the model explaining rather than deciding. Keep the dialysis-risk what-if scientifically honest: recalculate only from real equation inputs, and explain the rest. Keep the clinical content versioned and clinician-governed.

### Tradeoffs made

Conservative escalation means some over-referral, accepted for a silent disease and mitigated by tuning against real primary-care patterns. Generic-only medication guidance trades specificity for safety and a defensible regulatory position. The dialysis-risk explorer is deliberately less "magical" than a calculator that claims to model every lifestyle change, because a scientifically unsound number would be worse than an honest one. The app is not a diagnostic or measurement device. And it stays narrow to CKD rather than going broad.

---

## 6\. Launch checklist

### Readiness criteria

The escalation and AKI eval suites pass (must-always-escalate and must-always-detect-AKI sets at 100%, `pass^k` satisfied, do-not-answer adherence verified); classification and KFRE accuracy validated on a labelled set including UK-unit and unstable-value edge cases. Out-of-scope prescribing requests are refused, verified with negative test cases. Clinical content and thresholds reviewed and signed off against KDIGO 2024 and NICE by a UK renal clinician; a clinical-safety case (DCB0129) drafted with a named Clinical Safety Officer; guideline-version register in place. UK GDPR, information-governance and security reviews complete; secrets scan clean. Copy reviewed for tone and for the classify-not-prescribe line.

### Launch phases

1. Offline golden-set evaluation against curated KDIGO/NICE cases, including must-always-escalate, must-detect-AKI, and sparse-data cases.  
2. Shadow and internal test, comparing classifications, AKI flags and escalation decisions to expected outcomes without exposing users.  
3. Limited beta with a small at-risk and diagnosed cohort, ideally alongside a supportive GP practice or PCN, every escalation clinically reviewed.  
4. Controlled rollout, widening gradually and watching the safety metrics.

### Monitoring plan

Escalation precision and recall, AKI-detection recall, and classification/KFRE accuracy, reviewed continuously. Missed escalations and missed AKI reviewed with a clinician in the loop, every miss an incident. Drift monitoring on model, retrieval, and guideline currency. Do-not-answer adherence tracked, watching for personalised-prescribing leakage. User-reported outcomes and any signal of added GP workload or reduced duplicate testing. Per-session logging of every classification, AKI, and escalation decision for auditability.

---

## 7\. Scope, phasing, and platform integration

These are product phases, distinct from the rollout phases in section 6\.

### Phase 1 — in scope (the capstone MVP)

A web app with the full classify-inform-escalate core: KDIGO classification and risk band, NICE monitoring and referral flags, AKI recognition, the KFRE risk explorer, the medication and lifestyle modules, result-context and data-quality handling, ACR how-to, appointment prep, case-finding, and the patient-assembled primary/secondary view. Data comes in by manual entry, photo capture, and, where available, import from the NHS App or GP online records. This demonstrates the agent end to end and is the artefact the writeup describes.

### Phase 2 — out of scope for the capstone

Automated ingestion of device and home-vitals data (smartwatch, home BP, weight) through Apple HealthKit and Android Health Connect. Deferred because it forces a native app (both stores are on-device, native-only, and unreachable from a web app; on Android the target is Health Connect, since Google's Fit APIs are deprecated and supported only to the end of 2026); because it mainly enriches the secondary signals, not the labs that drive classification, which in the UK come from GP records and the NHS App; and because shipping a native app sharpens the regulatory question through App Store and Play health-app review, with Apple noting that in some regions the app may count as a regulated medical device and, from spring 2026, allowing regulatory-status declaration. The evals, guardrails and clinical governance should be solid first.

### Phase 3 — future, dependency-heavy

Deeper NHS integration (GP Connect, shared care records, lab feeds) so the core labs flow in automatically and the primary/secondary view reconciles itself. Highest value, hardest to build, and gated behind NHS information-governance and integration approvals.

---

## Feature context

KidneyCompass is a patient-facing, natural-language CKD companion for the UK and NHS context, built for the 5-Day AI Agents Intensive capstone. It closes the gap for a disease that is silent until late and under-recognised across UK primary care. It takes whatever results a person has, classifies their CKD against KDIGO, tells them how often to monitor and what to raise, recognises an acute kidney injury and keeps it out of the chronic trend, estimates their five-year dialysis risk honestly, prepares them for GP and renal-clinic appointments, brings primary and secondary results together for those who need it, and prompts undiagnosed at-risk users to get tested. It classifies and informs generically, and it never prescribes. It is evaluated for the failure mode that matters most in a clinical domain, reasoning that is wrong but looks right, with the classification, AKI, risk and escalation logic gated deterministically and the clinical content versioned and clinician-governed.

---

## Key sources

*Primary documents behind the clinical logic, for the writeup and for content curation. Verify against the originals before any real-world use.*

- **KDIGO 2024 Clinical Practice Guideline for the Evaluation and Management of CKD** — classification (CGA and risk heat-map), SGLT2 inhibitor recommendations (including eGFR 20–45), and current management. kdigo.org.  
- **NICE NG203, Chronic kidney disease: assessment and management** (2021, updated Nov 2024\) — UK management: definition, monitoring, BP targets, referral criteria, KFRE. nice.org.uk/guidance/ng203.  
- **NICE TA775 (dapagliflozin, 2022\)** and **NICE TA942 (empagliflozin, Dec 2024\)** — SGLT2 inhibitors in NHS CKD care.  
- **UK Kidney Association / Renal Association, Clinical Practice Guideline: Exercise and Lifestyle in CKD** (2021) — the physical activity, weight, smoking and alcohol recommendations. ukkidney.org.  
- **Kidney Failure Risk Equation (KFRE)** — Tangri et al. (4- and 8-variable); UK external validation and recalibration (Major et al., *PLoS Medicine* 2019); UKKA KFRE summary. NICE recommends the UK-calibrated version.  
- **NHS England "Think Kidneys" AKI programme** and **KDIGO AKI criteria** — the acute kidney injury thresholds and the national AKI warning-stage algorithm. thinkkidneys.nhs.uk.  
- **Kidney Care UK** and the **UK Kidney Association** (ukkidney.org) — trusted patient-facing lifestyle, diet and self-management information.  
- **Kidney Research UK, "Kidney disease: a UK public health emergency" (2023)** — UK prevalence and economic burden.  
- **OxRen cohort (BJGP 2020\)** — UK primary-care CKD prevalence and undiagnosed proportion.  
- **GP-awareness studies** — Blakeman et al. (BJGP 2010, QICKD); CKMAPPS (BJGP 2015); the QICKD confidence/knowledge questionnaire (BMC Nephrology 2014); primary-care CKD stage-3 treatment-needs study (BJGP 2012).

---

## Appendix — supporting detail

*UK-centric figures and thresholds behind the sources above.*

### Classification and management

- **KDIGO categories:** G1 (eGFR ≥90), G2 (60–89), G3a (45–59), G3b (30–44), G4 (15–29), G5 (\<15); A1 (\<3), A2 (3–30), A3 (\>30) mg/mmol. Risk heat-map from green (low) to red (very high); risk rises with lower eGFR and higher ACR and multiplies in combination.  
- **BP targets (NICE, clinic):** ACR below 70 mg/mmol, aim below 140/90; ACR 70 mg/mmol or more, aim below 130/80.  
- **First-line drugs:** ACE inhibitor or ARB to maximum tolerated dose; statins for CV risk; SGLT2 inhibitors per KDIGO 2024 / NICE TAs.  
- **Referral (NICE):** 5-year KFRE risk over 5%; eGFR below 30; ACR 70 mg/mmol or more; A3 with haematuria; hypertension uncontrolled on four or more agents; suspected renal artery stenosis; suspected rare/genetic causes.  
- **Anaemia:** eGFR under 60 prompts investigating whether anaemia is due to CKD; consider treatment at Hb ≤110 g/L or symptoms; iron-deficiency markers ferritin \<100 µg/L, transferrin saturation \<20%.  
- **Bone profile:** measure calcium, phosphate, PTH in G4/G5; treat vitamin D deficiency; consider sodium bicarbonate if eGFR \<30 and bicarbonate \<20 mmol/L.  
- **Ultrasound (NICE):** for accelerated progression, visible or persistent haematuria, obstruction symptoms, family history of ADPKD (with counselling), eGFR below 30, or if biopsy considered.

### AKI thresholds (KDIGO / Think Kidneys)

- Creatinine rise ≥26 µmol/L within 48 hours, or ≥1.5× baseline within 7 days (or an equivalent abrupt eGFR fall). Staged 1–3 by magnitude. Urine-output criteria apply only to catheterised hospital patients. AKI is a risk factor for later CKD; monitor for ≥3 years afterward.

### KFRE

- 4-variable inputs: age, sex, eGFR, ACR; predicts 2- and 5-year risk of kidney replacement therapy for G3a–G5. 8-variable adds serum albumin, phosphate, bicarbonate, calcium. Smoking, HbA1c and BP are not inputs (the 6-variable adds diabetes and hypertension as flags, but is not the version used in practice). UK-recalibrated version recommended by NICE; non-UK versions overestimate UK risk. Does not model competing risk of death.

### ACR collection

- First-morning sample preferred; avoid vigorous exercise for 24 hours; do not collect during menstruation, UTI, fever, or acute illness. Confirm a new result of 3–70 mg/mmol on a repeat first-morning sample; ≥70 mg/mmol needs no repeat. ACR ≥3 mg/mmol is clinically important proteinuria.

### Lifestyle (UKKA Exercise and Lifestyle in CKD)

- Physical activity adapted from UK CMO guidance: build toward 150 minutes/week moderate activity, strength/balance twice weekly, reduce sedentary time; proven CKD benefits are BP, physical function and quality of life. Smoking cessation is the strongest progression lever (1A). Maintain a healthy weight (U-shaped risk); alcohol within national limits; individualised diet, no low-protein diets.

### Prevalence, under-recording, GP awareness, burden (UK)

- OxRen: 18.2% CKD in adults ≥60; \~44% undiagnosed without screening. PHE model: higher in women (7.4%) than men (4.7%), rising with age. QOF register \~4.1% vs true \~8.5%; Lambeth \~45.5% coded; \~30% of register patients with suboptimal management.  
- GP awareness: Blakeman 2010 (reluctance to apply the label, especially stage 3); CKMAPPS 2015 (little advanced-CKD experience, wanted referral guidance); QICKD 2014 (validated confidence/knowledge questionnaire); BJGP 2012 (67% of stage-3 patients needed further intervention despite being seen as low-risk).  
- Kidney Research UK 2023: \~£7bn/year to the UK economy, \~£6.4bn direct NHS; \~3.25m at stages 3–5; dialysis \>£1bn/year, \~£30k per patient per year.  
- Treatment effect: SGLT2 inhibitors reduce progression risk by \~a third (≈37% meta-analysis; 39% DAPA-CKD; 28% EMPA-KIDNEY); ACEi/ARB and BP control foundational.

