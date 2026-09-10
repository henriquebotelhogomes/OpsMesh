"""MCP Client for Universal Tool Gateway.

Connects to Model Context Protocol (MCP) servers over stdio or HTTP/SSE,
discovering exposed tools and executing tool calls conforming to JSON-RPC 2.0.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


class MCPClientError(Exception):
    """Exception raised when an MCP tool invocation fails."""


class StdioMCPClient:
    """Lightweight stdio client for Anthropic MCP Servers."""

    def __init__(
        self, command: str, args: list[str] | None = None, env: dict[str, str] | None = None
    ):
        self.command = command
        self.args = args or []
        self.env = env
        self.process: asyncio.subprocess.Process | None = None
        self._request_id = 0

    async def connect(self) -> None:
        """Spawn the MCP server subprocess."""
        if self.process is not None:
            return

        try:
            self.process = await asyncio.create_subprocess_exec(
                self.command,
                *self.args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=self.env,
            )
            # Initialize handshake
            init_payload = {
                "jsonrpc": "2.0",
                "id": self._next_id(),
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "clientInfo": {"name": "opsmesh-gateway", "version": "0.1.0"},
                },
            }
            await self._send(init_payload)
            await self._receive()
        except Exception as exc:
            logger.warning("Failed to start stdio MCP server (%s): %s", self.command, exc)
            self.process = None

    def _next_id(self) -> int:
        self._request_id += 1
        return self._request_id

    async def _send(self, payload: dict[str, Any]) -> None:
        if not self.process or not self.process.stdin:
            raise MCPClientError("MCP process is not running.")
        message = json.dumps(payload) + "\n"
        self.process.stdin.write(message.encode("utf-8"))
        await self.process.stdin.drain()

    async def _receive(self) -> dict[str, Any]:
        if not self.process or not self.process.stdout:
            raise MCPClientError("MCP process is not running.")
        line = await self.process.stdout.readline()
        if not line:
            raise MCPClientError("MCP process closed stream unexpectedly.")
        return json.loads(line.decode("utf-8").strip())

    async def list_tools(self) -> list[dict[str, Any]]:
        """List all tools exposed by the MCP server."""
        if not self.process:
            return []
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/list",
            "params": {},
        }
        await self._send(payload)
        resp = await self._receive()
        return resp.get("result", {}).get("tools", [])

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> str:
        """Execute a tool on the MCP server."""
        if not self.process:
            raise MCPClientError("MCP server is not connected.")
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
        }
        await self._send(payload)
        resp = await self._receive()
        if "error" in resp:
            raise MCPClientError(f"MCP tool error: {resp['error']}")
        content_items = resp.get("result", {}).get("content", [])
        return "\n".join(item.get("text", "") for item in content_items if isinstance(item, dict))

    async def close(self) -> None:
        """Terminate the server process gracefully."""
        if self.process:
            try:
                self.process.terminate()
                await asyncio.wait_for(self.process.wait(), timeout=3.0)
            except Exception:
                if self.process:
                    self.process.kill()
            finally:
                self.process = None
