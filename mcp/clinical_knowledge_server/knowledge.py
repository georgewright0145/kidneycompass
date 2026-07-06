"""Clinical-knowledge retrieval over the versioned guideline text in spec/guidelines/.

Two retrieval modes run in PARALLEL (not a cascade), per the plan: exact-term / full-text for
anything that must match precisely (thresholds, ACR in mg/mmol, drug names, referral criteria) and a
token-overlap full-text score for natural-language questions. Vector retrieval is a documented future
addition. Every result carries its source file and version so answers stay traceable and governed.

Deterministic and import-safe (no server needed) so it is unit-testable.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

GUIDELINES_DIR = Path(__file__).resolve().parents[2] / "spec" / "guidelines"

_VERSION_RE = re.compile(r"[Vv]ersion:\s*`?([a-z0-9\-\._]+)`?", re.IGNORECASE)
_TOKEN_RE = re.compile(r"[a-z0-9]+(?:\.[0-9]+)?", re.IGNORECASE)
_STOP = {"the", "a", "an", "of", "for", "and", "or", "to", "in", "is", "at", "on", "with", "my",
         "what", "how", "should", "i", "be", "are", "if", "not", "it", "this", "that", "your"}


@dataclass
class Passage:
    source: str          # file name
    version: str         # guideline version tag
    heading: str         # nearest markdown heading
    text: str


@dataclass
class SearchResult:
    query: str
    mode: str
    passages: list[dict] = field(default_factory=list)  # {source, version, heading, text, score}
    note: str = ""


def _tokens(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN_RE.findall(text) if t.lower() not in _STOP]


class GuidelineIndex:
    """Loads and indexes the versioned guideline passages once."""

    def __init__(self, guidelines_dir: Path | None = None):
        self.dir = guidelines_dir or GUIDELINES_DIR
        self.passages: list[Passage] = []
        self._load()

    def _load(self) -> None:
        self.passages = []
        for path in sorted(self.dir.glob("*.md")):
            raw = path.read_text(encoding="utf-8")
            vm = _VERSION_RE.search(raw)
            version = vm.group(1) if vm else path.stem
            heading = path.stem
            buf: list[str] = []

            def flush(h: str, b: list[str]) -> None:
                block = "\n".join(b).strip()
                if block:
                    self.passages.append(Passage(source=path.name, version=version, heading=h, text=block))

            for line in raw.splitlines():
                if line.startswith("#"):
                    flush(heading, buf)
                    buf = []
                    heading = line.lstrip("#").strip()
                elif line.strip() == "" and buf:
                    flush(heading, buf)
                    buf = []
                else:
                    buf.append(line)
            flush(heading, buf)

    def sources(self) -> list[dict]:
        seen: dict[str, str] = {}
        for p in self.passages:
            seen.setdefault(p.source, p.version)
        return [{"source": s, "version": v} for s, v in seen.items()]

    def _exact_score(self, query: str, p: Passage) -> int:
        q = query.lower().strip()
        if not q:
            return 0
        return p.text.lower().count(q)

    def _fulltext_score(self, q_tokens: list[str], p: Passage) -> int:
        if not q_tokens:
            return 0
        p_tokens = set(_tokens(p.text)) | set(_tokens(p.heading))
        return sum(1 for t in q_tokens if t in p_tokens)

    def search(self, query: str, mode: str = "auto", limit: int = 5) -> SearchResult:
        """Search the guideline passages. mode: 'exact' | 'fulltext' | 'auto' (both, merged)."""
        mode = (mode or "auto").lower()
        q_tokens = _tokens(query)
        scored: dict[int, float] = {}

        run_exact = mode in ("exact", "auto")
        run_full = mode in ("fulltext", "auto")

        for i, p in enumerate(self.passages):
            score = 0.0
            if run_exact:
                score += self._exact_score(query, p) * 5  # exact-term matches weighted highest
            if run_full:
                score += self._fulltext_score(q_tokens, p)
            if score > 0:
                scored[i] = score

        ranked = sorted(scored.items(), key=lambda kv: kv[1], reverse=True)[:limit]
        result = SearchResult(query=query, mode=mode)
        for i, score in ranked:
            p = self.passages[i]
            result.passages.append({
                "source": p.source,
                "version": p.version,
                "heading": p.heading,
                "text": p.text,
                "score": round(score, 2),
            })
        if not result.passages:
            result.note = ("No matching guideline passage found. KidneyCompass only reasons from the "
                           "curated guideline text; if a threshold is not here, it is not answered.")
        return result
