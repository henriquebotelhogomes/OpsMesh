import pytest

from opsmesh.gateway.adapter import (
    format_mcp_result_for_llm,
    mcp_to_openai_tool,
    openai_to_mcp_tool,
)
from opsmesh.gateway.dispatcher import ToolDispatcher
from opsmesh.gateway.tools import (
    MAX_TOOL_OUTPUT_CHARS,
    truncate_tool_output,
)


def test_mcp_to_openai_tool_conversion():
    mcp_tool = {
        "name": "custom_query",
        "description": "Execute a query",
        "inputSchema": {
            "type": "object",
            "properties": {"q": {"type": "string"}},
            "required": ["q"],
        },
    }
    openai_tool = mcp_to_openai_tool(mcp_tool)
    assert openai_tool["type"] == "function"
    assert openai_tool["function"]["name"] == "custom_query"
    assert openai_tool["function"]["description"] == "Execute a query"
    assert "properties" in openai_tool["function"]["parameters"]


def test_openai_to_mcp_tool_conversion():
    openai_tool = {
        "type": "function",
        "function": {
            "name": "run_action",
            "description": "Run an action",
            "parameters": {
                "type": "object",
                "properties": {"action_id": {"type": "string"}},
            },
        },
    }
    mcp_tool = openai_to_mcp_tool(openai_tool)
    assert mcp_tool["name"] == "run_action"
    assert mcp_tool["description"] == "Run an action"
    assert "action_id" in mcp_tool["inputSchema"]["properties"]


def test_format_mcp_result_for_llm():
    msg = format_mcp_result_for_llm("call_123", {"status": "ok"})
    assert msg["role"] == "tool"
    assert msg["tool_call_id"] == "call_123"
    assert '"status": "ok"' in msg["content"]


def test_tool_truncation_guardrail():
    long_text = "A" * 3000
    truncated = truncate_tool_output(long_text, max_chars=MAX_TOOL_OUTPUT_CHARS)
    assert len(truncated) <= MAX_TOOL_OUTPUT_CHARS
    assert "TRUNCATED" in truncated


@pytest.mark.asyncio
async def test_tool_dispatcher_execution():
    dispatcher = ToolDispatcher()
    tools = dispatcher.get_openai_tools()
    assert len(tools) >= 3

    tool_names = [t["function"]["name"] for t in tools]
    assert "query_logs" in tool_names
    assert "inspect_database_activity" in tool_names
    assert "check_k8s_deployment_health" in tool_names

    # Test query_logs execution
    res_logs = await dispatcher.execute_tool("query_logs", {"filter_query": "postgres"})
    assert "connection pool exhausted" in res_logs
    assert len(res_logs) <= MAX_TOOL_OUTPUT_CHARS

    # Test database inspection
    res_db = await dispatcher.execute_tool("inspect_database_activity", {"metric": "connections"})
    assert "connection_pool_utilization_pct" in res_db

    # Test k8s check
    res_k8s = await dispatcher.execute_tool(
        "check_k8s_deployment_health", {"service_name": "recommendation-ml"}
    )
    assert "OOMKilled" in res_k8s

    # Test unknown tool handling
    res_unknown = await dispatcher.execute_tool("non_existent_tool", {})
    assert "UnknownToolError" in res_unknown
