"""Consume the clinical-knowledge MCP server as a tool (Day 2 — MCP, "USB-C" style).

The guidance agent uses this to look up guideline text (thresholds, drug notes, referral criteria)
from the versioned spec/guidelines/ content instead of model memory. Scoped to this project only.

Kept optional and defensive: if the MCP stack can't initialise (e.g. in a constrained CI or deploy
runtime), the guidance agent still works with its deterministic tools. The server is launched over
stdio with the project's own Python interpreter.
"""

from __future__ import annotations

import sys
from pathlib import Path

_SERVER = Path(__file__).resolve().parents[1] / "mcp" / "clinical_knowledge_server" / "server.py"


def clinical_knowledge_toolset():
    """Return an ADK McpToolset for the clinical-knowledge server, or None if unavailable."""
    try:
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
        from mcp import StdioServerParameters
    except ImportError:
        return None

    return McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command=sys.executable,             # the project venv's python (absolute)
                args=[str(_SERVER)],                # absolute path, per ADK requirement
            ),
        ),
        tool_filter=["lookup_guideline", "list_guideline_sources"],
    )
