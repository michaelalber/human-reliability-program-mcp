"""Tests for handbook ingestion business logic.

Tests cover HTML parsing, section parsing, and section ID generation.
"""

from bs4 import BeautifulSoup

from hrp_mcp.data.ingest.handbook_ingest import HandbookIngestor

# --- Initialization Tests ---


class TestHandbookIngestorInit:
    """Tests for HandbookIngestor initialization."""

    def test_should_initialize_with_default_batch_size(self):
        """Test default initialization."""
        ingestor = HandbookIngestor()

        assert ingestor.batch_size == 50

    def test_should_initialize_with_custom_batch_size(self):
        """Test initialization with custom batch size."""
        ingestor = HandbookIngestor(batch_size=100)

        assert ingestor.batch_size == 100


# --- Find Main Content Tests ---


class TestHandbookIngestorFindMainContent:
    """Tests for _find_main_content method."""

    def test_should_find_main_element(self):
        """Test finding main element."""
        ingestor = HandbookIngestor()
        soup = BeautifulSoup("<html><main><p>Content</p></main></html>", "html.parser")

        result = ingestor._find_main_content(soup)

        assert result is not None
        assert result.name == "main"

    def test_should_find_article_when_no_main(self):
        """Test falling back to article element."""
        ingestor = HandbookIngestor()
        soup = BeautifulSoup("<html><article><p>Content</p></article></html>", "html.parser")

        result = ingestor._find_main_content(soup)

        assert result is not None
        assert result.name == "article"

    def test_should_find_body_when_no_main_or_article(self):
        """Test falling back to body element."""
        ingestor = HandbookIngestor()
        soup = BeautifulSoup("<html><body><p>Content</p></body></html>", "html.parser")

        result = ingestor._find_main_content(soup)

        assert result is not None
        assert result.name == "body"

    def test_should_return_none_when_no_content(self):
        """Test returning None for empty document."""
        ingestor = HandbookIngestor()
        soup = BeautifulSoup("", "html.parser")

        result = ingestor._find_main_content(soup)

        assert result is None

    def test_should_prefer_main_over_article(self):
        """Test that main is preferred over article."""
        ingestor = HandbookIngestor()
        html = "<html><body><article>Article</article><main>Main</main></body></html>"
        soup = BeautifulSoup(html, "html.parser")

        result = ingestor._find_main_content(soup)

        assert result.name == "main"


# --- Format Heading Tests ---


class TestHandbookIngestorFormatHeading:
    """Tests for _format_heading method."""

    def test_should_format_h1(self):
        """Test formatting h1 heading."""
        ingestor = HandbookIngestor()
        soup = BeautifulSoup("<h1>Main Title</h1>", "html.parser")
        element = soup.find("h1")

        result = ingestor._format_heading(element)

        assert result == "\n# Main Title\n"

    def test_should_format_h2(self):
        """Test formatting h2 heading."""
        ingestor = HandbookIngestor()
        soup = BeautifulSoup("<h2>Section Title</h2>", "html.parser")
        element = soup.find("h2")

        result = ingestor._format_heading(element)

        assert result == "\n## Section Title\n"

    def test_should_format_h3(self):
        """Test formatting h3 heading."""
        ingestor = HandbookIngestor()
        soup = BeautifulSoup("<h3>Subsection</h3>", "html.parser")
        element = soup.find("h3")

        result = ingestor._format_heading(element)

        assert result == "\n### Subsection\n"

    def test_should_format_h4(self):
        """Test formatting h4 heading."""
        ingestor = HandbookIngestor()
        soup = BeautifulSoup("<h4>Minor heading</h4>", "html.parser")
        element = soup.find("h4")

        result = ingestor._format_heading(element)

        assert result == "\n#### Minor heading\n"

    def test_should_return_none_for_empty_heading(self):
        """Test returning None for empty heading."""
        ingestor = HandbookIngestor()
        soup = BeautifulSoup("<h1>   </h1>", "html.parser")
        element = soup.find("h1")

        result = ingestor._format_heading(element)

        assert result is None


# --- Format Paragraph Tests ---


class TestHandbookIngestorFormatParagraph:
    """Tests for _format_paragraph method."""

    def test_should_format_paragraph(self):
        """Test formatting paragraph."""
        ingestor = HandbookIngestor()
        soup = BeautifulSoup("<p>This is a paragraph.</p>", "html.parser")
        element = soup.find("p")

        result = ingestor._format_paragraph(element)

        assert result == "\nThis is a paragraph.\n"

    def test_should_strip_whitespace(self):
        """Test that whitespace is stripped."""
        ingestor = HandbookIngestor()
        soup = BeautifulSoup("<p>  Text with spaces  </p>", "html.parser")
        element = soup.find("p")

        result = ingestor._format_paragraph(element)

        assert result == "\nText with spaces\n"

    def test_should_return_none_for_empty_paragraph(self):
        """Test returning None for empty paragraph."""
        ingestor = HandbookIngestor()
        soup = BeautifulSoup("<p>   </p>", "html.parser")
        element = soup.find("p")

        result = ingestor._format_paragraph(element)

        assert result is None


# --- Format List Item Tests ---


class TestHandbookIngestorFormatListItem:
    """Tests for _format_list_item method."""

    def test_should_format_list_item(self):
        """Test formatting list item."""
        ingestor = HandbookIngestor()
        soup = BeautifulSoup("<li>Item text</li>", "html.parser")
        element = soup.find("li")

        result = ingestor._format_list_item(element)

        assert result == "- Item text"

    def test_should_return_none_for_empty_item(self):
        """Test returning None for empty item."""
        ingestor = HandbookIngestor()
        soup = BeautifulSoup("<li></li>", "html.parser")
        element = soup.find("li")

        result = ingestor._format_list_item(element)

        assert result is None


# --- Format Element Tests ---


class TestHandbookIngestorFormatElement:
    """Tests for _format_element method."""

    def test_should_route_heading_to_format_heading(self):
        """Test routing heading elements."""
        ingestor = HandbookIngestor()
        soup = BeautifulSoup("<h2>Title</h2>", "html.parser")
        element = soup.find("h2")

        result = ingestor._format_element(element)

        assert result == "\n## Title\n"

    def test_should_route_paragraph_to_format_paragraph(self):
        """Test routing paragraph elements."""
        ingestor = HandbookIngestor()
        soup = BeautifulSoup("<p>Content</p>", "html.parser")
        element = soup.find("p")

        result = ingestor._format_element(element)

        assert result == "\nContent\n"

    def test_should_route_list_item_to_format_list_item(self):
        """Test routing list item elements."""
        ingestor = HandbookIngestor()
        soup = BeautifulSoup("<li>Item</li>", "html.parser")
        element = soup.find("li")

        result = ingestor._format_element(element)

        assert result == "- Item"

    def test_should_return_none_for_unknown_element(self):
        """Test returning None for unknown elements."""
        ingestor = HandbookIngestor()
        soup = BeautifulSoup("<div>Content</div>", "html.parser")
        element = soup.find("div")

        result = ingestor._format_element(element)

        assert result is None


# --- Parse HTML Tests ---


class TestHandbookIngestorParseHtml:
    """Tests for _parse_html method."""

    def test_should_parse_simple_html(self):
        """Test parsing simple HTML document."""
        ingestor = HandbookIngestor()
        html = """
        <html>
        <body>
            <h1>Title</h1>
            <p>First paragraph.</p>
            <p>Second paragraph.</p>
        </body>
        </html>
        """

        result = ingestor._parse_html(html)

        assert "# Title" in result
        assert "First paragraph." in result
        assert "Second paragraph." in result

    def test_should_parse_nested_structure(self):
        """Test parsing nested HTML structure."""
        ingestor = HandbookIngestor()
        html = """
        <html>
        <main>
            <h1>Main Title</h1>
            <h2>Section 1</h2>
            <p>Content 1.</p>
            <h2>Section 2</h2>
            <p>Content 2.</p>
        </main>
        </html>
        """

        result = ingestor._parse_html(html)

        assert "# Main Title" in result
        assert "## Section 1" in result
        assert "## Section 2" in result

    def test_should_parse_lists(self):
        """Test parsing HTML lists."""
        ingestor = HandbookIngestor()
        html = """
        <html>
        <body>
            <ul>
                <li>Item 1</li>
                <li>Item 2</li>
            </ul>
        </body>
        </html>
        """

        result = ingestor._parse_html(html)

        assert "- Item 1" in result
        assert "- Item 2" in result

    def test_should_return_empty_for_no_content(self):
        """Test returning empty string for document with no main content."""
        ingestor = HandbookIngestor()
        html = ""

        result = ingestor._parse_html(html)

        assert result == ""


# --- Parse Handbook Sections Tests ---


class TestHandbookIngestorParseHandbookSections:
    """Tests for _parse_handbook_sections method."""

    def test_should_parse_single_section(self):
        """Test parsing content with single section."""
        ingestor = HandbookIngestor()
        content = """# Introduction

This is the introduction content.
It has multiple lines.
"""

        sections = ingestor._parse_handbook_sections(content)

        assert len(sections) == 1
        section_id = next(iter(sections.keys()))
        title, text = sections[section_id]
        assert title == "Introduction"
        assert "introduction content" in text

    def test_should_parse_multiple_sections(self):
        """Test parsing content with multiple sections."""
        ingestor = HandbookIngestor()
        content = """# First Section

First content.

## Second Section

Second content.

## Third Section

Third content.
"""

        sections = ingestor._parse_handbook_sections(content)

        assert len(sections) == 3

    def test_should_handle_intro_content_before_first_header(self):
        """Test handling content before first header."""
        ingestor = HandbookIngestor()
        content = """Some intro text before any header.

# First Real Section

Section content.
"""

        sections = ingestor._parse_handbook_sections(content)

        # Should have intro section and first real section
        assert len(sections) == 2
        # Check intro section exists
        intro_found = any("intro" in sid for sid in sections)
        assert intro_found

    def test_should_handle_empty_sections(self):
        """Test that empty sections are not included."""
        ingestor = HandbookIngestor()
        content = """# Header Only

# Another Header

Some content here.
"""

        sections = ingestor._parse_handbook_sections(content)

        # Only section with content should be included
        assert len(sections) == 1

    def test_should_handle_different_header_levels(self):
        """Test parsing different header levels."""
        ingestor = HandbookIngestor()
        content = """# H1 Title

H1 content.

## H2 Title

H2 content.

### H3 Title

H3 content.

#### H4 Title

H4 content.
"""

        sections = ingestor._parse_handbook_sections(content)

        assert len(sections) == 4

    def test_should_preserve_content_with_newlines(self):
        """Test that content newlines are preserved."""
        ingestor = HandbookIngestor()
        content = """# Section

Line 1.

Line 2.

Line 3.
"""

        sections = ingestor._parse_handbook_sections(content)

        section_id = next(iter(sections.keys()))
        _, text = sections[section_id]
        assert "Line 1." in text
        assert "Line 2." in text
        assert "Line 3." in text

    def test_should_handle_empty_content(self):
        """Test handling empty content."""
        ingestor = HandbookIngestor()
        content = ""

        sections = ingestor._parse_handbook_sections(content)

        assert len(sections) == 0

    def test_should_handle_whitespace_only_content(self):
        """Test handling whitespace-only content."""
        ingestor = HandbookIngestor()
        content = "   \n\n   \n"

        sections = ingestor._parse_handbook_sections(content)

        assert len(sections) == 0

    def test_should_capture_last_section(self):
        """Test that the last section is captured."""
        ingestor = HandbookIngestor()
        content = """# First

First content.

# Last

Last content here.
"""

        sections = ingestor._parse_handbook_sections(content)

        assert len(sections) == 2
        # Verify last section has content
        last_section = list(sections.values())[-1]
        assert "Last content" in last_section[1]


# --- Generate Section ID Tests ---


class TestHandbookIngestorGenerateSectionId:
    """Tests for _generate_section_id method."""

    def test_should_generate_basic_id(self):
        """Test generating basic section ID."""
        ingestor = HandbookIngestor()

        result = ingestor._generate_section_id("Introduction", 1)

        assert result == "handbook:introduction:001"

    def test_should_lowercase_title(self):
        """Test that title is lowercased."""
        ingestor = HandbookIngestor()

        result = ingestor._generate_section_id("UPPERCASE TITLE", 1)

        assert "uppercase_title" in result

    def test_should_replace_spaces_with_underscores(self):
        """Test that spaces become underscores."""
        ingestor = HandbookIngestor()

        result = ingestor._generate_section_id("Multiple Word Title", 1)

        assert "multiple_word_title" in result

    def test_should_remove_special_characters(self):
        """Test that special characters are removed."""
        ingestor = HandbookIngestor()

        result = ingestor._generate_section_id("What's the HRP?", 1)

        assert "?" not in result
        assert "'" not in result
        assert "whats_the_hrp" in result

    def test_should_truncate_long_titles(self):
        """Test that long titles are truncated."""
        ingestor = HandbookIngestor()
        long_title = "This is a very long title that exceeds thirty characters"

        result = ingestor._generate_section_id(long_title, 1)

        # ID should have handbook: prefix, truncated title (30 chars max), and counter
        parts = result.split(":")
        assert len(parts[1]) <= 30

    def test_should_include_counter(self):
        """Test that counter is included and zero-padded."""
        ingestor = HandbookIngestor()

        result1 = ingestor._generate_section_id("Title", 1)
        result5 = ingestor._generate_section_id("Title", 5)
        result99 = ingestor._generate_section_id("Title", 99)

        assert result1.endswith(":001")
        assert result5.endswith(":005")
        assert result99.endswith(":099")

    def test_should_handle_numeric_titles(self):
        """Test handling titles with numbers."""
        ingestor = HandbookIngestor()

        result = ingestor._generate_section_id("Section 712.11", 1)

        assert "section_71211" in result

    def test_should_handle_empty_title(self):
        """Test handling empty title."""
        ingestor = HandbookIngestor()

        result = ingestor._generate_section_id("", 1)

        assert result == "handbook::001"

    def test_should_collapse_multiple_spaces(self):
        """Test that multiple spaces collapse to single underscore."""
        ingestor = HandbookIngestor()

        result = ingestor._generate_section_id("Title   With   Spaces", 1)

        assert "title_with_spaces" in result
        assert "__" not in result
