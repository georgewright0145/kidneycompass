"""Clinical-knowledge MCP server (FastMCP, stdio) — the 4th course concept, consumed "USB-C" style.

Serves the versioned, dated, clinician-reviewable guideline content (KDIGO 2024, NICE NG203/TAs,
UKKA lifestyle, AKI thresholds, KFRE calibration) from spec/guidelines/. Exposes exact-term /
full-text retrieval so anything that must match precisely (thresholds, ACR in mg/mmol, drug names,
referral criteria) is looked up rather than recalled from model memory. Scoped to THIS project only.

Run standalone:  python mcp/clinical_knowledge_server/server.py
Consumed by the guidance agent via ADK McpToolset over stdio (see app/mcp_client.py).
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

# Import works both as a package (app import) and as a script (python server.py).
try:
    from .knowledge import GuidelineIndex
except ImportError:  # run directly as a script
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from knowledge import GuidelineIndex  # type: ignore

mcp = FastMCP("kidneycompass-clinical-knowledge")
_INDEX = GuidelineIndex()


@mcp.tool()
def lookup_guideline(query: str, mode: str = "auto", limit: int = 5) -> dict:
    """Look up UK CKD guideline text (KDIGO 2024, NICE NG203/TAs, UKKA, AKI, KFRE).

    Use this to ground any clinical threshold, drug-review note, referral criterion, BP target, ACR
    rule, or lifestyle recommendation in the curated guideline text instead of model memory. Results
    carry their source file and version for traceability.

    Args:
        query: What to look up, e.g. "ACR referral threshold", "metformin eGFR", "BP target ACR 70",
            "AKI creatinine rise", "SGLT2 inhibitor eGFR band".
        mode: "exact" (precise term/threshold/drug match), "fulltext" (natural-language), or "auto"
            (both, merged — the default).
        limit: Maximum passages to return (default 5).

    Returns:
        dict with the query, mode, and a list of matching passages (source, version, heading, text,
        score). If nothing matches, a note that the threshold is not in the curated content.
    """
    res = _INDEX.search(query, mode=mode, limit=limit)
    return {"query": res.query, "mode": res.mode, "passages": res.passages, "note": res.note}


@mcp.tool()
def list_guideline_sources() -> dict:
    """List the curated guideline sources and their versions currently served."""
    return {"sources": _INDEX.sources()}


if __name__ == "__main__":
    mcp.run()
