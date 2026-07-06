# KDIGO 2024 — CKD Classification (CGA) and Risk Heat-Map

> **Source & status.** Thresholds bootstrapped verbatim from the KidneyCompass PRD appendix
> ("Classification and management"), which cites the *KDIGO 2024 Clinical Practice Guideline for
> the Evaluation and Management of CKD*. **Pending UK renal-clinician sign-off** before any
> real-world use. Version: `kdigo-2024` / bootstrapped 2026-07-06. Verify against kdigo.org original.

## Definition of CKD
Sustained reduction in kidney function (eGFR below 60 ml/min/1.73m²) **and/or** kidney damage
(ACR of 3 mg/mmol or more), lasting **more than three months**.

## G categories (eGFR, ml/min/1.73m²)
| Category | eGFR range | Description |
|---|---|---|
| G1 | ≥ 90 | Normal or high |
| G2 | 60–89 | Mildly decreased |
| G3a | 45–59 | Mildly to moderately decreased |
| G3b | 30–44 | Moderately to severely decreased |
| G4 | 15–29 | Severely decreased |
| G5 | < 15 | Kidney failure |

Boundaries are inclusive of the lower bound (e.g. eGFR 45 → G3a; eGFR 44 → G3b; eGFR 30 → G3b; eGFR 29 → G4).

## A categories (urine ACR, **mg/mmol — UK units**)
| Category | ACR (mg/mmol) | ~mg/g cross-ref | Description |
|---|---|---|---|
| A1 | < 3 | < 30 | Normal to mildly increased |
| A2 | 3–30 | 30–300 | Moderately increased |
| A3 | > 30 | > 300 | Severely increased |

**UK-unit safety rule:** display and reason in **mg/mmol**. Cross-reference mg/g only when a KDIGO
threshold is quoted (e.g. ACR 20 mg/mmol ≈ 200 mg/g). Never silently treat mg/mmol as mg/g.
Boundary handling: ACR exactly 3 → A2; exactly 30 → A2 (A3 is strictly > 30).

## Risk heat-map (CGA → risk band)
Risk rises with lower eGFR and higher ACR, and multiplies in combination. Bands: **green (low),
amber (moderately increased), orange (high), red (very high)**.

| eGFR \ ACR | A1 (<3) | A2 (3–30) | A3 (>30) |
|---|---|---|---|
| **G1 (≥90)**   | Green  | Amber  | Orange |
| **G2 (60–89)** | Green  | Amber  | Orange |
| **G3a (45–59)**| Amber  | Orange | Red    |
| **G3b (30–44)**| Orange | Red    | Red    |
| **G4 (15–29)** | Red    | Red    | Red    |
| **G5 (<15)**   | Red    | Red    | Red    |

> Note: G1/G2 with A1 is only classified as CKD if kidney damage is otherwise evidenced and
> sustained >3 months (see definition). With A1 and eGFR ≥60 and no other damage marker, the person
> does not meet the CKD definition — classify on the G axis and state this openly.

## Monitoring frequency (times per year), by risk band
Per PRD 4.2: "roughly annual at lower-risk cells, rising to two or more times a year at higher-risk
cells." Encoded as a function of band (see `spec/classification_spec.md` for the exact mapping used).

- Green: at least once a year (1/yr)
- Amber: about once a year (1/yr)
- Orange: about twice a year (2/yr)
- Red: two or more times a year (≥2/yr; 3–4/yr at the most severe cells such as G4–G5)

> These monitoring intervals are the PRD's plain-English summary of NICE NG203 frequency guidance.
> **Flag for clinician review:** confirm exact NICE NG203 "number of times per year" table before pilot.
