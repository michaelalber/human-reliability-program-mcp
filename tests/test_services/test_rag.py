"""Tests for RAG service.

Tests cover semantic search, section retrieval, and chunk management.
"""

import pytest

from hrp_mcp.models.errors import SectionNotFoundError
from hrp_mcp.models.regulations import HRPSubpart, RegulationChunk, SourceType
from hrp_mcp.services.rag import RagService


# --- RagService Initialization Tests ---


class TestRagServiceInit:
    """Tests for RagService initialization."""

    def test_should_initialize_with_services(self, embedding_service, vector_store):
        """Test that RagService initializes with required services."""
        rag = RagService(
            embedding_service=embedding_service,
            vector_store=vector_store,
        )

        assert rag._embeddings is embedding_service
        assert rag._vector_store is vector_store


# --- Search Tests ---


class TestRagServiceSearch:
    """Tests for RagService search functionality."""

    @pytest.mark.asyncio
    async def test_should_return_empty_list_for_empty_store(self, rag_service):
        """Test search on empty store returns empty list."""
        results = await rag_service.search("certification requirements")

        assert isinstance(results, list)
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_should_find_matching_content(
        self, embedding_service, populated_vector_store
    ):
        """Test search finds matching content."""
        rag = RagService(
            embedding_service=embedding_service,
            vector_store=populated_vector_store,
        )

        results = await rag.search("HRP certification requirements")

        assert len(results) >= 1
        assert results[0].chunk.section == "712.11"

    @pytest.mark.asyncio
    async def test_should_return_results_with_scores(
        self, embedding_service, populated_vector_store
    ):
        """Test that search results include relevance scores."""
        rag = RagService(
            embedding_service=embedding_service,
            vector_store=populated_vector_store,
        )

        results = await rag.search("certification")

        if results:
            assert hasattr(results[0], "score")
            assert 0 <= results[0].score <= 1

    @pytest.mark.asyncio
    async def test_should_respect_limit_parameter(
        self, embedding_service, vector_store, sample_hrp_chunk
    ):
        """Test that limit parameter is respected."""
        # Add multiple chunks
        for i in range(5):
            chunk = RegulationChunk(
                id=f"test:chunk-{i}",
                source=SourceType.CFR_712,
                subpart=HRPSubpart.SUBPART_A,
                section="712.11",
                title="Test",
                content=f"Test content {i}",
                citation="10 CFR 712.11",
                chunk_index=i,
            )
            embedding = embedding_service.embed(chunk.to_embedding_text())
            vector_store.add_chunk(chunk, embedding)

        rag = RagService(embedding_service=embedding_service, vector_store=vector_store)
        results = await rag.search("test content", limit=2)

        assert len(results) <= 2


class TestRagServiceSearchSubparts:
    """Tests for subpart-specific search methods."""

    @pytest.mark.asyncio
    async def test_search_subpart_a(self, rag_service):
        """Test search_subpart_a method."""
        results = await rag_service.search_subpart_a("certification")

        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_search_subpart_b(self, rag_service):
        """Test search_subpart_b method."""
        results = await rag_service.search_subpart_b("medical standards")

        assert isinstance(results, list)


# --- Get Chunk Tests ---


class TestRagServiceGetChunk:
    """Tests for RagService get_chunk functionality."""

    @pytest.mark.asyncio
    async def test_should_raise_for_missing_chunk(self, rag_service):
        """Test that SectionNotFoundError is raised for missing chunk."""
        with pytest.raises(SectionNotFoundError):
            await rag_service.get_chunk("nonexistent-chunk-id")

    @pytest.mark.asyncio
    async def test_should_retrieve_existing_chunk(
        self, embedding_service, populated_vector_store, sample_hrp_chunk
    ):
        """Test retrieval of existing chunk."""
        rag = RagService(
            embedding_service=embedding_service,
            vector_store=populated_vector_store,
        )

        chunk = await rag.get_chunk(sample_hrp_chunk.id)

        assert chunk.id == sample_hrp_chunk.id
        assert chunk.section == sample_hrp_chunk.section


# --- Get Section Tests ---


class TestRagServiceGetSection:
    """Tests for RagService get_section functionality."""

    @pytest.mark.asyncio
    async def test_should_raise_for_missing_section(self, rag_service):
        """Test that SectionNotFoundError is raised for missing section."""
        with pytest.raises(SectionNotFoundError):
            await rag_service.get_section("712.999")

    @pytest.mark.asyncio
    async def test_should_retrieve_section_chunks(
        self, embedding_service, populated_vector_store
    ):
        """Test retrieval of section chunks."""
        rag = RagService(
            embedding_service=embedding_service,
            vector_store=populated_vector_store,
        )

        chunks = await rag.get_section("712.11")

        assert len(chunks) >= 1
        assert all(c.section == "712.11" for c in chunks)

    @pytest.mark.asyncio
    async def test_should_return_chunks_sorted_by_index(
        self, embedding_service, vector_store
    ):
        """Test that chunks are returned sorted by chunk_index."""
        # Add chunks out of order
        for i in [2, 0, 1]:
            chunk = RegulationChunk(
                id=f"test:712-15:chunk-{i:03d}",
                source=SourceType.CFR_712,
                subpart=HRPSubpart.SUBPART_A,
                section="712.15",
                title="Drug testing",
                content=f"Content part {i}",
                citation="10 CFR 712.15",
                chunk_index=i,
            )
            embedding = embedding_service.embed(chunk.to_embedding_text())
            vector_store.add_chunk(chunk, embedding)

        rag = RagService(embedding_service=embedding_service, vector_store=vector_store)
        chunks = await rag.get_section("712.15")

        assert len(chunks) == 3
        assert [c.chunk_index for c in chunks] == [0, 1, 2]


# --- Store Count Tests ---


class TestRagServiceStoreCount:
    """Tests for RagService store count functionality."""

    def test_should_return_zero_for_empty_store(self, rag_service):
        """Test count on empty store."""
        count = rag_service.get_store_count()
        assert count == 0

    def test_should_return_correct_count(
        self, embedding_service, populated_vector_store
    ):
        """Test count after adding chunks."""
        rag = RagService(
            embedding_service=embedding_service,
            vector_store=populated_vector_store,
        )

        count = rag.get_store_count()
        assert count >= 1

    def test_should_filter_count_by_subpart(
        self, embedding_service, vector_store
    ):
        """Test count filtering by subpart."""
        # Add chunks from different subparts
        chunk_a = RegulationChunk(
            id="test:712-11:chunk-000",
            source=SourceType.CFR_712,
            subpart=HRPSubpart.SUBPART_A,
            section="712.11",
            title="Test A",
            content="Subpart A content",
            citation="10 CFR 712.11",
            chunk_index=0,
        )
        chunk_b = RegulationChunk(
            id="test:712-30:chunk-000",
            source=SourceType.CFR_712,
            subpart=HRPSubpart.SUBPART_B,
            section="712.30",
            title="Test B",
            content="Subpart B content",
            citation="10 CFR 712.30",
            chunk_index=0,
        )

        vector_store.add_chunk(chunk_a, embedding_service.embed(chunk_a.to_embedding_text()))
        vector_store.add_chunk(chunk_b, embedding_service.embed(chunk_b.to_embedding_text()))

        rag = RagService(embedding_service=embedding_service, vector_store=vector_store)

        total = rag.get_store_count()
        subpart_a = rag.get_store_count(subpart=HRPSubpart.SUBPART_A)
        subpart_b = rag.get_store_count(subpart=HRPSubpart.SUBPART_B)

        assert total == 2
        assert subpart_a == 1
        assert subpart_b == 1
