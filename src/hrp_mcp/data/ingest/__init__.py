"""Data ingestion modules for HRP MCP server."""

from hrp_mcp.data.ingest.base import BaseIngestor, IngestResult
from hrp_mcp.data.ingest.ecfr_ingest import HRPIngestor

__all__ = [
    "BaseIngestor",
    "IngestResult",
    "HRPIngestor",
]
