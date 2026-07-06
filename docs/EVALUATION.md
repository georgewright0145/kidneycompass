# Evaluation evidence

*Safety in a clinical agent is proven, not asserted. Every gate below is **deterministic** (no LLM
judge), so results are stable and reproducible. Regenerate with `bash security/ci/run_security_and_eval.sh`.*

## Unit tests — the deterministic safety core (offline, instant)

```
.venv/bin/python -m pytest tests/unit/ -q   →   104 passed
```

Covers: KDIGO classification (boundaries, missing-data, CKD definition), the AKI check (both KDIGO /
Think Kidneys criteria + windows), KFRE (computation, refusal paths, what-if validity, cohort-matched
values), the escalation gate (every must-escalate class + urgency resolution), medication/referral
flags, appointment assembly, and the eval metrics themselves.

## Clinical eval golden sets — `agents-cli eval`, all pass^k

Each suite runs the full agent over labelled cases and grades with a **deterministic** metric that
recomputes ground truth from the engines (no hand-written expected answers).

| Suite | Purpose | Cases | Mean score | Dataset · metric |
|---|---|---|---|---|
| `must_escalate` | Never miss an escalation | 8 | **1.00** | [dataset](../tests/eval/datasets/must_escalate.json) · [metric](../tests/eval/escalation_metric.py) |
| `must_detect_aki` | Never miss a suspected AKI | 6 | **1.00** | [dataset](../tests/eval/datasets/must_detect_aki.json) · [metric](../tests/eval/aki_metric.py) |
| `must_not_escalate` | Never over-refer a stable patient | 7 | **1.00** | [dataset](../tests/eval/datasets/must_not_escalate.json) · [metric](../tests/eval/no_false_escalation_metric.py) |
| `classification` | Correct KDIGO category + risk band | 10 | **1.00** | [dataset](../tests/eval/datasets/classification.json) · [metric](../tests/eval/classification_metric.py) |
| `kfre_accuracy` | 5-yr risk within ±2pp of the engine; refuse when N/A | 6 | **1.00** | [dataset](../tests/eval/datasets/kfre.json) · [metric](../tests/eval/kfre_metric.py) |
| `redteam_refusal` | Refuse prescribing/diagnosis, incl. injection | 10 | **1.00** | [dataset](../security/redteam_refusal_suite/refusal_cases.json) · [metric](../security/redteam_refusal_suite/refusal_metric.py) |

`must_escalate`, `must_detect_aki` and `redteam_refusal` are treated as **pass^k**: they must score
1.0 on *every* run, not on average — the bar for a safety gate.

### The must_not_escalate suite is the interesting one
A recall-biased safety agent risks the opposite failure: crying wolf on the ~90% of stable patients
(over-referral). This suite proves it doesn't — stable patients (green/amber bands, normal Hb, no AKI)
are **not** urgently routed. During development it caught two apparent failures that turned out to be
a *metric* bug (matching the word "urgent" inside reassuring negations like "no urgent concern"); the
agent was correct, and the fix is locked with a regression test.

## Security scans (CI gate)

| Scan | Scope | Result |
|---|---|---|
| Semgrep SAST (`--config auto`) | `engines app tests security mcp` | **0 findings** |
| detect-secrets | all tracked source | **0 findings** |
| Secret in git history | full history | `.env` and patient CSV **never committed** |

## KFRE recalibration — validated, not asserted

The UK-recalibrated baseline survival was re-estimated on the **Major 2019 cohort (n=35,539, 568 KRT
events)** via a Breslow recalibration with the Tangri coefficients held fixed.

- **Discrimination:** Harrell's **C = 0.930** — matches published KFRE performance; because C depends
  only on the linear predictor, this confirms the coefficients are transcribed correctly.
- **Direction check:** the derived UK baseline survival (S₀ 5yr = 0.957) is **higher** than the
  non-UK Tangri value (0.924) — matching the published finding that non-UK calibrations overestimate
  UK risk.
- **Calibration (5-yr, top decile):** predicted 12.9% vs observed 14.2% — good agreement where the
  >5% referral decision is made.

Full method, results, and reproducible script: [`spec/kfre_recalibration/`](../spec/kfre_recalibration/).

## What "deterministic gate" buys the evaluation

Because classification, AKI, KFRE and escalation are code, the eval isn't measuring whether the model
*happened* to get a number right — it's measuring whether the agent surfaces the engine's answer
faithfully. The clinical correctness is guaranteed by construction and unit-tested; the eval suites
guard the *agent's behaviour around* those guarantees (does it always escalate, never over-refer,
always refuse prescribing, never fabricate a risk number).
