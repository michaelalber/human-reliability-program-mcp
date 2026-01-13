"""Tests for document chunking functionality.

Tests cover token counting, text chunking, and overlap handling.
"""

from hrp_mcp.models.regulations import SourceType
from hrp_mcp.rag.chunking import ChunkMetadata, RegulationChunker


# --- ChunkMetadata Tests ---


class TestChunkMetadata:
    """Tests for ChunkMetadata dataclass."""

    def test_should_create_with_required_fields(self):
        """Test creation with only required fields."""
        metadata = ChunkMetadata(section="712.11")

        assert metadata.section == "712.11"
        assert metadata.title == ""
        assert metadata.citation == ""
        assert metadata.source == SourceType.CFR_712

    def test_should_create_with_all_fields(self):
        """Test creation with all fields."""
        metadata = ChunkMetadata(
            section="712.15",
            title="Drug testing",
            citation="10 CFR 712.15",
            source=SourceType.CFR_710,
        )

        assert metadata.section == "712.15"
        assert metadata.title == "Drug testing"
        assert metadata.citation == "10 CFR 712.15"
        assert metadata.source == SourceType.CFR_710


# --- RegulationChunker Initialization Tests ---


class TestRegulationChunkerInit:
    """Tests for RegulationChunker initialization."""

    def test_should_initialize_with_defaults(self):
        """Test initialization with default parameters."""
        chunker = RegulationChunker()

        assert chunker.max_tokens == 512
        assert chunker.overlap_tokens == 50

    def test_should_initialize_with_custom_params(self):
        """Test initialization with custom parameters."""
        chunker = RegulationChunker(max_tokens=256, overlap_tokens=25)

        assert chunker.max_tokens == 256
        assert chunker.overlap_tokens == 25


# --- Token Counting Tests ---


class TestRegulationChunkerTokenCounting:
    """Tests for token counting functionality."""

    def test_should_count_tokens_in_text(self):
        """Test basic token counting."""
        chunker = RegulationChunker()

        count = chunker.count_tokens("Hello world")
        assert count > 0
        assert isinstance(count, int)

    def test_should_count_tokens_in_empty_string(self):
        """Test token counting for empty string."""
        chunker = RegulationChunker()

        count = chunker.count_tokens("")
        assert count == 0

    def test_should_count_tokens_consistently(self):
        """Test that same text produces same count."""
        chunker = RegulationChunker()
        text = "The HRP certification process requires multiple evaluations."

        count1 = chunker.count_tokens(text)
        count2 = chunker.count_tokens(text)

        assert count1 == count2


# --- Chunk Text Tests ---


class TestRegulationChunkerChunkText:
    """Tests for text chunking functionality."""

    def test_should_return_single_chunk_for_short_text(self):
        """Test that short text returns single chunk."""
        chunker = RegulationChunker(max_tokens=512)
        metadata = ChunkMetadata(
            section="712.11",
            title="General requirements",
            citation="10 CFR 712.11",
        )

        chunks = chunker.chunk_text("Short regulation text.", metadata)

        assert len(chunks) == 1
        assert chunks[0].content == "Short regulation text."
        assert chunks[0].section == "712.11"
        assert chunks[0].chunk_index == 0

    def test_should_split_long_text_into_multiple_chunks(self):
        """Test that long text is split into multiple chunks."""
        chunker = RegulationChunker(max_tokens=50, overlap_tokens=10)
        metadata = ChunkMetadata(
            section="712.11",
            title="General requirements",
            citation="10 CFR 712.11",
        )

        # Create text that will need multiple chunks
        long_text = " ".join(["This is test content for chunking."] * 20)
        chunks = chunker.chunk_text(long_text, metadata)

        assert len(chunks) > 1

    def test_should_preserve_section_metadata(self):
        """Test that all chunks preserve section metadata."""
        chunker = RegulationChunker(max_tokens=50, overlap_tokens=10)
        metadata = ChunkMetadata(
            section="712.15",
            title="Drug testing",
            citation="10 CFR 712.15",
        )

        long_text = " ".join(["Test content."] * 30)
        chunks = chunker.chunk_text(long_text, metadata)

        for chunk in chunks:
            assert chunk.section == "712.15"
            assert chunk.title == "Drug testing"
            assert chunk.citation == "10 CFR 712.15"

    def test_should_assign_sequential_chunk_indices(self):
        """Test that chunks have sequential indices."""
        chunker = RegulationChunker(max_tokens=50, overlap_tokens=10)
        metadata = ChunkMetadata(section="712.11")

        long_text = " ".join(["Test content for sequential indices."] * 20)
        chunks = chunker.chunk_text(long_text, metadata)

        indices = [c.chunk_index for c in chunks]
        assert indices == list(range(len(chunks)))

    def test_should_generate_unique_chunk_ids(self):
        """Test that each chunk has a unique ID."""
        chunker = RegulationChunker(max_tokens=50, overlap_tokens=10)
        metadata = ChunkMetadata(section="712.11")

        long_text = " ".join(["Test content."] * 30)
        chunks = chunker.chunk_text(long_text, metadata)

        ids = [c.id for c in chunks]
        assert len(ids) == len(set(ids))  # All unique

    def test_should_set_subpart_for_cfr_712(self):
        """Test that subpart is set correctly for 10 CFR 712."""
        chunker = RegulationChunker()

        # Subpart A section
        metadata_a = ChunkMetadata(section="712.11", source=SourceType.CFR_712)
        chunks_a = chunker.chunk_text("Test content.", metadata_a)
        assert chunks_a[0].subpart is not None

        # Subpart B section
        metadata_b = ChunkMetadata(section="712.30", source=SourceType.CFR_712)
        chunks_b = chunker.chunk_text("Test content.", metadata_b)
        assert chunks_b[0].subpart is not None

    def test_should_not_set_subpart_for_other_sources(self):
        """Test that subpart is not set for non-712 sources."""
        chunker = RegulationChunker()
        metadata = ChunkMetadata(section="710.1", source=SourceType.CFR_710)

        chunks = chunker.chunk_text("Test content.", metadata)

        assert chunks[0].subpart is None


# --- Paragraph Splitting Tests ---


class TestRegulationChunkerParagraphSplitting:
    """Tests for paragraph-based splitting."""

    def test_should_split_on_double_newlines(self):
        """Test splitting on paragraph boundaries."""
        chunker = RegulationChunker()

        text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
        paragraphs = chunker._split_paragraphs(text)

        assert len(paragraphs) == 3
        assert paragraphs[0] == "First paragraph."
        assert paragraphs[1] == "Second paragraph."
        assert paragraphs[2] == "Third paragraph."

    def test_should_handle_empty_paragraphs(self):
        """Test handling of empty paragraphs."""
        chunker = RegulationChunker()

        text = "Content.\n\n\n\nMore content."
        paragraphs = chunker._split_paragraphs(text)

        assert len(paragraphs) == 2

    def test_should_preserve_single_newlines(self):
        """Test that single newlines are preserved within paragraphs."""
        chunker = RegulationChunker()

        text = "Line one.\nLine two.\n\nNew paragraph."
        paragraphs = chunker._split_paragraphs(text)

        assert len(paragraphs) == 2
        assert "Line one.\nLine two." in paragraphs[0]


# --- Overlap Handling Tests ---


class TestRegulationChunkerOverlap:
    """Tests for overlap handling between chunks."""

    def test_should_get_overlap_text(self):
        """Test extraction of overlap text."""
        chunker = RegulationChunker(overlap_tokens=5)

        text = "This is a sample text for testing overlap extraction."
        overlap = chunker._get_overlap_text(text)

        # Should be shorter than original
        assert len(overlap) < len(text)

    def test_should_return_full_text_if_shorter_than_overlap(self):
        """Test that short text is returned in full."""
        chunker = RegulationChunker(overlap_tokens=100)

        text = "Short text."
        overlap = chunker._get_overlap_text(text)

        assert overlap == text


# --- Chunk ID Generation Tests ---


class TestRegulationChunkerChunkId:
    """Tests for chunk ID generation."""

    def test_should_generate_id_with_source_prefix(self):
        """Test that ID includes source prefix."""
        chunker = RegulationChunker()

        chunk_id = chunker._make_chunk_id("712.11", SourceType.CFR_712, 0)

        assert "10cfr712" in chunk_id

    def test_should_include_section_in_id(self):
        """Test that ID includes normalized section."""
        chunker = RegulationChunker()

        chunk_id = chunker._make_chunk_id("712.15", SourceType.CFR_712, 0)

        assert "712-15" in chunk_id

    def test_should_include_chunk_index_in_id(self):
        """Test that ID includes chunk index."""
        chunker = RegulationChunker()

        chunk_id_0 = chunker._make_chunk_id("712.11", SourceType.CFR_712, 0)
        chunk_id_5 = chunker._make_chunk_id("712.11", SourceType.CFR_712, 5)

        assert "chunk-000" in chunk_id_0
        assert "chunk-005" in chunk_id_5

    def test_should_generate_different_ids_for_different_sources(self):
        """Test that different sources produce different IDs."""
        chunker = RegulationChunker()

        id_712 = chunker._make_chunk_id("712.11", SourceType.CFR_712, 0)
        id_710 = chunker._make_chunk_id("710.11", SourceType.CFR_710, 0)

        assert id_712 != id_710


# --- Edge Cases ---


class TestRegulationChunkerEdgeCases:
    """Edge case tests for RegulationChunker."""

    def test_should_handle_empty_text(self):
        """Test handling of empty text."""
        chunker = RegulationChunker()
        metadata = ChunkMetadata(section="712.11")

        chunks = chunker.chunk_text("", metadata)

        assert len(chunks) == 1
        assert chunks[0].content == ""

    def test_should_handle_whitespace_only_text(self):
        """Test handling of whitespace-only text."""
        chunker = RegulationChunker()
        metadata = ChunkMetadata(section="712.11")

        chunks = chunker.chunk_text("   \n\n   ", metadata)

        assert len(chunks) == 1

    def test_should_handle_very_long_single_paragraph(self):
        """Test handling of very long paragraph with sentences."""
        chunker = RegulationChunker(max_tokens=50, overlap_tokens=10)
        metadata = ChunkMetadata(section="712.11")

        # Create a long paragraph with sentence boundaries for proper splitting
        sentences = [f"This is certification requirement number {i}." for i in range(50)]
        long_para = " ".join(sentences)
        chunks = chunker.chunk_text(long_para, metadata)

        # Should split into multiple chunks due to sentence-based splitting
        assert len(chunks) > 1
