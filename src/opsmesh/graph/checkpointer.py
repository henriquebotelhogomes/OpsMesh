"""Persistence Checkpointer for LangGraph.

Supports in-memory checkpointer for development/testing/demo and
AsyncPostgresSaver for production PostgreSQL Serverless deployments (Neon/Supabase).
"""

from __future__ import annotations

import logging
from typing import Any

from langgraph.checkpoint.memory import MemorySaver

from opsmesh.core.config import settings

logger = logging.getLogger(__name__)

_memory_saver = MemorySaver()


async def get_checkpointer() -> Any:
    """Return an active checkpointer instance based on configuration."""
    if settings.APP_ENV in ("test", "development") or "localhost" in settings.DATABASE_URL:
        # Use in-memory checkpointer for zero-latency local development and tests
        return _memory_saver

    try:
        from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
        from psycopg_pool import AsyncConnectionPool

        pool = AsyncConnectionPool(conninfo=settings.DATABASE_URL, max_size=10, open=False)
        await pool.open()
        checkpointer = AsyncPostgresSaver(pool)
        await checkpointer.setup()
        return checkpointer
    except Exception as exc:
        logger.warning(
            "Could not connect to PostgreSQL checkpointer (%s), falling back to MemorySaver.", exc
        )
        return _memory_saver
