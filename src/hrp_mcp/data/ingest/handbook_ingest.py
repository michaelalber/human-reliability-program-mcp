"""HRP Handbook ingestion from DOE website or local PDF."""

import logging
import re
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

from hrp_mcp.data.ingest.base import BaseIngestor, IngestResult
from hrp_mcp.models.regulations import RegulationChunk, SourceType
from hrp_mcp.rag.chunking import ChunkMetadata, RegulationChunker
from hrp_mcp.services import get_embedding_service, get_vector_store

logger = logging.getLogger(__name__)

# DOE HRP Handbook URL (publicly available HTML page)
HRP_HANDBOOK_URL = "https://www.energy.gov/ehss/human-reliability-program-handbook"

# Known handbook sections from the DOE website
HANDBOOK_SECTIONS = {
    "what_is_hrp": "What is the HRP?",
    "who_must_be_certified": "Who Must Be HRP Certified?",
    "hrp_requirements": "What Are the HRP Requirements?",
    "how_often": "How Often Are HRP Requirements Performed?",
    "responsibilities": "What Are My HRP Responsibilities?",
    "when_report": "When Should I Report a Concern?",
    "what_concern": "What Might Be a Concern?",
    "how_report": "How Do I Report a Concern?",
    "concern_identified": "What Happens When a Reliability Concern is Identified?",
    "removed_from_duties": "What Happens When Someone is Removed from HRP Duties?",
    "options": "What Are My Options?",
    "resources": "Resources",
    "glossary": "Glossary",
}


class HandbookIngestor(BaseIngestor):
    """Ingestor for DOE HRP Handbook from website or local PDF."""

    def __init__(self, batch_size: int = 50):
        """
        Initialize the handbook ingestor.

        Args:
            batch_size: Number of chunks to add at once.
        """
        self.batch_size = batch_size
        self._chunker = RegulationChunker(max_tokens=512, overlap_tokens=50)

    async def ingest(self, source_path: str | None = None) -> IngestResult:
        """
        Ingest HRP Handbook from local file or by downloading from DOE website.

        Args:
            source_path: Optional path to local file. If None, downloads from DOE.
                        Can be a PDF file or an HTML file.

        Returns:
            IngestResult with statistics.
        """
        result = IngestResult()

        try:
            if source_path:
                # Local file provided
                file_path = Path(source_path)
                if not file_path.exists():
                    result.add_error(f"Source file not found: {source_path}")
                    return result

                if file_path.suffix.lower() == ".pdf":
                    # Use docling for PDF
                    content = await self._parse_pdf(file_path)
                else:
                    # Assume HTML
                    content = file_path.read_text(encoding="utf-8")
                    content = self._parse_html(content)
            else:
                # Download from DOE website
                logger.info(f"Downloading HRP Handbook from {HRP_HANDBOOK_URL}")
                html_content = await self._download_html()
                content = self._parse_html(html_content)

            # Parse sections from content
            sections = self._parse_handbook_sections(content)
            result.sections_ingested = len(sections)

            if not sections:
                result.add_error("No sections found in handbook")
                return result

            # Chunk and embed
            all_chunks: list[RegulationChunk] = []
            for section_id, (title, section_content) in sections.items():
                metadata = ChunkMetadata(
                    section=section_id,
                    title=title,
                    citation=f"DOE HRP Handbook - {title}",
                    source=SourceType.HRP_HANDBOOK,
                )
                chunks = self._chunker.chunk_text(section_content, metadata)
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
        Download HRP Handbook HTML to local path.

        Args:
            target_path: Directory to save the HTML file.

        Returns:
            Path to the downloaded file.
        """
        target_dir = Path(target_path)
        target_dir.mkdir(parents=True, exist_ok=True)

        html_content = await self._download_html()

        file_path = target_dir / "hrp_handbook.html"
        file_path.write_text(html_content, encoding="utf-8")

        logger.info(f"Downloaded HRP Handbook to {file_path}")
        return str(file_path)

    async def _download_html(self) -> str:
        """Download the HRP Handbook HTML from DOE website."""
        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            resp = await client.get(HRP_HANDBOOK_URL)
            resp.raise_for_status()
            return resp.text

    async def _parse_pdf(self, pdf_path: Path) -> str:
        """Parse PDF file using docling."""
        try:
            from docling.document_converter import DocumentConverter

            converter = DocumentConverter()
            logger.info(f"Converting PDF: {pdf_path}")
            doc_result = converter.convert(str(pdf_path))
            return doc_result.document.export_to_markdown()
        except ImportError as e:
            raise ImportError(
                "docling is required for PDF processing. "
                "Install it with: pip install docling"
            ) from e

    def _parse_html(self, html_content: str) -> str:
        """Parse HTML content and extract text as markdown-like format."""
        soup = BeautifulSoup(html_content, "html.parser")

        # Find the main content area
        main_content = soup.find("main") or soup.find("article") or soup.find("body")

        if not main_content:
            return ""

        # Build markdown-like text
        lines = []

        for element in main_content.find_all(["h1", "h2", "h3", "h4", "p", "li", "ul"]):
            tag = element.name

            if tag in ("h1", "h2", "h3", "h4"):
                level = int(tag[1])
                text = element.get_text(strip=True)
                if text:
                    lines.append(f"\n{'#' * level} {text}\n")

            elif tag == "p":
                text = element.get_text(strip=True)
                if text:
                    lines.append(f"\n{text}\n")

            elif tag == "li":
                text = element.get_text(strip=True)
                if text:
                    lines.append(f"- {text}")

        return "\n".join(lines)

    def _parse_handbook_sections(
        self, content: str
    ) -> dict[str, tuple[str, str]]:
        """
        Parse handbook content into sections.

        Args:
            content: Text content (markdown-like format).

        Returns:
            Dict mapping section ID to (title, content) tuple.
        """
        sections: dict[str, tuple[str, str]] = {}

        # Split by headers (# or ##)
        header_pattern = r"^(#{1,4})\s+(.+)$"
        lines = content.split("\n")

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
