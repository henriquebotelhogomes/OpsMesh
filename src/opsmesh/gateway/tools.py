"""Mock Observability Tools for OpsMesh.

Simulates observability systems (LogHub/Elasticsearch/Loki, PostgreSQL pg_stat_activity,
and Kubernetes API) with strict read-only guarantees and output truncation guardrails
(maximum 2,000 characters per call to avoid context window explosion).
"""

from __future__ import annotations

import json
from typing import Any

MAX_TOOL_OUTPUT_CHARS = 2000


def truncate_tool_output(output: str, max_chars: int = MAX_TOOL_OUTPUT_CHARS) -> str:
    """Truncate tool output if it exceeds max_chars, appending a warning indicator."""
    if len(output) <= max_chars:
        return output
    truncated = output[:max_chars]
    suffix = f"\n... [TRUNCATED: Output exceeded {max_chars} characters. FinOps guardrail active.]"
    return truncated[: max_chars - len(suffix)] + suffix


def query_logs(filter_query: str, time_range: str = "15m", limit: int = 50) -> str:
    """Search and query application and system logs with a query filter.

    Args:
        filter_query: Lucene or regex filter string (e.g., 'error', 'timeout', 'PostgreSQL').
        time_range: Time range to search (e.g., '15m', '1h', '24h').
        limit: Maximum number of log lines to retrieve (default 50).

    Returns:
        Structured string of matched log entries, truncated to 2000 chars max.
    """
    q = filter_query.lower()

    # Scenario matching for realistic incident diagnosis
    if "postgres" in q or "pool" in q or "connection" in q or "db" in q:
        entries = [
            {
                "timestamp": "2026-09-10T00:14:22Z",
                "level": "ERROR",
                "service": "order-service",
                "message": "FATAL: remaining connection slots are reserved for non-replication superuser connections",
            },
            {
                "timestamp": "2026-09-10T00:14:25Z",
                "level": "ERROR",
                "service": "payment-service",
                "message": "asyncpg.exceptions.TooManyConnectionsError: connection pool exhausted (max_size=20 reached, queue_wait > 5000ms)",
            },
            {
                "timestamp": "2026-09-10T00:14:31Z",
                "level": "WARN",
                "service": "cart-service",
                "message": "DbConnectionTimeout: Failed to acquire connection within 5.00s. Retrying attempt 3/3.",
            },
            {
                "timestamp": "2026-09-10T00:14:35Z",
                "level": "ERROR",
                "service": "order-service",
                "message": "HTTP 500 Internal Server Error: Database unreachable, terminating worker process pid=10492",
            },
            {
                "timestamp": "2026-09-10T00:14:40Z",
                "level": "ERROR",
                "service": "ingress-nginx",
                "message": "upstream server temporarily disabled while connecting to upstream: 10.244.2.45:8000",
            },
        ]
    elif "checkout" in q or "cart" in q or "500" in q or "504" in q:
        entries = [
            {
                "timestamp": "2026-09-10T00:12:00Z",
                "level": "ERROR",
                "service": "checkout-api",
                "message": "GatewayTimeout: Upstream inventory-service timed out after 3000ms at /api/v1/stock/reserve",
            },
            {
                "timestamp": "2026-09-10T00:12:15Z",
                "level": "ERROR",
                "service": "checkout-api",
                "message": "CircuitBreakerOpenException: inventory-service circuit opened. Fallback rejected.",
            },
            {
                "timestamp": "2026-09-10T00:12:30Z",
                "level": "WARN",
                "service": "frontend-proxy",
                "message": "Client IP [REDACTED_PUBLIC_IP] received HTTP 504 on POST /checkout/submit",
            },
        ]
    elif "payment" in q or "gateway" in q or "stripe" in q:
        entries = [
            {
                "timestamp": "2026-09-10T00:10:05Z",
                "level": "WARN",
                "service": "payment-worker",
                "message": "External payment gateway latency spike: p99 reached 12.4s (threshold: 2.0s)",
            },
            {
                "timestamp": "2026-09-10T00:10:20Z",
                "level": "ERROR",
                "service": "payment-worker",
                "message": "ConnectionRefusedError: Failed to connect to payment acquirer socket 172.16.40.12:8443: Connection timed out",
            },
            {
                "timestamp": "2026-09-10T00:10:45Z",
                "level": "ERROR",
                "service": "payment-service",
                "message": "PaymentProcessingException: Webhook verification failed for transaction tx_991823",
            },
        ]
    elif "oom" in q or "memory" in q or "drift" in q or "cpu" in q:
        entries = [
            {
                "timestamp": "2026-09-10T00:08:10Z",
                "level": "WARN",
                "service": "recommendation-ml",
                "message": "RSS memory consumption crossed 92% of limit (3.68GB / 4.00GB)",
            },
            {
                "timestamp": "2026-09-10T00:08:45Z",
                "level": "ERROR",
                "service": "kernel",
                "message": "Out of memory: Kill process 8841 (python -m worker) score 950 or sacrifice child",
            },
            {
                "timestamp": "2026-09-10T00:09:00Z",
                "level": "ERROR",
                "service": "kubelet",
                "message": "Container recommendation-engine in pod recommendation-ml-7bc994-x8k2 terminated with exitCode 137 (OOMKilled)",
            },
        ]
    else:
        entries = [
            {
                "timestamp": "2026-09-10T00:15:00Z",
                "level": "INFO",
                "service": "system",
                "message": f"Log search for '{filter_query}' within {time_range}: No specific critical anomalies found in recent windows.",
            },
            {
                "timestamp": "2026-09-10T00:15:02Z",
                "level": "WARN",
                "service": "system",
                "message": "Elevated warning rate: 14% higher than baseline for current hour.",
            },
        ]

    formatted = json.dumps(entries[:limit], indent=2, ensure_ascii=False)
    return truncate_tool_output(formatted)


def inspect_database_activity(metric: str = "connections") -> str:
    """Inspect PostgreSQL server state (pg_stat_activity, pool saturation, locks) in Read-Only mode.

    Args:
        metric: Diagnostic metric to query ('connections', 'locks', 'slow_queries', 'pool').

    Returns:
        Structured JSON string containing database diagnostic data, truncated to 2000 chars.
    """
    m = metric.lower()

    if "conn" in m or "pool" in m:
        data: dict[str, Any] = {
            "query": "SELECT count(*), state FROM pg_stat_activity GROUP BY state",
            "max_connections": 100,
            "active_connections": 98,
            "idle_in_transaction": 42,
            "waiting_connections": 36,
            "connection_pool_utilization_pct": 98.0,
            "longest_idle_transaction_seconds": 1824.5,
            "sample_stuck_query": "SELECT * FROM orders WHERE status = 'PENDING' FOR UPDATE NOWAIT",
            "status": "CRITICAL_SATURATION",
        }
    elif "lock" in m:
        data = {
            "query": "SELECT relation::regclass, mode, granted FROM pg_locks WHERE NOT granted",
            "blocked_queries_count": 27,
            "primary_blocking_pid": 10492,
            "lock_type": "ExclusiveLock",
            "relation": "orders_partition_2026_09",
            "status": "DEADLOCK_RISK",
        }
    else:
        data = {
            "query": "SELECT pid, query_start, state, query FROM pg_stat_activity WHERE state != 'idle'",
            "slow_queries_count": 12,
            "p95_query_duration_sec": 48.2,
            "top_slow_query": "SELECT * FROM audit_logs WHERE payload LIKE '%error%' ORDER BY id DESC",
            "status": "HIGH_LATENCY",
        }

    formatted = json.dumps(data, indent=2, ensure_ascii=False)
    return truncate_tool_output(formatted)


def check_k8s_deployment_health(service_name: str) -> str:
    """Check Kubernetes Deployment and Pod status for a microservice in Read-Only mode.

    Args:
        service_name: Name of the Kubernetes service/deployment to inspect.

    Returns:
        Structured JSON string describing pod replicas, restart counts, and status events.
    """
    s = service_name.lower()

    if "rec" in s or "ml" in s or "model" in s:
        data = {
            "deployment": service_name,
            "namespace": "production",
            "desired_replicas": 3,
            "ready_replicas": 1,
            "available_replicas": 1,
            "pods": [
                {
                    "name": f"{service_name}-pod-1",
                    "status": "Running",
                    "restart_count": 0,
                    "node": "k8s-node-worker-01",
                },
                {
                    "name": f"{service_name}-pod-2",
                    "status": "CrashLoopBackOff",
                    "restart_count": 7,
                    "last_exit_code": 137,
                    "reason": "OOMKilled",
                    "node": "k8s-node-worker-02",
                },
                {
                    "name": f"{service_name}-pod-3",
                    "status": "CrashLoopBackOff",
                    "restart_count": 9,
                    "last_exit_code": 137,
                    "reason": "OOMKilled",
                    "node": "k8s-node-worker-03",
                },
            ],
            "events": [
                "Pod was OOMKilled: container exceeded memory limit 4096Mi",
                "Liveness probe failed: HTTP probe failed with statuscode: 503",
            ],
        }
    elif "order" in s or "db" in s or "cart" in s or "checkout" in s:
        data = {
            "deployment": service_name,
            "namespace": "production",
            "desired_replicas": 4,
            "ready_replicas": 4,
            "available_replicas": 4,
            "pods": [
                {
                    "name": f"{service_name}-pod-{i}",
                    "status": "Running",
                    "restart_count": 1,
                    "cpu_usage_pct": 88.5,
                    "memory_usage_pct": 74.0,
                }
                for i in range(1, 5)
            ],
            "events": [
                "Connection pool error logs detected on stdout",
                "Readiness probe latency warning: 1800ms response time",
            ],
        }
    else:
        data = {
            "deployment": service_name,
            "namespace": "production",
            "desired_replicas": 2,
            "ready_replicas": 2,
            "available_replicas": 2,
            "pods": [
                {"name": f"{service_name}-pod-1", "status": "Running", "restart_count": 0},
                {"name": f"{service_name}-pod-2", "status": "Running", "restart_count": 0},
            ],
            "events": ["All health checks passing nominally."],
        }

    formatted = json.dumps(data, indent=2, ensure_ascii=False)
    return truncate_tool_output(formatted)
