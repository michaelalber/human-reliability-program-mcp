"""Custom exception hierarchy for HRP MCP."""


class HRPError(Exception):
    """Base exception for all HRP MCP errors."""

    pass


class SectionNotFoundError(HRPError):
    """Raised when a requested regulation section does not exist."""

    def __init__(self, section: str, subpart: str | None = None):
        self.section = section
        self.subpart = subpart
        if subpart:
            message = f"Section '{section}' not found in {subpart}"
        else:
            message = f"Section '{section}' not found in 10 CFR 712"
        super().__init__(message)


class TermNotFoundError(HRPError):
    """Raised when a requested HRP term/definition does not exist."""

    def __init__(self, term: str):
        self.term = term
        super().__init__(f"Term '{term}' not found in HRP definitions (10 CFR 712.3)")


class VectorStoreError(HRPError):
    """Raised for ChromaDB operation failures."""

    pass


class EmbeddingError(HRPError):
    """Raised when embedding generation fails."""

    pass


class AuditLogError(HRPError):
    """Raised when audit logging fails."""

    pass


class IngestionError(HRPError):
    """Raised when data ingestion fails."""

    def __init__(self, source: str, message: str):
        self.source = source
        super().__init__(f"Failed to ingest '{source}': {message}")


class DataNotFoundError(HRPError):
    """Raised when required data files are missing."""

    def __init__(self, path: str):
        self.path = path
        super().__init__(f"Required data not found at '{path}'. Run ingestion first.")
