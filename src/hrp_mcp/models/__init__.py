"""Data models for HRP MCP server."""

from hrp_mcp.models.errors import (
    AuditLogError,
    DataNotFoundError,
    EmbeddingError,
    HRPError,
    IngestionError,
    SectionNotFoundError,
    TermNotFoundError,
    VectorStoreError,
)
from hrp_mcp.models.hrp import (
    AppealProcess,
    CertificationComponent,
    CertificationRequirement,
    CertificationStatus,
    DisqualifyingCategory,
    DisqualifyingFactor,
    HRPPositionType,
    HRPRole,
    HRPRoleInfo,
    MedicalStandard,
    PositionTypeInfo,
    ReinstatementProcess,
    RemovalProcess,
    RemovalType,
    TestingRequirement,
    TestType,
)
from hrp_mcp.models.regulations import (
    HRPSubpart,
    RegulationChunk,
    SearchResult,
    SectionInfo,
    get_subpart_for_section,
)

__all__ = [
    # Errors
    "HRPError",
    "SectionNotFoundError",
    "TermNotFoundError",
    "VectorStoreError",
    "EmbeddingError",
    "AuditLogError",
    "IngestionError",
    "DataNotFoundError",
    # Regulations
    "HRPSubpart",
    "RegulationChunk",
    "SearchResult",
    "SectionInfo",
    "get_subpart_for_section",
    # HRP Models
    "HRPPositionType",
    "CertificationStatus",
    "RemovalType",
    "DisqualifyingCategory",
    "TestType",
    "HRPRole",
    "PositionTypeInfo",
    "CertificationRequirement",
    "CertificationComponent",
    "DisqualifyingFactor",
    "MedicalStandard",
    "TestingRequirement",
    "RemovalProcess",
    "ReinstatementProcess",
    "AppealProcess",
    "HRPRoleInfo",
]
