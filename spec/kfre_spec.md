# Spec — KFRE Risk (`engines/kfre.py`)

*Source of truth for `kfre.py`. Grounded in `spec/guidelines/kfre.md`. Deterministic Python.*

## Interface
```
kfre_risk(age, sex, egfr, acr_mg_mmol, *, suspected_aki=False) -> KfreResult
```
`KfreResult`: `status` ("ok" | "constants_unavailable" | "not_applicable" | "unstable_value"),
`risk_2yr` (float|None), `risk_5yr` (float|None), `inputs_echo` (dict), `caveats` (list[str]),
`valid_whatifs` (list[str] = ["egfr","acr"]).

## HARD GATE — current state
- The UK recalibration constants are **not yet supplied**. Until a `UK_KFRE_CONSTANTS` block is
  filled in (from user), `kfre_risk` MUST return `status="constants_unavailable"`, `risk_*=None`,
  and a caveat explaining a clinician-verified UK-calibrated calculation is pending.
- **Do NOT invent constants.** A wrong risk number is worse than an honest "unavailable."

## Refusal / applicability scenarios (must hold even once constants exist)
- `suspected_aki=True` → `status="unstable_value"`, no number. (Never run on AKI-flagged values.)
- eGFR ≥ 60 → `status="not_applicable"` (KFRE is for G3a–G5).
- Missing any of age/sex/egfr/acr → `status="not_applicable"`, list what's missing.

## What-if rules (once constants exist)
- Only **eGFR** and **ACR** are recalculable inputs. `valid_whatifs=["egfr","acr"]`.
- Smoking / HbA1c / BP / weight are **not** inputs → any what-if request on them returns an
  explanation flag, never a recomputed number.

## Units
- ACR received in **mg/mmol**. The published equation uses mg/g → conversion (×8.8403 approx) is a
  **safety-critical step** and must be unit-tested once constants are added. Documented, not yet active.

## Caveats always attached
- Does not model competing risk of death; may overestimate in older/frailer people.
- eGFR/ACR vary day to day — trend matters more than one value.
```
