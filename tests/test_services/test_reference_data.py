"""Tests for reference data."""

from hrp_mcp.resources.reference_data import (
    HRP_DEFINITIONS,
    HRP_POSITION_TYPES,
    HRP_SECTIONS,
    get_definition,
    get_position_type,
    get_section_info,
)


def test_hrp_definitions_exist():
    """Test that HRP definitions are loaded."""
    assert len(HRP_DEFINITIONS) > 0
    # Use lowercase key as per the implementation
    assert "human_reliability_program" in HRP_DEFINITIONS


def test_get_definition_exact():
    """Test exact term lookup."""
    result = get_definition("hrp")
    assert result is not None
    # The definition mentions reliability program
    assert "reliability" in result["definition"].lower()


def test_get_definition_full_term():
    """Test full term lookup."""
    result = get_definition("human_reliability_program")
    assert result is not None
    assert result["term"] == "Human Reliability Program (HRP)"


def test_get_definition_case_insensitive():
    """Test case-insensitive lookup."""
    result = get_definition("HRP")
    assert result is not None


def test_get_definition_not_found():
    """Test lookup for non-existent term."""
    result = get_definition("nonexistent_term_xyz")
    assert result is None


def test_position_types_exist():
    """Test that position types are loaded."""
    assert len(HRP_POSITION_TYPES) > 0


def test_get_position_type():
    """Test position type lookup."""
    # Test looking up by category name in the list
    result = get_position_type("category_i_snm")
    assert result is not None


def test_hrp_sections_exist():
    """Test that HRP sections are loaded."""
    assert len(HRP_SECTIONS) > 0
    assert "712.1" in HRP_SECTIONS
    assert "712.11" in HRP_SECTIONS


def test_get_section_info():
    """Test section info lookup."""
    result = get_section_info("712.11")
    assert result is not None
    assert result["section"] == "712.11"
    assert "subpart" in result
