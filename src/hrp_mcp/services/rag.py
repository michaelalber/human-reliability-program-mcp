"""RAG (Retrieval-Augmented Generation) service for HRP regulation search."""

from hrp_mcp.models.errors import SectionNotFoundError
from hrp_mcp.models.regulations import (
    HRPSubpart,
    RegulationChunk,
    SearchResult,
)
from hrp_mcp.services.embeddings import EmbeddingService
from hrp_mcp.services.vector_store import VectorStoreService


class RagService:
    """Retrieval-Augmented Generation service for HRP regulations."""

    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store: VectorStoreService,
    ):
        """
        Initialize the RAG service.

        Args:
            embedding_service: Service for generating query embeddings.
            vector_store: Service for vector similarity search.
        """
        self._embeddings = embedding_service
        self._vector_store = vector_store

    async def search(
        self,
        query: str,
        subpart: HRPSubpart | None = None,
        section: str | None = None,
        limit: int = 10,
    ) -> list[SearchResult]:
        """
        Semantic search for HRP regulations.

        Args:
            query: Natural language search query.
            subpart: Optional filter (Subpart A or B). None searches all.
            section: Optional section filter (e.g., "712.11").
            limit: Maximum number of results to return.

        Returns:
            Ranked list of regulation chunks with relevance scores.
        """
        # Generate query embedding
        query_embedding = self._embeddings.embed(query)

        # Search vector store
        results = self._vector_store.search(
            query_embedding=query_embedding,
            subpart=subpart,
            section=section,
            limit=limit,
        )

        # Convert to SearchResult objects
        search_results: list[SearchResult] = []
        for metadata, score in results:
            # Reconstruct RegulationChunk from stored JSON
            full_json = metadata.get("full_json")
            if full_json:
                chunk = RegulationChunk.model_validate_json(full_json)
                search_results.append(
                    SearchResult(
                        chunk=chunk,
                        score=score,
                    )
                )

        return search_results

    async def search_subpart_a(
        self,
        query: str,
        limit: int = 10,
    ) -> list[SearchResult]:
        """
        Search Subpart A (Procedures) only.

        Args:
            query: Natural language search query.
            limit: Maximum number of results.

        Returns:
            Ranked list of Subpart A regulation chunks.
        """
        return await self.search(
            query=query,
            subpart=HRPSubpart.SUBPART_A,
            limit=limit,
        )

    async def search_subpart_b(
        self,
        query: str,
        limit: int = 10,
    ) -> list[SearchResult]:
        """
        Search Subpart B (Medical Standards) only.

        Args:
            query: Natural language search query.
            limit: Maximum number of results.

        Returns:
            Ranked list of Subpart B regulation chunks.
        """
        return await self.search(
            query=query,
            subpart=HRPSubpart.SUBPART_B,
            limit=limit,
        )

    async def get_chunk(self, chunk_id: str) -> RegulationChunk:
        """
        Retrieve a specific regulation chunk by ID.

        Args:
            chunk_id: Chunk identifier.

        Returns:
            The requested regulation chunk.

        Raises:
            SectionNotFoundError: If the chunk doesn't exist.
        """
        metadata = self._vector_store.get_by_id(chunk_id)

        if metadata is None:
            raise SectionNotFoundError(chunk_id)

        full_json = metadata.get("full_json")
        if not full_json:
            raise SectionNotFoundError(chunk_id)

        return RegulationChunk.model_validate_json(full_json)

    async def get_section(self, section: str) -> list[RegulationChunk]:
        """
        Retrieve all chunks for a specific section.

        Args:
            section: Section number (e.g., "712.11").

        Returns:
            List of regulation chunks for the section, ordered by chunk_index.

        Raises:
            SectionNotFoundError: If no chunks exist for the section.
        """
        metadata_list = self._vector_store.get_by_section(section)

        if not metadata_list:
            raise SectionNotFoundError(section)

        chunks = []
        for metadata in metadata_list:
            full_json = metadata.get("full_json")
            if full_json:
                chunks.append(RegulationChunk.model_validate_json(full_json))

        # Sort by chunk_index
        chunks.sort(key=lambda c: c.chunk_index)
        return chunks

    def get_store_count(self, subpart: HRPSubpart | None = None) -> int:
        """Return the number of chunks in the vector store."""
        return self._vector_store.count(subpart)
