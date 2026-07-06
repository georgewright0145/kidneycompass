# Kaggle submission checklist

*A missing required asset is the most common silent disqualifier at scale. Confirm every row before
hitting Submit.*

## Required assets

- [ ] **Kaggle Writeup created** (New Writeup → paste `submission/WRITEUP.md`, ~1,295 words, under the 2,500 limit)
- [ ] **Track selected: Agents for Good** (required to submit)
- [ ] **Title + subtitle** set in the Kaggle fields
- [ ] **Cover image** attached to the Media Gallery (screenshot of `submission/cover.html` — required to submit)
- [ ] **Video** recorded from `submission/VIDEO_SCRIPT.md`, ≤ 5:00, uploaded to **YouTube**, attached to the Media Gallery
- [ ] **Public Project Link** attached → `https://github.com/georgewright0145/kidneycompass`
- [ ] **Submit button clicked** (a saved draft is NOT a submission)

## Quality checks (raise the automated + human score)

- [ ] Repo is **public** and the README renders as the front door (concept map + verify block)
- [ ] Writeup **names the four course concepts and where they live** (only 3 required — 4 is a strength)
- [ ] Writeup states **verifiable metrics** (104 tests, 6 eval suites, C=0.930) — LLM judges quote concrete numbers
- [ ] Video **shows the trace panel** during the classification + AKI beats (proves deterministic tool calls)
- [ ] Video does **not** claim Antigravity; frames deployability as "deploy-ready" (rules allow repo-only)
- [ ] No API keys / secrets anywhere (verified: `.env` gitignored, secret scan clean, never in history)

## Scoring map (100 pts) — where each asset earns points

| Criterion | Points | Carried by |
|---|---|---|
| Core Concept & Value | 10 | Writeup + video |
| YouTube Video | 10 | The video (record it — biggest remaining gap) |
| Writeup | 10 | `submission/WRITEUP.md` |
| Technical Implementation | 50 | The **repo** (README, `engines/`, `app/`, `mcp/`, evals) |
| Documentation | 20 | The **repo** (README, `docs/EVALUATION.md`, `security/README.md`) |

70 of 100 points are judged in the repository — which is why the README is written as a reviewer's
front door.
