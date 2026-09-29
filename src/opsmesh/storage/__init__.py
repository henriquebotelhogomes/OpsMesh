"""Storage package for OpsMesh."""

from opsmesh.storage.analytics import query_incident_metrics, record_incident_analytics

__all__ = ["record_incident_analytics", "query_incident_metrics"]
