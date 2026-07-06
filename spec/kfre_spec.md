# Spec — KFRE Risk (`engines/kfre.py`)

*Source of truth for `kfre.py`. Grounded in `spec/guidelines/kfre.md`. Deterministic Python.*

## Interface
```
kfre_risk(age, sex, egfr, acr_mg_mmol, *, suspected_aki=False) -> KfreResult
```
`KfreResult`: `status` ("ok" | "constants_unavailable" | "not_applicable" | "unstable_value"),
`risk_2yr` (float|None), `risk_5yr` (float|None), `inputs_echo` (dict), `caveats` (list[str]),
`valid_whatifs` (list[str] = ["egfr","acr"]).

## Constants state
- `UK_KFRE_CONSTANTS` is now **populated**: Tangri 4-var coefficients (from the ukidney.com
  calculator JS) + UK baseline survival recalibrated on the Major 2019 cohort (see
  `spec/kfre_recalibration/`). `kfre_risk` computes for valid G3a–5 inputs.
- The refusal path is retained: if `UK_KFRE_CONSTANTS` is ever set back to `None`, `kfre_risk` MUST
  return `status="constants_unavailable"` rather than invent a number.
- **Never invent constants.** A wrong risk number is worse than an honest "unavailable."

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
