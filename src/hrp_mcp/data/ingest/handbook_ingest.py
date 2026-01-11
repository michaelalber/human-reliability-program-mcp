"""HRP Handbook PDF ingestion using docling."""

import logging
import re
from pathlib import Path

import httpx
from docling.document_converter import DocumentConverter

from hrp_mcp.data.ingest.base import BaseIngestor, IngestResult
from hrp_mcp.models.regulations import RegulationChunk, SourceType
from hrp_mcp.rag.chunking import ChunkMetadata, RegulationChunker
from hrp_mcp.services import get_embedding_service, get_vector_store

logger = logging.getLogger(__name__)

# DOE HRP Handbook URL (publicly available)
HRP_HANDBOOK_URL = "https://www.energy.gov/ehss/downloads/doe-handbook-human-reliability-program"

# Known handbook sections/chapters for organization
HANDBOOK_CHAPTERS = {
    "chapter1": "Introduction and Purpose",
    "chapter2": "Program Administration",
    "chapter3": "HRP Position Designation",
    "chapter4": "HRP Certification and Recertification",
    "chapter5": "Supervisory Review",
    "chapter6": "Medical Assessment",
    "chapter7": "Management Evaluation",
    "chapter8": "Security Review",
    "chapter9": "Drug and Alcohol Testing",
    "chapter10": "Removal and Reinstatement",
    "chapter11": "Administrative Review Process",
    "appendix_a": "Definitions",
    "appendix_b": "Forms and Records",
    "appendix_c": "Medical Standards Reference",
}


class HandbookIngestor(BaseIngestor):
    """Ingestor for DOE HRP Implementation Handbook PDF."""

    def __init__(self, batch_size: int = 50):
        """
        Initialize the handbook ingestor.

        Args:
            batch_size: Number of chunks to add at once.
        """
        self.batch_size = batch_size
        self._chunker = RegulationChunker(max_tokens=512, overlap_tokens=50)
        self._converter = DocumentConverter()

    async def ingest(self, source_path: str | None = None) -> IngestResult:
        """
        Ingest HRP Handbook from local file or by downloading.

        Args:
            source_path: Optional path to PDF file. If None, downloads from DOE.

        Returns:
            IngestResult with statistics.
        """
        result = IngestResult()

        try:
            # Get PDF path
            if source_path:
                pdf_path = Path(source_path)
                if not pdf_path.exists():
                    result.add_error(f"Source file not found: {source_path}")
                    return result
            else:
                result.add_error(
                    "HRP Handbook must be downloaded manually from DOE website. "
                    "Please download from: https://www.energy.gov/ehss/downloads/doe-handbook-human-reliability-program "
                    "and provide the path using --source option."
                )
                return result

            # Convert PDF to document using docling
            logger.info(f"Converting PDF: {pdf_path}")
            doc_result = self._converter.convert(str(pdf_path))

            # Extract markdown content
            markdown_content = doc_result.document.export_to_markdown()

            # Parse and chunk the content
            sections = self._parse_handbook_sections(markdown_content)
            result.sections_ingested = len(sections)

            if not sections:
                result.add_error("No sections found in handbook PDF")
                return result

            # Chunk and embed
            all_chunks: list[RegulationChunk] = []
            for section_id, (title, content) in sections.items():
                metadata = ChunkMetadata(
                    section=section_id,
                    title=title,
                    citation=f"DOE HRP Handbook - {title}",
                    source=SourceType.HRP_HANDBOOK,
                )
                chunks = self._chunker.chunk_text(content, metadata)
                all_chunks.extend(chunks)

            result.chunks_created = len(all_chunks)

            if not all_chunks:
                result.add_error("No chunks created from handbook")
                return result

            # Generate embeddings and store
            await self._store_chunks(all_chunks)

            logger.info(
                f"Ingested HRP Handbook: {result.sections_ingested} sections, "
                f"created {result.chunks_created} chunks"
            )

        except Exception as e:
            result.add_error(str(e))
            logger.exception("Handbook ingestion failed")

        return result

    async def download(self, target_path: str) -> str:
        """
        Download HRP Handbook PDF to local path.

        Note: DOE website may require manual download due to terms/conditions.

        Args:
            target_path: Directory to save the PDF file.

        Returns:
            Path to the downloaded file.
        """
        target_dir = Path(target_path)
        target_dir.mkdir(parents=True, exist_ok=True)

        # Attempt download (may not work if DOE requires form submission)
        async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
            try:
                resp = await client.get(HRP_HANDBOOK_URL)
                resp.raise_for_status()

                # Check if we got a PDF or a landing page
                content_type = resp.headers.get("content-type", "")
                if "pdf" not in content_type.lower():
                    raise ValueError(
                        "DOE website returned landing page instead of PDF. "
                        "Please download manually from: "
                        "https://www.energy.gov/ehss/downloads/doe-handbook-human-reliability-program"
                    )

                file_path = target_dir / "hrp_handbook.pdf"
                file_path.write_bytes(resp.content)

                logger.info(f"Downloaded HRP Handbook to {file_path}")
                return str(file_path)

            except httpx.HTTPStatusError as e:
                raise ValueError(
                    f"Failed to download HRP Handbook: {e}. "
                    "Please download manually from: "
                    "https://www.energy.gov/ehss/downloads/doe-handbook-human-reliability-program"
                ) from e

    def _parse_handbook_sections(
        self, markdown_content: str
    ) -> dict[str, tuple[str, str]]:
        """
        Parse handbook markdown content into sections.

        Args:
            markdown_content: Markdown text from docling conversion.

        Returns:
            Dict mapping section ID to (title, content) tuple.
        """
        sections: dict[str, tuple[str, str]] = {}

        # Split by headers (# or ##)
        # Pattern matches markdown headers
        header_pattern = r"^(#{1,3})\s+(.+)$"
        lines = markdown_content.split("\n")

        current_section_id = "intro"
        current_title = "Introduction"
        current_content: list[str] = []
        section_counter = 0

        for line in lines:
            match = re.match(header_pattern, line)
            if match:
                # Save previous section if it has content
                if current_content:
                    content_text = "\n".join(current_content).strip()
                    if content_text:
                        sections[current_section_id] = (current_title, content_text)

                # Start new section
                title = match.group(2).strip()

                # Generate section ID
                section_counter += 1
                section_id = self._generate_section_id(title, section_counter)

                current_section_id = section_id
                current_title = title
                current_content = []
            else:
                current_content.append(line)

        # Don't forget last section
        if current_content:
            content_text = "\n".join(current_content).strip()
            if content_text:
                sections[current_section_id] = (current_title, content_text)

        return sections

    def _generate_section_id(self, title: str, counter: int) -> str:
        """Generate a section ID from title."""
        # Normalize title
        normalized = title.lower()
        normalized = re.sub(r"[^a-z0-9\s]", "", normalized)
        normalized = re.sub(r"\s+", "_", normalized.strip())

        # Limit length and add counter for uniqueness
        if len(normalized) > 30:
            normalized = normalized[:30]

        return f"handbook:{normalized}:{counter:03d}"

    async def _store_chunks(self, chunks: list[RegulationChunk]) -> None:
        """Generate embeddings and store chunks in vector store."""
        embedding_service = get_embedding_service()
        vector_store = get_vector_store()

        # Process in batches
        for i in range(0, len(chunks), self.batch_size):
            batch = chunks[i : i + self.batch_size]

            # Generate embeddings
            texts = [chunk.to_embedding_text() for chunk in batch]
            embeddings = embedding_service.embed_batch(texts)

            # Store in vector store
            vector_store.add_chunks_batch(batch, embeddings)

            logger.debug(f"Stored batch of {len(batch)} chunks")
