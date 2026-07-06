#!/usr/bin/env bash
# KidneyCompass CI gate — security scans + deterministic clinical gates.
# Course frame (Day 4/5): security tells you the agent stayed inside the boundary; evaluation tells
# you whether what happened inside is worth shipping. Both run in the SDLC, not as a bolt-on.
#
# Usage: bash security/ci/run_security_and_eval.sh
# Exit non-zero if any gate fails. Requires: uv/uvx, the project .venv (agents-cli install), ADC.
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=.venv/bin/python
FAIL=0

echo "== 1. Unit tests (deterministic engines + metrics) =="
$PY -m pytest tests/unit/ -q || FAIL=1

echo "== 2. Semgrep SAST (fail on findings) =="
uvx semgrep --config auto --error engines/ app/ tests/ security/ mcp/ 2>/dev/null || FAIL=1

echo "== 3. Secret scan (project source only; .env is gitignored) =="
LEAKS=$(uvx detect-secrets scan engines app tests security spec mcp 2>/dev/null \
  | $PY -c "import json,sys; print(sum(len(v) for v in json.load(sys.stdin).get('results',{}).values()))")
echo "   project secret findings: $LEAKS"
[ "$LEAKS" = "0" ] || { echo "   SECRET LEAK DETECTED"; FAIL=1; }

echo "== 4. Clinical eval gates (pass^k: every case must score 1.0) =="
run_gate () {  # name dataset config
  local name=$1 dataset=$2 config=$3 out="artifacts/ci_${1}"
  agents-cli eval generate --dataset "$dataset" -o "${out}/traces/" >/dev/null 2>&1
  local trace; trace=$(ls "${out}/traces/"*.json | tail -1)
  agents-cli eval grade --traces "$trace" --config "$config" --output "${out}/grade/" 2>&1 \
    | grep -E "mean_score" | tee /dev/stderr | grep -q "1.0000" \
    && echo "   [PASS] $name" || { echo "   [FAIL] $name"; FAIL=1; }
}
run_gate must_escalate      tests/eval/datasets/must_escalate.json            tests/eval/must_escalate_config.yaml
run_gate must_detect_aki    tests/eval/datasets/must_detect_aki.json          tests/eval/must_detect_aki_config.yaml
run_gate must_not_escalate  tests/eval/datasets/must_not_escalate.json        tests/eval/must_not_escalate_config.yaml
run_gate classification     tests/eval/datasets/classification.json           tests/eval/classification_config.yaml
run_gate kfre_accuracy      tests/eval/datasets/kfre.json                     tests/eval/kfre_config.yaml
run_gate redteam_refusal    security/redteam_refusal_suite/refusal_cases.json security/redteam_refusal_suite/refusal_config.yaml

echo "======================================"
[ "$FAIL" = "0" ] && echo "ALL GATES PASSED" || { echo "GATES FAILED"; exit 1; }
