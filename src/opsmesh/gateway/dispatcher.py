"""Tool Dispatcher for Universal Tool Gateway.

Provides a unified execution layer capable of routing tool calls originating from
OpenAI/DeepSeek agents or Anthropic MCP agents to Python handlers or external MCP servers.
"""

from __future__ import annotations

import inspect
import json
import logging
from collections.abc import Callable
from typing import Any

from opsmesh.gateway.mcp_client import StdioMCPClient
from opsmesh.gateway.tools import (
    check_k8s_deployment_health,
    inspect_database_activity,
    query_logs,
    truncate_tool_output,
)

logger = logging.getLogger(__name__)


class ToolDispatcher:
    """Dispatches tool execution between native Python functions and MCP servers."""

    def __init__(self) -> None:
        self._local_tools: dict[str, Callable[..., Any]] = {}
        self._tool_schemas: dict[str, dict[str, Any]] = {}
        self._mcp_clients: list[StdioMCPClient] = []

        # Register default observability tools
        self.register_function(
            query_logs,
            name="query_logs",
            description="Query and search application/system logs across services with an optional query filter.",
            parameters={
                "type": "object",
                "properties": {
                    "filter_query": {
                        "type": "string",
                        "description": "Search keyword or filter term (e.g., 'error', 'pool', 'timeout').",
                    },
                    "time_range": {
                        "type": "string",
                        "description": "Time window (e.g. '15m', '1h', '24h'). Default is '15m'.",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max entries to retrieve (default 50).",
                    },
                },
                "required": ["filter_query"],
            },
        )

        self.register_function(
            inspect_database_activity,
            name="inspect_database_activity",
            description="Inspect PostgreSQL state (pg_stat_activity, pool saturation, lock queue) in Read-Only mode.",
            parameters={
                "type": "object",
                "properties": {
                    "metric": {
                        "type": "string",
                        "enum": ["connections", "locks", "slow_queries"],
                        "description": "Specific database metric to inspect.",
                    }
                },
                "required": [],
            },
        )

        self.register_function(
            check_k8s_deployment_health,
            name="check_k8s_deployment_health",
            description="Check Kubernetes deployment, pods, container restarts and OOMKilled events in Read-Only mode.",
            parameters={
                "type": "object",
                "properties": {
                    "service_name": {
                        "type": "string",
                        "description": "Name of the service/deployment to inspect (e.g. 'order-service', 'recommendation-ml').",
                    }
                },
                "required": ["service_name"],
            },
        )

    def register_function(
        self, func: Callable[..., Any], name: str, description: str, parameters: dict[str, Any]
    ) -> None:
        """Register a local Python function as an executable tool."""
        self._local_tools[name] = func
        self._tool_schemas[name] = {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters,
            },
        }

    def register_mcp_client(self, client: StdioMCPClient) -> None:
        """Register an active external MCP client."""
        self._mcp_clients.append(client)

    def get_openai_tools(self) -> list[dict[str, Any]]:
        """Return all registered tools formatted as OpenAI Function Calling schemas."""
        return list(self._tool_schemas.values())

    async def execute_tool(self, name: str, arguments: dict[str, Any] | str) -> str:
        """Execute a tool by name with arguments, enforcing output truncation guardrails.

        Args:
            name: Tool name.
            arguments: Tool arguments (dict or json string).

        Returns:
            Result text string, safely truncated to <= 2000 chars.
        """
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except json.JSONDecodeError:
                arguments = {}

        # 1. Local tool execution
        if name in self._local_tools:
            func = self._local_tools[name]
            try:
                if inspect.iscoroutinefunction(func):
                    result = await func(**arguments)
                else:
                    result = func(**arguments)

                if not isinstance(result, str):
                    result = json.dumps(result, ensure_ascii=False)
                return truncate_tool_output(result)
            except Exception as exc:
                logger.error("Error executing local tool %s: %s", name, exc)
                return f"ToolExecutionError in {name}: {exc}"

        # 2. Remote MCP server execution
        for client in self._mcp_clients:
            try:
                result = await client.call_tool(name, arguments)
                return truncate_tool_output(result)
            except Exception as exc:
                logger.warning("MCP client error executing %s: %s", name, exc)

        return f"UnknownToolError: Tool '{name}' is not registered in the Universal Gateway."
