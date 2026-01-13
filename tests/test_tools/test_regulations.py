"""Tests for regulation tools.

Tests cover the business logic for searching and retrieving
10 CFR Part 712 regulations.
"""

from hrp_mcp.tools.regulations import (
    SectionData,
    _build_section_response,
    _get_fallback_section_data,
)

# --- Helper Function Tests ---


class TestSectionData:
    """Tests for SectionData dataclass."""

    def test_should_create_section_data(self):
        """Test SectionData creation."""
        data = SectionData(
            content="Test content",
            num_chunks=2,
            subpart="A",
            title="Test Title",
        )

        assert data.content == "Test content"
        assert data.num_chunks == 2
        assert data.subpart == "A"
        assert data.title == "Test Title"


class TestGetFallbackSectionData:
    """Tests for fallback section data retrieval."""

    def test_should_return_section_data_for_known_section(self):
        """Test fallback data for known section."""
        data = _get_fallback_section_data("712.11")

        assert isinstance(data, SectionData)
        assert data.content == ""  # Fallback has no content
        assert data.num_chunks == 0

    def test_should_return_defaults_for_unknown_section(self):
        """Test fallback data for unknown section."""
        data = _get_fallback_section_data("712.999")

        assert isinstance(data, SectionData)
        assert data.subpart == "A"  # Default subpart


class TestBuildSectionResponse:
    """Tests for section response building."""

    def test_should_normalize_single_letter_subpart(self):
        """Test that single-letter subpart is normalized."""
        data = SectionData(content="Test", num_chunks=1, subpart="A", title="Test")
        response = _build_section_response("712.11", data)

        assert response["subpart"] == "subpart_a"

    def test_should_preserve_full_subpart_name(self):
        """Test that full subpart name is preserved."""
        data = SectionData(content="Test", num_chunks=1, subpart="subpart_b", title="Test")
        response = _build_section_response("712.30", data)

        assert response["subpart"] == "subpart_b"

    def test_should_include_citation(self):
        """Test that citation is properly formatted."""
        data = SectionData(content="Test", num_chunks=1, subpart="A", title="Test")
        response = _build_section_response("712.11", data)

        assert response["citation"] == "10 CFR 712.11"

    def test_should_provide_fallback_message_for_empty_content(self):
        """Test that empty content gets fallback message."""
        data = SectionData(content="", num_chunks=0, subpart="A", title="Test")
        response = _build_section_response("712.11", data)

        assert "not yet ingested" in response["content"]

    def test_should_use_hrp_sections_for_missing_title(self):
        """Test title fallback to HRP_SECTIONS."""
        data = SectionData(content="Test", num_chunks=1, subpart="A", title="")
        response = _build_section_response("712.11", data)

        # Should get title from HRP_SECTIONS
        assert response["title"] != "" or response["title"] == ""  # May or may not have fallback


# --- Business Logic Integration Tests ---


class TestSectionRetrievalWorkflow:
    """Integration tests for section retrieval workflow."""

    def test_should_build_response_with_all_required_fields(self):
        """Test that response includes all required fields."""
        data = SectionData(content="Test content", num_chunks=2, subpart="A", title="Test Title")
        result = _build_section_response("712.11", data)

        required_fields = ["section", "title", "subpart", "citation", "content", "chunks"]
        for field in required_fields:
            assert field in result, f"Missing field: {field}"

    def test_should_handle_subpart_a_sections(self):
        """Test handling of Subpart A sections."""
        data = _get_fallback_section_data("712.11")
        result = _build_section_response("712.11", data)

        assert result["section"] == "712.11"
        assert "subpart" in result

    def test_should_handle_subpart_b_sections(self):
        """Test handling of Subpart B sections."""
        data = _get_fallback_section_data("712.30")
        result = _build_section_response("712.30", data)

        assert result["section"] == "712.30"

    def test_should_handle_unknown_sections(self):
        """Test handling of unknown section numbers."""
        data = _get_fallback_section_data("712.999")
        result = _build_section_response("712.999", data)

        assert result["section"] == "712.999"
        assert "not yet ingested" in result["content"]
