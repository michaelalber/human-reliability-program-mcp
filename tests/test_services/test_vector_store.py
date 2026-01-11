"""Tests for vector store service."""


from hrp_mcp.models.regulations import HRPSubpart


def test_vector_store_add_chunk(vector_store, embedding_service, sample_hrp_chunk):
    """Test adding a chunk to the vector store."""
    embedding = embedding_service.embed(sample_hrp_chunk.to_embedding_text())
    vector_store.add_chunk(sample_hrp_chunk, embedding)

    assert vector_store.count() == 1


def test_vector_store_search(populated_vector_store, embedding_service):
    """Test searching the vector store."""
    query = "HRP certification requirements"
    query_embedding = embedding_service.embed(query)

    # search returns list of (metadata, score) tuples
    results = populated_vector_store.search(query_embedding, limit=5)

    assert len(results) > 0
    metadata, score = results[0]
    assert metadata["section"] == "712.11"
    assert 0 <= score <= 1


def test_vector_store_get_by_section(populated_vector_store):
    """Test getting chunks by section number."""
    # get_by_section returns list of metadata dicts
    chunks = populated_vector_store.get_by_section("712.11")

    assert len(chunks) > 0
    assert chunks[0]["section"] == "712.11"


def test_vector_store_subpart_filter(vector_store, embedding_service, sample_hrp_chunk):
    """Test filtering by subpart."""
    embedding = embedding_service.embed(sample_hrp_chunk.to_embedding_text())
    vector_store.add_chunk(sample_hrp_chunk, embedding)

    query_embedding = embedding_service.embed("certification")

    # Filter for Subpart A (should find)
    results_a = vector_store.search(query_embedding, subpart=HRPSubpart.SUBPART_A, limit=5)
    assert len(results_a) > 0

    # Filter for Subpart B (should not find)
    results_b = vector_store.search(query_embedding, subpart=HRPSubpart.SUBPART_B, limit=5)
    assert len(results_b) == 0


def test_vector_store_delete_all(populated_vector_store):
    """Test deleting all chunks."""
    assert populated_vector_store.count() > 0
    populated_vector_store.delete_all()
    assert populated_vector_store.count() == 0


def test_vector_store_get_by_id(populated_vector_store):
    """Test getting a chunk by its ID."""
    result = populated_vector_store.get_by_id("hrp:712-11:chunk-000")
    assert result is not None
    assert result["section"] == "712.11"


def test_vector_store_get_by_id_not_found(vector_store):
    """Test getting a non-existent chunk returns None."""
    result = vector_store.get_by_id("nonexistent-id")
    assert result is None
