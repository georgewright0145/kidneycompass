"""Generate machine-readable skill cards (Day 4 trust tiers) for the KidneyCompass skills.

Each card records author, trust tier, access, and limitations. All KidneyCompass clinical skills are
first-party and clinician-reviewed (pending sign-off); any third-party skill would be untrusted until
scanned by the skill inspector. Run: python security/skill_cards/generate_skill_cards.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = ROOT / "skills"
OUT_DIR = ROOT / "security" / "skill_cards"

COMMON = {
    "author": "KidneyCompass (first-party)",
    "trust_tier": "first-party-reviewed",
    "clinical_review_status": "pending UK renal-clinician sign-off",
    "access": {
        "network": False,
        "filesystem": "read-only references within the skill",
        "executes_code": "deterministic engines in engines/ only (no arbitrary code)",
    },
    "limitations": [
        "Informs and classifies; never diagnoses or prescribes.",
        "Clinical thresholds sourced only from spec/guidelines/; not from model training data.",
        "All high-stakes numbers come from deterministic engines, not the LLM.",
    ],
}


def main() -> None:
    cards = []
    for skill_dir in sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir()):
        name = skill_dir.name
        card = {"skill": name, **COMMON}
        (OUT_DIR / f"{name}.card.json").write_text(json.dumps(card, indent=2) + "\n")
        cards.append(name)
    print(f"Wrote {len(cards)} skill cards: {', '.join(cards)}")


if __name__ == "__main__":
    main()
