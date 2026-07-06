"""Pinned configuration. Model string verified live on Vertex us-east1 (see VERSIONS.md).

Do NOT change the model to a training-cutoff default (e.g. gemini-flash-latest 404s in us-east1).
"""

# Verified served in us-east1 via generateContent on 2026-07-06 (real output, finishReason STOP).
MODEL = "gemini-2.5-flash"

DISCLAIMER = (
    "KidneyCompass is educational support and does not replace your GP or care team. "
    "It classifies and informs; it never diagnoses or prescribes."
)
