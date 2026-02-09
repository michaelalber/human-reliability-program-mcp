"""Vector store service using ChromaDB."""

from typing import Any

import chromadb
from chromadb import Collection
from chromadb.api import ClientAPI

from hrp_mcp.models.errors import VectorStoreError
from hrp_mcp.models.regulations import HRPSubpart, RegulationChunk, SourceType


class VectorStoreService:
    """ChromaDB wrapper for HRP regulation storage and retrieval."""

    # Single collection for 10 CFR 712
    HRP_COLLECTION = "hrp_regulations"

    def __init__(self, db_path: str):
        """
        Initialize ChromaDB in persistent mode.

        Args:
            db_path: Path to the ChromaDB storage directory.
        """
        self._db_path = db_path
        self._client: ClientAPI | None = None
        self._collection: Collection | None = None

    @property
    def client(self) -> ClientAPI:
        """Lazy-load and return the ChromaDB client."""
        if self._client is None:
            try:
                self._client = chromadb.PersistentClient(path=self._db_path)
            except Exception as e:
                raise VectorStoreError(
                    f"Failed to initialize ChromaDB at '{self._db_path}': {e}"
                ) from e
        return self._client

    @property
    def collection(self) -> Collection:
        """Get or create the HRP regulations collection."""
        if self._collection is None:
            try:
                self._collection = self.client.get_or_create_collection(
                    name=self.HRP_COLLECTION,
                    metadata={"hnsw:space": "cosine"},
                )
            except Exception as e:
                raise VectorStoreError(
                    f"Failed to access collection '{self.HRP_COLLECTION}': {e}"
                ) from e
        return self._collection

    def add_chunk(self, chunk: RegulationChunk, embedding: list[float]) -> None:
        """
        Add a single regulation chunk with its embedding.

        Args:
            chunk: The regulation chunk to store.
            embedding: Pre-computed embedding vector.

        Raises:
            VectorStoreError: If the operation fails.
        """
        try:
            metadata = {
                "source": chunk.source.value,
                "section": chunk.section,
                "title": chunk.title,
                "citation": chunk.citation,
                "chunk_index": chunk.chunk_index,
                "full_json": chunk.model_dump_json(),
            }
            if chunk.subpart:
                metadata["subpart"] = chunk.subpart.value

            self.collection.add(
                ids=[chunk.id],
                embeddings=[embedding],
                documents=[chunk.content],
                metadatas=[metadata],
            )
        except Exception as e:
            raise VectorStoreError(f"Failed to add chunk '{chunk.id}': {e}") from e

    def add_chunks_batch(
        self,
        chunks: list[RegulationChunk],
        embeddings: list[list[float]],
    ) -> None:
        """
        Add multiple regulation chunks efficiently.

        Args:
            chunks: List of chunks to store.
            embeddings: Corresponding embedding vectors.

        Raises:
            VectorStoreError: If the operation fails.
            ValueError: If chunks and embeddings lengths don't match.
        """
        if len(chunks) != len(embeddings):
            raise ValueError(
                f"Chunks ({len(chunks)}) and embeddings ({len(embeddings)}) must have same length"
            )

        if not chunks:
            return

        try:
            metadatas = []
            for c in chunks:
                meta = {
                    "source": c.source.value,
                    "section": c.section,
                    "title": c.title,
                    "citation": c.citation,
                    "chunk_index": c.chunk_index,
                    "full_json": c.model_dump_json(),
                }
                if c.subpart:
                    meta["subpart"] = c.subpart.value
                metadatas.append(meta)

            self.collection.add(
                ids=[c.id for c in chunks],
                embeddings=embeddings,
                documents=[c.content for c in chunks],
                metadatas=metadatas,
            )
        except Exception as e:
            raise VectorStoreError(f"Failed to add batch of {len(chunks)} chunks: {e}") from e

    def search(
        self,
        query_embedding: list[float],
        source: SourceType | None = None,
        subpart: HRPSubpart | None = None,
        section: str | None = None,
        limit: int = 10,
    ) -> list[tuple[dict[str, Any], float]]:
        """
        Search for similar regulation chunks.

        Args:
            query_embedding: Query vector.
            source: Optional source filter (10cfr712, 10cfr710, etc.).
            subpart: Optional subpart filter (A or B) - for 712 only.
            section: Optional section filter (e.g., "712.11").
            limit: Maximum number of results.

        Returns:
            List of (metadata, score) tuples, where score is similarity (0-1).

        Raises:
            VectorStoreError: If the search fails.
        """
        try:
            # Build where clause
            conditions = []
            if source:
                conditions.append({"source": source.value})
            if subpart:
                conditions.append({"subpart": subpart.value})
            if section:
                conditions.append({"section": section})

            where: dict[str, Any] | None = None
            if len(conditions) == 1:
                where = conditions[0]
            elif len(conditions) > 1:
                where = {"$and": conditions}

            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where,
                include=["metadatas", "distances"],
            )

            all_results: list[tuple[dict[str, Any], float]] = []
            if results["metadatas"] and results["distances"]:
                for metadata, distance in zip(
                    results["metadatas"][0],
                    results["distances"][0],
                    strict=True,
                ):
                    # Cosine distance to similarity: similarity = 1 - distance
                    similarity = max(0.0, 1.0 - distance)
                    all_results.append((metadata, similarity))

            return all_results

        except Exception as e:
            raise VectorStoreError(f"Search failed: {e}") from e

    def get_by_id(self, chunk_id: str) -> dict[str, Any] | None:
        """
        Get a chunk by exact ID match.

        Args:
            chunk_id: Chunk identifier.

        Returns:
            Chunk metadata dict or None if not found.

        Raises:
            VectorStoreError: If the operation fails.
        """
        try:
            results = self.collection.get(
                ids=[chunk_id],
                include=["metadatas"],
            )
            if results["metadatas"]:
                return results["metadatas"][0]
            return None

        except Exception as e:
            raise VectorStoreError(f"Failed to get chunk '{chunk_id}': {e}") from e

    def get_by_section(self, section: str) -> list[dict[str, Any]]:
        """
        Get all chunks for a specific section.

        Args:
            section: Section number (e.g., "712.11").

        Returns:
            List of chunk metadata dicts.

        Raises:
            VectorStoreError: If the operation fails.
        """
        try:
            results = self.collection.get(
                where={"section": section},
                include=["metadatas"],
            )
            return results["metadatas"] if results["metadatas"] else []

        except Exception as e:
            raise VectorStoreError(f"Failed to get section '{section}': {e}") from e

    def count(self, subpart: HRPSubpart | None = None) -> int:
        """
        Return the total number of chunks in the store.

        Args:
            subpart: Optional subpart to count. None counts all.

        Returns:
            Number of stored chunks.
        """
        if subpart is None:
            return self.collection.count()

        try:
            results = self.collection.get(
                where={"subpart": subpart.value},
                include=[],
            )
            return len(results["ids"]) if results["ids"] else 0
        except Exception:
            return 0

    def delete_all(self) -> None:
        """
        Delete all chunks from the collection.

        Warning: Use with caution.
        """
        try:
            all_ids = self.collection.get()["ids"]
            if all_ids:
                self.collection.delete(ids=all_ids)
        except Exception as e:
            raise VectorStoreError(f"Failed to delete chunks: {e}") from e
