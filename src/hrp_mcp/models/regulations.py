"""Pydantic models for HRP regulations (10 CFR Part 712)."""

from enum import Enum

from pydantic import BaseModel, Field


class HRPSubpart(str, Enum):
    """Subparts of 10 CFR Part 712."""

    SUBPART_A = "subpart_a"  # Establishment of and Procedures for the HRP (712.1-712.25)
    SUBPART_B = "subpart_b"  # Medical Standards (712.30-712.38)


# Section to subpart mapping
SECTION_SUBPARTS = {
    # Subpart A - Procedures
    "712.1": HRPSubpart.SUBPART_A,
    "712.2": HRPSubpart.SUBPART_A,
    "712.3": HRPSubpart.SUBPART_A,
    "712.10": HRPSubpart.SUBPART_A,
    "712.11": HRPSubpart.SUBPART_A,
    "712.12": HRPSubpart.SUBPART_A,
    "712.13": HRPSubpart.SUBPART_A,
    "712.14": HRPSubpart.SUBPART_A,
    "712.15": HRPSubpart.SUBPART_A,
    "712.16": HRPSubpart.SUBPART_A,
    "712.17": HRPSubpart.SUBPART_A,
    "712.18": HRPSubpart.SUBPART_A,
    "712.19": HRPSubpart.SUBPART_A,
    "712.20": HRPSubpart.SUBPART_A,
    "712.21": HRPSubpart.SUBPART_A,
    "712.22": HRPSubpart.SUBPART_A,
    "712.23": HRPSubpart.SUBPART_A,
    "712.24": HRPSubpart.SUBPART_A,
    "712.25": HRPSubpart.SUBPART_A,
    # Subpart B - Medical Standards
    "712.30": HRPSubpart.SUBPART_B,
    "712.31": HRPSubpart.SUBPART_B,
    "712.32": HRPSubpart.SUBPART_B,
    "712.33": HRPSubpart.SUBPART_B,
    "712.34": HRPSubpart.SUBPART_B,
    "712.35": HRPSubpart.SUBPART_B,
    "712.36": HRPSubpart.SUBPART_B,
    "712.37": HRPSubpart.SUBPART_B,
    "712.38": HRPSubpart.SUBPART_B,
}


def get_subpart_for_section(section: str) -> HRPSubpart:
    """Determine which subpart a section belongs to."""
    if section in SECTION_SUBPARTS:
        return SECTION_SUBPARTS[section]
    # Default logic based on section number
    section_num = section.replace("712.", "")
    try:
        num = int(section_num.split(".")[0])
        if num < 30:
            return HRPSubpart.SUBPART_A
        return HRPSubpart.SUBPART_B
    except ValueError:
        return HRPSubpart.SUBPART_A


class RegulationChunk(BaseModel):
    """A chunk of regulation text with metadata for vector storage."""

    id: str = Field(..., description="Unique chunk ID (e.g., 'hrp:712.11:chunk-000')")
    subpart: HRPSubpart = Field(..., description="Subpart A (Procedures) or B (Medical)")
    section: str = Field(..., description="Section number (e.g., '712.11')")
    title: str = Field(..., description="Section title")
    content: str = Field(..., description="Full text content of this chunk")
    citation: str = Field(..., description="CFR citation (e.g., '10 CFR 712.11')")
    chunk_index: int = Field(default=0, description="Index if content was split into chunks")

    def to_embedding_text(self) -> str:
        """Generate text for embedding generation.

        Combines title and content for semantic search.
        """
        return f"{self.title}\n\n{self.content}"


class SearchResult(BaseModel):
    """Search result containing a regulation chunk with relevance score."""

    chunk: RegulationChunk = Field(..., description="The matched regulation chunk")
    score: float = Field(..., description="Relevance score (0-1, higher is better)")

    def to_dict(self) -> dict:
        """Convert to dictionary for MCP tool response."""
        return {
            "id": self.chunk.id,
            "subpart": self.chunk.subpart.value,
            "section": self.chunk.section,
            "title": self.chunk.title,
            "content": self.chunk.content[:500] + "..."
            if len(self.chunk.content) > 500
            else self.chunk.content,
            "citation": self.chunk.citation,
            "score": round(self.score, 3),
        }


class SectionInfo(BaseModel):
    """Information about a specific section of 10 CFR 712."""

    section: str = Field(..., description="Section number (e.g., '712.11')")
    title: str = Field(..., description="Section title")
    subpart: HRPSubpart = Field(..., description="Subpart A or B")
    citation: str = Field(..., description="Full CFR citation")
    content: str = Field(..., description="Full section text")
    related_sections: list[str] = Field(
        default_factory=list,
        description="Related section numbers",
    )

    def to_dict(self) -> dict:
        """Convert to dictionary for MCP tool response."""
        return {
            "section": self.section,
            "title": self.title,
            "subpart": self.subpart.value,
            "citation": self.citation,
            "content": self.content,
            "related_sections": self.related_sections,
        }
