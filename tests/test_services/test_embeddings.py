"""Tests for embedding service."""



def test_embedding_service_creates_embeddings(embedding_service):
    """Test that embedding service creates embeddings."""
    text = "Human Reliability Program certification requirements"
    embedding = embedding_service.embed(text)

    assert embedding is not None
    assert len(embedding) > 0
    assert isinstance(embedding[0], float)


def test_embedding_service_batch(embedding_service):
    """Test batch embedding."""
    texts = [
        "HRP certification",
        "Medical evaluation",
        "Drug testing requirements",
    ]
    embeddings = embedding_service.embed_batch(texts)

    assert len(embeddings) == 3
    for emb in embeddings:
        assert len(emb) > 0


def test_embedding_service_consistency(embedding_service):
    """Test that same text produces same embedding."""
    text = "DOE personnel security review"
    emb1 = embedding_service.embed(text)
    emb2 = embedding_service.embed(text)

    assert emb1 == emb2
