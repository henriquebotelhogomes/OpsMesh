"""Schema Adapter for Universal Tool Gateway.

Translates bidirectionally between Anthropic Model Context Protocol (MCP) tool
definitions and OpenAI/DeepSeek function calling format.
"""

from __future__ import annotations

import json
from typing import Any


def mcp_to_openai_tool(mcp_tool: dict[str, Any]) -> dict[str, Any]:
    """Convert an Anthropic MCP tool definition to OpenAI function format.

    Args:
        mcp_tool: MCP tool specification containing 'name', 'description', and 'inputSchema'.

    Returns:
        OpenAI-compatible tool dictionary with type='function'.
    """
    name = mcp_tool.get("name", "")
    description = mcp_tool.get("description", "")
    parameters = mcp_tool.get(
        "inputSchema",
        {"type": "object", "properties": {}, "required": []},
    )

    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": parameters,
        },
    }


def openai_to_mcp_tool(openai_tool: dict[str, Any]) -> dict[str, Any]:
    """Convert an OpenAI function tool definition to Anthropic MCP format.

    Args:
        openai_tool: OpenAI tool dictionary with structure {"type": "function", "function": {...}}
                     or direct function dictionary.

    Returns:
        MCP tool specification with 'name', 'description', and 'inputSchema'.
    """
    fn = openai_tool.get("function", openai_tool)
    name = fn.get("name", "")
    description = fn.get("description", "")
    input_schema = fn.get(
        "parameters",
        {"type": "object", "properties": {}, "required": []},
    )

    return {
        "name": name,
        "description": description,
        "inputSchema": input_schema,
    }


def format_mcp_result_for_llm(tool_call_id: str, content: str | dict | list) -> dict[str, Any]:
    """Format tool output as an OpenAI tool response message.

    Args:
        tool_call_id: Unique tool call identifier from the LLM turn.
        content: Raw result string or JSON object.

    Returns:
        OpenAI tool message dictionary.
    """
    if not isinstance(content, str):
        content = json.dumps(content, ensure_ascii=False)

    return {
        "role": "tool",
        "tool_call_id": tool_call_id,
        "content": content,
    }
