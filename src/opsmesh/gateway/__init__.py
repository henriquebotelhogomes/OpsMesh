"""OpsMesh Universal Tool Gateway.

Provides bidirectional conversion between Anthropic MCP and OpenAI/DeepSeek Tool Schemas,
unified tool execution, and observability tool mocks with output truncation guardrails.
"""

from opsmesh.gateway.adapter import mcp_to_openai_tool, openai_to_mcp_tool
from opsmesh.gateway.dispatcher import ToolDispatcher
from opsmesh.gateway.tools import (
    check_k8s_deployment_health,
    inspect_database_activity,
    query_logs,
)

__all__ = [
    "mcp_to_openai_tool",
    "openai_to_mcp_tool",
    "ToolDispatcher",
    "query_logs",
    "inspect_database_activity",
    "check_k8s_deployment_health",
]
