"""Tests for data ingestion functionality.

Tests cover IngestResult, CFRPartIngestor initialization,
XML parsing helpers, and section extraction logic.
"""

from xml.etree.ElementTree import Element, SubElement

import pytest

from hrp_mcp.data.ingest.base import IngestResult
from hrp_mcp.data.ingest.ecfr_ingest import CFR_PARTS, CFRPartIngestor
from hrp_mcp.models.regulations import SourceType

# --- IngestResult Tests ---


class TestIngestResult:
    """Tests for IngestResult dataclass."""

    def test_should_initialize_with_defaults(self):
        """Test default initialization."""
        result = IngestResult()

        assert result.sections_ingested == 0
        assert result.chunks_created == 0
        assert result.errors == []

    def test_should_return_success_false_when_no_chunks(self):
        """Test success property when no chunks created."""
        result = IngestResult(sections_ingested=5, chunks_created=0)

        assert result.success is False

    def test_should_return_success_true_when_chunks_created(self):
        """Test success property when chunks created."""
        result = IngestResult(sections_ingested=5, chunks_created=10)

        assert result.success is True

    def test_should_add_error_message(self):
        """Test add_error method."""
        result = IngestResult()

        result.add_error("First error")
        result.add_error("Second error")

        assert len(result.errors) == 2
        assert "First error" in result.errors
        assert "Second error" in result.errors

    def test_should_allow_success_with_errors(self):
        """Test that success is based on chunks, not errors."""
        result = IngestResult(chunks_created=5)
        result.add_error("Non-fatal warning")

        assert result.success is True
        assert len(result.errors) == 1


# --- CFRPartIngestor Initialization Tests ---


class TestCFRPartIngestorInit:
    """Tests for CFRPartIngestor initialization."""

    def test_should_initialize_with_default_part(self):
        """Test default initialization uses Part 712."""
        ingestor = CFRPartIngestor()

        assert ingestor.part == 712
        assert ingestor.source_type == SourceType.CFR_712

    def test_should_initialize_with_part_707(self):
        """Test initialization with Part 707."""
        ingestor = CFRPartIngestor(part=707)

        assert ingestor.part == 707
        assert ingestor.source_type == SourceType.CFR_707

    def test_should_initialize_with_part_710(self):
        """Test initialization with Part 710."""
        ingestor = CFRPartIngestor(part=710)

        assert ingestor.part == 710
        assert ingestor.source_type == SourceType.CFR_710

    def test_should_initialize_with_custom_batch_size(self):
        """Test initialization with custom batch size."""
        ingestor = CFRPartIngestor(batch_size=100)

        assert ingestor.batch_size == 100

    def test_should_raise_for_unsupported_part(self):
        """Test that unsupported part raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported part"):
            CFRPartIngestor(part=999)

    def test_should_have_all_supported_parts_configured(self):
        """Test that CFR_PARTS has expected parts."""
        assert 707 in CFR_PARTS
        assert 710 in CFR_PARTS
        assert 712 in CFR_PARTS


# --- Tag Name Helper Tests ---


class TestCFRPartIngestorGetTagName:
    """Tests for _get_tag_name helper method."""

    def test_should_extract_simple_tag_name(self):
        """Test extraction from simple tag."""
        ingestor = CFRPartIngestor()
        elem = Element("SECTION")

        result = ingestor._get_tag_name(elem)

        assert result == "SECTION"

    def test_should_extract_namespaced_tag_name(self):
        """Test extraction from namespaced tag."""
        ingestor = CFRPartIngestor()
        elem = Element("{http://example.com/ns}SECTNO")

        result = ingestor._get_tag_name(elem)

        assert result == "SECTNO"

    def test_should_return_uppercase(self):
        """Test that result is uppercase."""
        ingestor = CFRPartIngestor()
        elem = Element("section")

        result = ingestor._get_tag_name(elem)

        assert result == "SECTION"


# --- Find Child Text Tests ---


class TestCFRPartIngestorFindChildText:
    """Tests for _find_child_text helper method."""

    def test_should_find_matching_child_text(self):
        """Test finding text from matching child element."""
        ingestor = CFRPartIngestor()
        parent = Element("SECTION")
        child = SubElement(parent, "SECTNO")
        child.text = "§ 712.11"

        result = ingestor._find_child_text(parent, "SECTNO")

        assert result == "§ 712.11"

    def test_should_return_none_when_no_match(self):
        """Test returning None when no matching child."""
        ingestor = CFRPartIngestor()
        parent = Element("SECTION")
        SubElement(parent, "HEAD").text = "Title"

        result = ingestor._find_child_text(parent, "SECTNO")

        assert result is None

    def test_should_return_none_for_empty_text(self):
        """Test returning None when child has empty text."""
        ingestor = CFRPartIngestor()
        parent = Element("SECTION")
        child = SubElement(parent, "SECTNO")
        child.text = "   "

        result = ingestor._find_child_text(parent, "SECTNO")

        assert result is None

    def test_should_strip_whitespace(self):
        """Test that whitespace is stripped from text."""
        ingestor = CFRPartIngestor()
        parent = Element("SECTION")
        child = SubElement(parent, "SECTNO")
        child.text = "  § 712.11  "

        result = ingestor._find_child_text(parent, "SECTNO")

        assert result == "§ 712.11"


# --- Match Section Number Tests ---


class TestCFRPartIngestorMatchSectionNumber:
    """Tests for _match_section_number helper method."""

    def test_should_match_section_number(self):
        """Test matching valid section number."""
        ingestor = CFRPartIngestor(part=712)

        result = ingestor._match_section_number("§ 712.11 Purpose")

        assert result == "712.11"

    def test_should_match_section_without_symbol(self):
        """Test matching section number without § symbol."""
        ingestor = CFRPartIngestor(part=712)

        result = ingestor._match_section_number("712.15 Drug testing")

        assert result == "712.15"

    def test_should_return_none_for_wrong_part(self):
        """Test returning None when part doesn't match."""
        ingestor = CFRPartIngestor(part=712)

        result = ingestor._match_section_number("§ 710.5 Purpose")

        assert result is None

    def test_should_return_none_for_no_match(self):
        """Test returning None when no section number found."""
        ingestor = CFRPartIngestor(part=712)

        result = ingestor._match_section_number("No section number here")

        assert result is None

    def test_should_match_different_parts(self):
        """Test matching with different part numbers."""
        ingestor_707 = CFRPartIngestor(part=707)
        ingestor_710 = CFRPartIngestor(part=710)

        assert ingestor_707._match_section_number("707.5") == "707.5"
        assert ingestor_710._match_section_number("710.10") == "710.10"


# --- Extract Section Number Tests ---


class TestCFRPartIngestorExtractSectionNumber:
    """Tests for _extract_section_number method."""

    def test_should_extract_from_sectno_element(self):
        """Test extraction from SECTNO child element."""
        ingestor = CFRPartIngestor(part=712)
        section = Element("SECTION")
        sectno = SubElement(section, "SECTNO")
        sectno.text = "§ 712.11"

        result = ingestor._extract_section_number(section)

        assert result == "712.11"

    def test_should_extract_from_head_element(self):
        """Test extraction from HEAD child element when no SECTNO."""
        ingestor = CFRPartIngestor(part=712)
        section = Element("SECTION")
        head = SubElement(section, "HEAD")
        head.text = "712.15 Drug testing"

        result = ingestor._extract_section_number(section)

        assert result == "712.15"

    def test_should_extract_from_n_attribute(self):
        """Test extraction from N attribute as fallback."""
        ingestor = CFRPartIngestor(part=712)
        section = Element("SECTION", N="712.20")

        result = ingestor._extract_section_number(section)

        assert result == "712.20"

    def test_should_return_none_when_not_found(self):
        """Test returning None when section number not found."""
        ingestor = CFRPartIngestor(part=712)
        section = Element("SECTION")
        SubElement(section, "P").text = "Some content"

        result = ingestor._extract_section_number(section)

        assert result is None

    def test_should_prefer_sectno_over_head(self):
        """Test that SECTNO is preferred over HEAD element."""
        ingestor = CFRPartIngestor(part=712)
        section = Element("SECTION")
        sectno = SubElement(section, "SECTNO")
        sectno.text = "§ 712.11"
        head = SubElement(section, "HEAD")
        head.text = "712.99 Wrong"

        result = ingestor._extract_section_number(section)

        assert result == "712.11"


# --- Clean Title Text Tests ---


class TestCFRPartIngestorCleanTitleText:
    """Tests for _clean_title_text helper method."""

    def test_should_remove_section_prefix_with_symbol(self):
        """Test removing section prefix with § symbol."""
        ingestor = CFRPartIngestor(part=712)

        result = ingestor._clean_title_text("§ 712.11 Purpose")

        assert result == "Purpose"

    def test_should_remove_section_prefix_without_symbol(self):
        """Test removing section prefix without § symbol."""
        ingestor = CFRPartIngestor(part=712)

        result = ingestor._clean_title_text("712.15 Drug testing")

        assert result == "Drug testing"

    def test_should_preserve_text_without_prefix(self):
        """Test preserving text that has no section prefix."""
        ingestor = CFRPartIngestor(part=712)

        result = ingestor._clean_title_text("Drug testing requirements")

        assert result == "Drug testing requirements"


# --- Extract Title Tests ---


class TestCFRPartIngestorExtractTitle:
    """Tests for _extract_title method."""

    def test_should_extract_from_subject_element(self):
        """Test extraction from SUBJECT child element."""
        ingestor = CFRPartIngestor(part=712)
        section = Element("SECTION")
        subject = SubElement(section, "SUBJECT")
        subject.text = "Purpose"
        section_titles = {"712.11": "Fallback Title"}

        result = ingestor._extract_title(section, "712.11", section_titles)

        assert result == "Purpose"

    def test_should_extract_from_head_element(self):
        """Test extraction from HEAD when no SUBJECT."""
        ingestor = CFRPartIngestor(part=712)
        section = Element("SECTION")
        head = SubElement(section, "HEAD")
        head.text = "§ 712.15 Drug testing"
        section_titles = {"712.15": "Fallback Title"}

        result = ingestor._extract_title(section, "712.15", section_titles)

        assert result == "Drug testing"

    def test_should_fallback_to_section_titles(self):
        """Test fallback to section_titles dict."""
        ingestor = CFRPartIngestor(part=712)
        section = Element("SECTION")
        section_titles = {"712.11": "Purpose from API"}

        result = ingestor._extract_title(section, "712.11", section_titles)

        assert result == "Purpose from API"

    def test_should_return_empty_when_not_found(self):
        """Test returning empty string when title not found."""
        ingestor = CFRPartIngestor(part=712)
        section = Element("SECTION")
        section_titles = {}

        result = ingestor._extract_title(section, "712.99", section_titles)

        assert result == ""


# --- Extract Content Tests ---


class TestCFRPartIngestorExtractContent:
    """Tests for _extract_content method."""

    def test_should_extract_paragraph_content(self):
        """Test extracting content from P elements."""
        ingestor = CFRPartIngestor()
        section = Element("SECTION")
        p1 = SubElement(section, "P")
        p1.text = "First paragraph."
        p2 = SubElement(section, "P")
        p2.text = "Second paragraph."

        result = ingestor._extract_content(section)

        assert "First paragraph." in result
        assert "Second paragraph." in result

    def test_should_extract_fp_content(self):
        """Test extracting content from FP elements."""
        ingestor = CFRPartIngestor()
        section = Element("SECTION")
        fp = SubElement(section, "FP")
        fp.text = "Flush paragraph content."

        result = ingestor._extract_content(section)

        assert "Flush paragraph content." in result

    def test_should_join_with_double_newlines(self):
        """Test that paragraphs are joined with double newlines."""
        ingestor = CFRPartIngestor()
        section = Element("SECTION")
        p1 = SubElement(section, "P")
        p1.text = "Para 1"
        p2 = SubElement(section, "P")
        p2.text = "Para 2"

        result = ingestor._extract_content(section)

        assert result == "Para 1\n\nPara 2"

    def test_should_return_empty_for_no_content(self):
        """Test returning empty string when no content elements."""
        ingestor = CFRPartIngestor()
        section = Element("SECTION")
        SubElement(section, "HEAD").text = "Title"

        result = ingestor._extract_content(section)

        assert result == ""


# --- Find Sections Tests ---


class TestCFRPartIngestorFindSections:
    """Tests for _find_sections method."""

    def test_should_find_section_elements(self):
        """Test finding SECTION elements."""
        ingestor = CFRPartIngestor()
        root = Element("ROOT")
        SubElement(root, "SECTION")
        SubElement(root, "SECTION")

        sections = ingestor._find_sections(root)

        assert len(sections) == 2

    def test_should_find_div8_elements(self):
        """Test finding DIV8 elements (alternative section format)."""
        ingestor = CFRPartIngestor()
        root = Element("ROOT")
        SubElement(root, "DIV8")

        sections = ingestor._find_sections(root)

        assert len(sections) == 1

    def test_should_find_div9_elements(self):
        """Test finding DIV9 elements (alternative section format)."""
        ingestor = CFRPartIngestor()
        root = Element("ROOT")
        SubElement(root, "DIV9")

        sections = ingestor._find_sections(root)

        assert len(sections) == 1


# --- Extract Sections From Structure Tests ---


class TestCFRPartIngestorExtractSectionsFromStructure:
    """Tests for _extract_sections_from_structure method."""

    def test_should_extract_sections_from_part(self):
        """Test extracting sections from structure JSON."""
        ingestor = CFRPartIngestor(part=712)
        structure = {
            "identifier": "10",
            "children": [
                {
                    "identifier": "712",
                    "children": [
                        {
                            "type": "section",
                            "identifier": "712.1",
                            "label_description": "Purpose",
                        },
                        {
                            "type": "section",
                            "identifier": "712.3",
                            "label_description": "Definitions",
                        },
                    ],
                }
            ],
        }

        sections = ingestor._extract_sections_from_structure(structure)

        assert "712.1" in sections
        assert sections["712.1"] == "Purpose"
        assert "712.3" in sections
        assert sections["712.3"] == "Definitions"

    def test_should_return_empty_for_missing_part(self):
        """Test returning empty dict when part not found."""
        ingestor = CFRPartIngestor(part=712)
        structure = {
            "identifier": "10",
            "children": [{"identifier": "710", "children": []}],
        }

        sections = ingestor._extract_sections_from_structure(structure)

        assert sections == {}

    def test_should_skip_non_section_nodes(self):
        """Test that non-section nodes are skipped."""
        ingestor = CFRPartIngestor(part=712)
        structure = {
            "identifier": "712",
            "children": [
                {"type": "subpart", "identifier": "A"},
                {
                    "type": "section",
                    "identifier": "712.1",
                    "label_description": "Purpose",
                },
            ],
        }

        sections = ingestor._extract_sections_from_structure(structure)

        assert len(sections) == 1
        assert "712.1" in sections


# --- Parse Sections Regex Tests ---


class TestCFRPartIngestorParseSectionsRegex:
    """Tests for _parse_sections_regex fallback method."""

    def test_should_parse_section_with_regex(self):
        """Test regex parsing of sections."""
        ingestor = CFRPartIngestor(part=712)
        xml_content = """
        § 712.1 Purpose
        This part establishes the HRP requirements.

        § 712.3 Definitions
        The following definitions apply.
        """
        section_titles = {"712.1": "Purpose", "712.3": "Definitions"}

        sections = ingestor._parse_sections_regex(xml_content, section_titles)

        assert "712.1" in sections
        assert "712.3" in sections

    def test_should_skip_sections_not_in_titles(self):
        """Test that sections not in section_titles are skipped."""
        ingestor = CFRPartIngestor(part=712)
        xml_content = "§ 712.999 Unknown section"
        section_titles = {"712.1": "Purpose"}

        sections = ingestor._parse_sections_regex(xml_content, section_titles)

        assert "712.999" not in sections

    def test_should_clean_html_tags(self):
        """Test that HTML tags are removed from content."""
        ingestor = CFRPartIngestor(part=712)
        xml_content = """
        § 712.1 Purpose
        Content with <b>bold</b> and <i>italic</i> text.
        """
        section_titles = {"712.1": "Purpose"}

        sections = ingestor._parse_sections_regex(xml_content, section_titles)

        if "712.1" in sections:
            _, content = sections["712.1"]
            assert "<b>" not in content
            assert "<i>" not in content


# --- Source Type Property Tests ---


class TestCFRPartIngestorSourceType:
    """Tests for source_type property."""

    def test_should_return_correct_source_type_for_each_part(self):
        """Test that each part returns correct source type."""
        assert CFRPartIngestor(part=707).source_type == SourceType.CFR_707
        assert CFRPartIngestor(part=710).source_type == SourceType.CFR_710
        assert CFRPartIngestor(part=712).source_type == SourceType.CFR_712
