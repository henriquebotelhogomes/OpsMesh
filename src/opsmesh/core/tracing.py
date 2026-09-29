"""Distributed Tracing and APM Context Propagation for OpsMesh.

Handles W3C Trace Context (traceparent) and Datadog APM headers (x-datadog-trace-id),
correlating Chaos Lab fault injections, alert webhooks, and LangGraph multi-agent nodes.
"""

from __future__ import annotations

import contextlib
import logging
import uuid
from collections.abc import AsyncIterator, Iterator
from typing import Any

from opsmesh.core.config import settings

logger = logging.getLogger(__name__)

# Check if ddtrace is available
try:
    from ddtrace import tracer

    HAS_DDTRACE = True
except ImportError:
    HAS_DDTRACE = False
    tracer = None  # type: ignore[assignment]


def extract_trace_context(
    headers: dict[str, Any] | None = None, metadata: dict[str, Any] | None = None
) -> dict[str, str]:
    """Extract distributed trace context from HTTP headers or alert payload metadata.

    Supports W3C traceparent and Datadog headers:
    - traceparent: version-trace_id-parent_id-flags
    - x-datadog-trace-id: 64-bit integer
    """
    ctx: dict[str, str] = {}
    combined: dict[str, Any] = {}
    if headers:
        combined.update({k.lower(): str(v) for k, v in headers.items()})
    if metadata:
        combined.update({k.lower(): str(v) for k, v in metadata.items()})

    traceparent = combined.get("traceparent")
    if traceparent and len(traceparent.split("-")) >= 4:
        parts = traceparent.split("-")
        ctx["trace_id"] = parts[1]
        ctx["span_id"] = parts[2]
        ctx["traceparent"] = traceparent

    dd_trace_id = combined.get("x-datadog-trace-id")
    if dd_trace_id:
        ctx["datadog_trace_id"] = dd_trace_id
        if "trace_id" not in ctx:
            ctx["trace_id"] = dd_trace_id

    if "trace_id" not in ctx:
        ctx["trace_id"] = uuid.uuid4().hex

    return ctx


@contextlib.contextmanager
def trace_span(
    name: str, resource: str | None = None, service: str = "opsmesh"
) -> Iterator[dict[str, Any]]:
    """Context manager for distributed tracing spans.

    Uses Datadog tracer if installed and enabled, otherwise records span metadata locally.
    """
    span_id = uuid.uuid4().hex[:16]
    span_info: dict[str, Any] = {
        "span_name": name,
        "resource": resource or name,
        "service": service,
        "span_id": span_id,
    }

    if HAS_DDTRACE and settings.DATADOG_TRACE_ENABLED and tracer is not None:
        with tracer.trace(name, service=service, resource=resource) as span:
            span_info["dd_span_id"] = span.span_id
            span_info["dd_trace_id"] = span.trace_id
            yield span_info
    else:
        yield span_info


@contextlib.asynccontextmanager
async def trace_async_span(
    name: str, resource: str | None = None, service: str = "opsmesh"
) -> AsyncIterator[dict[str, Any]]:
    """Async context manager for tracing LangGraph agent nodes and asynchronous operations."""
    with trace_span(name=name, resource=resource, service=service) as span_info:
        yield span_info
