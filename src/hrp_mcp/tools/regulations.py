"""Regulation search tools for HRP MCP.

Provides semantic search capabilities for 10 CFR Part 712 regulations,
section lookups, and HRP terminology definitions.
"""

from dataclasses import dataclass

from hrp_mcp.audit import audit_log
from hrp_mcp.models.regulations import HRPSubpart, RegulationChunk
from hrp_mcp.resources.reference_data import (
    HRP_SECTIONS,
    get_definition,
    get_section_info,
)
from hrp_mcp.server import mcp
from hrp_mcp.services import get_rag_service

# --- Section Retrieval Helpers ---


@dataclass
class SectionData:
    """Data retrieved for a regulation section."""

    content: str
    num_chunks: int
    subpart: str
    title: str


async def _fetch_section_from_rag(section_num: str) -> SectionData | None:
    """
    Fetch section data from RAG service.

    Returns SectionData if found, None if section not in vector store.
    """
    rag_service = get_rag_service()
    try:
        chunks: list[RegulationChunk] = await rag_service.get_section(section_num)
        if not chunks:
            return None

        return SectionData(
            content="\n\n".join(chunk.content for chunk in chunks),
            num_chunks=len(chunks),
            subpart=chunks[0].subpart.value if chunks[0].subpart else "unknown",
            title=chunks[0].title,
        )
    except Exception:
        return None


def _get_fallback_section_data(section_num: str) -> SectionData:
    """Get section data from reference data when RAG lookup fails."""
    section_info = get_section_info(section_num)
    return SectionData(
        content="",
        num_chunks=0,
        subpart=section_info.get("subpart", "A") if section_info else "A",
        title=section_info.get("title", "") if section_info else "",
    )


def _build_section_response(section_num: str, data: SectionData) -> dict:
    """Build the response dictionary for a section lookup."""
    # Normalize subpart format
    subpart = data.subpart
    if len(subpart) == 1:
        subpart = f"subpart_{subpart.lower()}"

    # Get title with fallback
    title = data.title or HRP_SECTIONS.get(section_num, {}).get("title", "")

    # Get content with fallback message
    content = data.content or "Section content not yet ingested. Run ingestion first."

    return {
        "section": section_num,
        "title": title,
        "subpart": subpart,
        "citation": f"10 CFR {section_num}",
        "content": content,
        "chunks": data.num_chunks,
    }


@mcp.tool()
@audit_log
async def search_10cfr712(
    query: str,
    subpart: str | None = None,
    limit: int = 10,
) -> list[dict]:
    """
    Search 10 CFR Part 712 (Human Reliability Program) using semantic search.

    Find relevant HRP provisions based on natural language queries. Use this
    to research HRP requirements, certification processes, medical standards,
    or procedural requirements.

    10 CFR Part 712 governs the Human Reliability Program for DOE/NNSA sites,
    ensuring individuals with access to certain materials, nuclear explosive
    devices, and facilities meet reliability and suitability standards.

    Args:
        query: Natural language search query describing what you're looking for.
               Examples:
               - "certification requirements for HRP"
               - "drug testing procedures"
               - "medical standards for HRP positions"
               - "temporary removal process"
               - "appeal rights after removal"
        subpart: Optional filter by subpart:
              - "A" or "subpart_a" - Procedures (712.1-712.25)
              - "B" or "subpart_b" - Medical Standards (712.30-712.38)
              Leave empty to search all sections.
        limit: Maximum number of results to return (1-50, default 10).

    Returns:
        List of matching regulation sections, each containing:
        - id: Unique chunk identifier
        - subpart: Subpart A or B
        - section: Section number (e.g., "712.11")
        - title: Section title
        - content: Relevant text content (truncated if long)
        - citation: CFR citation (e.g., "10 CFR 712.11")
        - score: Relevance score (0-1, higher is more relevant)
    """
    rag_service = get_rag_service()

    # Clamp limit to reasonable range
    limit = max(1, min(limit, 50))

    # Parse subpart filter
    subpart_filter = None
    if subpart:
        subpart_upper = subpart.upper().strip()
        if subpart_upper in ("A", "SUBPART_A", "SUBPART A"):
            subpart_filter = HRPSubpart.SUBPART_A
        elif subpart_upper in ("B", "SUBPART_B", "SUBPART B"):
            subpart_filter = HRPSubpart.SUBPART_B

    # Perform search
    results = await rag_service.search(
        query=query,
        subpart=subpart_filter,
        limit=limit,
    )

    # Format response for MCP
    return [r.to_dict() for r in results]


@mcp.tool()
@audit_log
async def get_section(section: str) -> dict:
    """
    Get the full text of a specific section of 10 CFR Part 712.

    Retrieve the complete content of a specific HRP regulation section.
    Use this when you know the exact section number you need.

    Args:
        section: Section number to retrieve. Examples:
                 - "712.11" (General requirements for HRP certification)
                 - "712.15" (Drug and alcohol testing)
                 - "712.19" (Temporary removal from HRP)
                 - "712.34" (Psychological evaluation)
                 Can also use just the number: "11" will be interpreted as "712.11"

    Returns:
        Section information containing:
        - section: Section number
        - title: Section title
        - subpart: Subpart A or B
        - citation: Full CFR citation
        - content: Complete section text
        - chunks: Number of chunks for this section
    """
    # Normalize section number
    section_num = section.strip()
    if not section_num.startswith("712."):
        section_num = f"712.{section_num}"

    # Try RAG service first, fall back to reference data
    data = await _fetch_section_from_rag(section_num)
    if data is None:
        data = _get_fallback_section_data(section_num)

    return _build_section_response(section_num, data)


@mcp.tool()
@audit_log
async def get_subpart(subpart: str) -> dict:
    """
    Get information about an entire subpart of 10 CFR Part 712.

    Retrieve a summary of all sections in a subpart.

    Args:
        subpart: Which subpart to retrieve:
                 - "A" - Establishment of and Procedures for the HRP (712.1-712.25)
                 - "B" - Medical Standards (712.30-712.38)

    Returns:
        Subpart information containing:
        - subpart: Subpart identifier
        - title: Subpart title
        - sections: List of section summaries in this subpart
    """
    subpart_upper = subpart.upper().strip()

    if subpart_upper in ("A", "SUBPART_A", "SUBPART A"):
        subpart_id = "A"
        title = "Establishment of and Procedures for the Human Reliability Program"
    elif subpart_upper in ("B", "SUBPART_B", "SUBPART B"):
        subpart_id = "B"
        title = "Medical Standards"
    else:
        return {
            "error": f"Invalid subpart '{subpart}'. Use 'A' or 'B'.",
            "valid_subparts": ["A", "B"],
        }

    # Get sections for this subpart
    sections = []
    for section_num, info in HRP_SECTIONS.items():
        if info.get("subpart") == subpart_id:
            sections.append(
                {
                    "section": section_num,
                    "title": info.get("title", ""),
                    "description": info.get("description", ""),
                    "citation": f"10 CFR {section_num}",
                }
            )

    # Sort by section number
    sections.sort(key=lambda x: float(x["section"].replace("712.", "")))

    return {
        "subpart": subpart_id,
        "title": title,
        "citation": f"10 CFR Part 712, Subpart {subpart_id}",
        "section_count": len(sections),
        "sections": sections,
    }


@mcp.tool()
@audit_log
async def explain_term(term: str) -> dict:
    """
    Look up the definition of an HRP term from 10 CFR 712.3.

    Find the official regulatory definition of terms used in the
    Human Reliability Program. These definitions come from 712.3
    and are important for proper interpretation of HRP requirements.

    Args:
        term: The term to look up. Examples:
              - "certifying official"
              - "designated physician"
              - "HRP candidate"
              - "safety concern"
              - "temporary removal"
              - "alcohol use disorder"
              Partial matches are supported.

    Returns:
        Definition information containing:
        - term: The official term name
        - definition: The regulatory definition
        - section: Source section (typically 712.3)
        - related_terms: List of related terms (if any)
    """
    result = get_definition(term)

    if result:
        return {
            "term": result.get("term", term),
            "definition": result.get("definition", ""),
            "section": result.get("section", "712.3"),
            "citation": f"10 CFR {result.get('section', '712.3')}",
            "found": True,
        }

    # Try to provide suggestions
    from hrp_mcp.resources.reference_data import HRP_DEFINITIONS

    suggestions = []
    term_lower = term.lower()
    for key, value in HRP_DEFINITIONS.items():
        if term_lower in key or term_lower in value.get("term", "").lower():
            suggestions.append(value.get("term", key))

    return {
        "term": term,
        "definition": None,
        "found": False,
        "message": f"Term '{term}' not found in HRP definitions.",
        "suggestions": suggestions[:5] if suggestions else [],
    }
