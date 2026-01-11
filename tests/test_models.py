"""Tests for data models."""

from hrp_mcp.models.hrp import (
    CertificationStatus,
    HRPPositionType,
    RemovalType,
)
from hrp_mcp.models.regulations import (
    HRPSubpart,
    RegulationChunk,
    SearchResult,
    get_subpart_for_section,
)


def test_hrp_subpart_enum():
    """Test HRPSubpart enum values."""
    assert HRPSubpart.SUBPART_A.value == "subpart_a"
    assert HRPSubpart.SUBPART_B.value == "subpart_b"


def test_regulation_chunk_creation():
    """Test creating a RegulationChunk."""
    chunk = RegulationChunk(
        id="hrp:712-11:chunk-000",
        subpart=HRPSubpart.SUBPART_A,
        section="712.11",
        title="General requirements",
        content="Test content for HRP certification.",
        citation="10 CFR 712.11",
        chunk_index=0,
    )

    assert chunk.id == "hrp:712-11:chunk-000"
    assert chunk.subpart == HRPSubpart.SUBPART_A
    assert chunk.section == "712.11"


def test_regulation_chunk_to_embedding_text():
    """Test embedding text generation."""
    chunk = RegulationChunk(
        id="hrp:712-11:chunk-000",
        subpart=HRPSubpart.SUBPART_A,
        section="712.11",
        title="General requirements",
        content="Test content.",
        citation="10 CFR 712.11",
        chunk_index=0,
    )

    text = chunk.to_embedding_text()
    assert "General requirements" in text
    assert "Test content" in text


def test_search_result_to_dict():
    """Test SearchResult serialization."""
    chunk = RegulationChunk(
        id="hrp:712-11:chunk-000",
        subpart=HRPSubpart.SUBPART_A,
        section="712.11",
        title="General requirements",
        content="Test content.",
        citation="10 CFR 712.11",
        chunk_index=0,
    )

    result = SearchResult(chunk=chunk, score=0.95)
    result_dict = result.to_dict()

    assert result_dict["section"] == "712.11"
    assert result_dict["score"] == 0.95
    assert "content" in result_dict


def test_get_subpart_for_section():
    """Test section to subpart mapping."""
    assert get_subpart_for_section("712.11") == HRPSubpart.SUBPART_A
    assert get_subpart_for_section("712.30") == HRPSubpart.SUBPART_B
    assert get_subpart_for_section("712.1") == HRPSubpart.SUBPART_A


def test_hrp_position_type_enum():
    """Test HRPPositionType enum."""
    assert HRPPositionType.CATEGORY_I_SNM is not None
    assert HRPPositionType.NUCLEAR_EXPLOSIVE is not None
    assert HRPPositionType.CATEGORY_I_SNM.value == "category_i_snm"


def test_certification_status_enum():
    """Test CertificationStatus enum."""
    assert CertificationStatus.CERTIFIED.value == "certified"
    assert CertificationStatus.PENDING.value == "pending"


def test_removal_type_enum():
    """Test RemovalType enum."""
    assert RemovalType.TEMPORARY.value == "temporary"
    assert RemovalType.PERMANENT.value == "permanent"
