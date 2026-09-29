"""Serverless Columnar Analytics Engine (DuckDB + Parquet).

Provides zero-daemon OLAP analytics for historical incident tracking, MTTR calculation,
and financial ROI reporting (costs avoided in USD) without external databases.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

import duckdb

logger = logging.getLogger(__name__)

DEFAULT_PARQUET_PATH = "data/incidents.parquet"


def _ensure_data_dir(parquet_path: str) -> Path:
    """Ensure the target directory exists."""
    p = Path(parquet_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def record_incident_analytics(
    incident_data: dict[str, Any],
    parquet_path: str = DEFAULT_PARQUET_PATH,
) -> None:
    """Append a resolved incident record to the columnar Parquet analytics dataset."""
    target_path = _ensure_data_dir(parquet_path)

    incident_id = str(incident_data.get("incident_id", "INC-UNKNOWN"))
    service = str(incident_data.get("service", "shopcore-api"))
    severity = str(incident_data.get("severity", "P1_HIGH"))
    status = str(incident_data.get("status", "RESOLVED"))
    duration_min = float(incident_data.get("total_duration_minutes", 4.5))
    cost_avoided = float(incident_data.get("estimated_cost_avoided_usd", 12500.0))
    root_cause = str(incident_data.get("root_cause_summary", ""))[:250]
    timestamp = str(
        incident_data.get("created_at") or incident_data.get("timestamp", "2026-09-10T00:00:00Z")
    )

    con = duckdb.connect(database=":memory:")
    try:
        # Create temp table with the new row
        con.execute(
            """
            CREATE TABLE new_record (
                incident_id VARCHAR,
                service VARCHAR,
                severity VARCHAR,
                status VARCHAR,
                duration_minutes DOUBLE,
                cost_avoided_usd DOUBLE,
                root_cause VARCHAR,
                created_at VARCHAR
            )
            """
        )
        con.execute(
            """
            INSERT INTO new_record VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                incident_id,
                service,
                severity,
                status,
                duration_min,
                cost_avoided,
                root_cause,
                timestamp,
            ],
        )

        if target_path.exists() and os.path.getsize(target_path) > 0:
            # Union existing parquet and new record
            con.execute(
                f"""
                COPY (
                    SELECT * FROM read_parquet('{target_path.as_posix()}')
                    UNION ALL
                    SELECT * FROM new_record
                ) TO '{target_path.as_posix()}' (FORMAT PARQUET)
                """
            )
        else:
            con.execute(
                f"""
                COPY new_record TO '{target_path.as_posix()}' (FORMAT PARQUET)
                """
            )
    except Exception as exc:
        logger.warning("Failed to record incident analytics to Parquet: %s", exc)
    finally:
        con.close()


def query_incident_metrics(
    parquet_path: str = DEFAULT_PARQUET_PATH,
) -> dict[str, Any]:
    """Execute SQL analytics queries over the Parquet store using DuckDB."""
    target_path = Path(parquet_path)

    # If no data exists yet, return nominal baseline metrics
    if not target_path.exists() or os.path.getsize(target_path) == 0:
        return {
            "total_incidents": 0,
            "avg_mttr_minutes": 0.0,
            "total_cost_avoided_usd": 0.0,
            "service_breakdown": {},
        }

    con = duckdb.connect(database=":memory:")
    try:
        res = con.execute(
            f"""
            SELECT
                count(*) AS total,
                round(avg(duration_minutes), 2) AS avg_mttr,
                round(sum(cost_avoided_usd), 2) AS total_savings
            FROM read_parquet('{target_path.as_posix()}')
            """
        ).fetchone()

        breakdown_rows = con.execute(
            f"""
            SELECT service, count(*) AS count
            FROM read_parquet('{target_path.as_posix()}')
            GROUP BY service
            ORDER BY count DESC
            """
        ).fetchall()

        breakdown = {row[0]: row[1] for row in breakdown_rows}

        return {
            "total_incidents": res[0] if res else 0,
            "avg_mttr_minutes": float(res[1]) if res and res[1] is not None else 0.0,
            "total_cost_avoided_usd": float(res[2]) if res and res[2] is not None else 0.0,
            "service_breakdown": breakdown,
        }
    except Exception as exc:
        logger.warning("DuckDB query on Parquet failed: %s", exc)
        return {
            "total_incidents": 0,
            "avg_mttr_minutes": 0.0,
            "total_cost_avoided_usd": 0.0,
            "service_breakdown": {},
        }
    finally:
        con.close()
