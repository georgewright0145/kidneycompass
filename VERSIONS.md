# KidneyCompass — Pinned Versions (Phase 0)

*Confirmed against live sources on 2026-07-06. Do NOT fall back to training-cutoff defaults.*

## Environment (Vertex + Gemini, ADC)
```
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=kaggle-course-499808
GOOGLE_CLOUD_LOCATION=us-east1          # verified: Gemini 2.5 Flash served here
GOOGLE_CLOUD_STORAGE_BUCKET=gs://kaggle-course-499808-agent-staging
```
ADC: OK (george.wright.0145@gmail.com).

## Model
| Purpose | Pinned string | Verified |
|---|---|---|
| Language (all sub-agents) | `gemini-2.5-flash` | ✅ live `generateContent` in us-east1 → real `OK`, finishReason STOP |
| (also available) | `gemini-2.5-flash-lite` | ✅ 200 in us-east1 |

Not served in us-east1/this project: `gemini-2.0-flash`, `gemini-3-flash`, `gemini-3-pro-preview`, `gemini-flash-latest` (all 404). **No region switch needed.**

## Toolchain
| Package | Pinned | Latest on PyPI | Notes |
|---|---|---|---|
| google-agents-cli | **1.0.0** | 1.0.0 (2026-07-01) | upgraded from 0.5.0; skills synced to match |
| google-adk | **2.3.0** | 2.3.0 (2026-06-18) | to install into the project venv |
| google-genai | **2.10.0** | 2.10.0 (2026-06-24) | |
| Python (project) | 3.12 (CLI's venv) | — | system python is 3.14; ADK targets 3.12 |

## CLI verb changes vs. the implementation plan (plan was written against older CLI)
- Plan says `uvx google-agents-cli setup` + `agents-cli scaffold` → actual: `agents-cli setup`, `agents-cli create <name>` (or `scaffold create`).
- Plan says `agents-cli eval run` → actual: `agents-cli eval generate` (inference over cases) + `agents-cli eval grade` (score traces).
