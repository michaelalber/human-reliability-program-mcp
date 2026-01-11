"""Pytest configuration and fixtures for HRP MCP tests."""


import pytest


@pytest.fixture(scope="session")
def embedding_service():
    """Get a shared embedding service for tests."""
    from hrp_mcp.services.embeddings import EmbeddingService

    return EmbeddingService(model_name="all-MiniLM-L6-v2")


@pytest.fixture
def temp_chroma_path(tmp_path):
    """Get a temporary directory for ChromaDB."""
    return str(tmp_path / "chroma")


@pytest.fixture
def temp_audit_log(tmp_path):
    """Get a temporary audit log path."""
    return str(tmp_path / "audit.jsonl")


@pytest.fixture
def vector_store(temp_chroma_path):
    """Get a test vector store."""
    from hrp_mcp.services.vector_store import VectorStoreService

    return VectorStoreService(db_path=temp_chroma_path)


@pytest.fixture
def rag_service(embedding_service, vector_store):
    """Get a test RAG service."""
    from hrp_mcp.services.rag import RagService

    return RagService(
        embedding_service=embedding_service,
        vector_store=vector_store,
    )


@pytest.fixture
def sample_hrp_chunk():
    """Get a sample HRP regulation chunk for testing."""
    from hrp_mcp.models.regulations import HRPSubpart, RegulationChunk

    return RegulationChunk(
        id="hrp:712-11:chunk-000",
        subpart=HRPSubpart.SUBPART_A,
        section="712.11",
        title="General requirements for HRP certification",
        content="Individuals in HRP positions must meet the following requirements: (a) Completion of initial and annual HRP instruction; (b) Successful completion of an initial and annual supervisory review, medical assessment, management evaluation, and a DOE personnel security review.",
        citation="10 CFR 712.11",
        chunk_index=0,
    )


@pytest.fixture
def populated_vector_store(vector_store, embedding_service, sample_hrp_chunk):
    """Get a vector store with sample data."""
    embedding = embedding_service.embed(sample_hrp_chunk.to_embedding_text())
    vector_store.add_chunk(sample_hrp_chunk, embedding)
    return vector_store
