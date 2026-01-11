"""eCFR ingestion for 10 CFR Part 712 (Human Reliability Program)."""

import logging
import re
from datetime import datetime
from pathlib import Path

import httpx
from defusedxml import ElementTree as ET  # noqa: N817

from hrp_mcp.data.ingest.base import BaseIngestor, IngestResult
from hrp_mcp.models.regulations import RegulationChunk
from hrp_mcp.rag.chunking import ChunkMetadata, RegulationChunker
from hrp_mcp.services import get_embedding_service, get_vector_store

logger = logging.getLogger(__name__)

# eCFR API base URL
ECFR_API_BASE = "https://www.ecfr.gov/api/versioner/v1"

# HRP sections we want to ingest (Part 712)
HRP_SECTIONS = {
    # Subpart A - Procedures
    "712.1": "Purpose",
    "712.2": "Scope",
    "712.3": "Definitions",
    "712.10": "Designation of HRP positions",
    "712.11": "General requirements for HRP certification",
    "712.12": "HRP recertification",
    "712.13": "Medical assessment",
    "712.14": "Supervisory review",
    "712.15": "Drug and alcohol testing",
    "712.16": "Management evaluation",
    "712.17": "DOE security review",
    "712.18": "Transferring HRP certification",
    "712.19": "Temporary removal from HRP",
    "712.20": "Removal from HRP",
    "712.21": "Reinstatement",
    "712.22": "Request for reconsideration",
    "712.23": "Administrative review",
    "712.24": "Administrative Judge",
    "712.25": "Secretary review",
    # Subpart B - Medical Standards
    "712.30": "Medical standards - general",
    "712.31": "Application of medical standards",
    "712.32": "Physical examination",
    "712.33": "Designated Physician",
    "712.34": "Psychological evaluation",
    "712.35": "Return to work evaluation",
    "712.36": "Medical disqualification",
    "712.37": "Medical removal protection",
    "712.38": "Medical records",
}


class HRPIngestor(BaseIngestor):
    """Ingestor for 10 CFR Part 712 from eCFR."""

    def __init__(self, batch_size: int = 50):
        """
        Initialize the HRP ingestor.

        Args:
            batch_size: Number of chunks to add at once.
        """
        self.batch_size = batch_size
        self._chunker = RegulationChunker(max_tokens=512, overlap_tokens=50)

    async def ingest(self, source_path: str | None = None) -> IngestResult:
        """
        Ingest 10 CFR Part 712 from local file or by downloading.

        Args:
            source_path: Optional path to XML file. If None, downloads from eCFR.

        Returns:
            IngestResult with statistics.
        """
        result = IngestResult()

        try:
            # Get XML content
            if source_path:
                xml_path = Path(source_path)
                if not xml_path.exists():
                    result.add_error(f"Source file not found: {source_path}")
                    return result
                xml_content = xml_path.read_text(encoding="utf-8")
            else:
                # Download from eCFR
                xml_content = await self._download_xml()

            # Parse sections
            sections = self._parse_sections(xml_content)
            result.sections_ingested = len(sections)

            if not sections:
                result.add_error("No sections found in XML")
                return result

            # Chunk and embed
            all_chunks: list[RegulationChunk] = []
            for section_num, (title, content) in sections.items():
                metadata = ChunkMetadata(
                    section=section_num,
                    title=title,
                    citation=f"10 CFR {section_num}",
                )
                chunks = self._chunker.chunk_text(content, metadata)
                all_chunks.extend(chunks)

            result.chunks_created = len(all_chunks)

            if not all_chunks:
                result.add_error("No chunks created from sections")
                return result

            # Generate embeddings and store
            await self._store_chunks(all_chunks)

            logger.info(
                f"Ingested {result.sections_ingested} sections, "
                f"created {result.chunks_created} chunks"
            )

        except Exception as e:
            result.add_error(str(e))
            logger.exception("Ingestion failed")

        return result

    async def download(self, target_path: str) -> str:
        """
        Download 10 CFR Part 712 XML to local path.

        Args:
            target_path: Directory to save the XML file.

        Returns:
            Path to the downloaded file.
        """
        target_dir = Path(target_path)
        target_dir.mkdir(parents=True, exist_ok=True)

        xml_content = await self._download_xml()

        today = datetime.now().strftime("%Y-%m-%d")
        file_path = target_dir / f"10cfr712_{today}.xml"
        file_path.write_text(xml_content, encoding="utf-8")

        logger.info(f"Downloaded 10 CFR 712 to {file_path}")
        return str(file_path)

    async def _download_xml(self) -> str:
        """Download Title 10, Chapter III, Part 712 XML from eCFR."""
        # Get latest date
        async with httpx.AsyncClient(timeout=300.0) as client:
            # First, get the current date for Title 10
            dates_url = f"{ECFR_API_BASE}/titles/10"
            resp = await client.get(dates_url)
            resp.raise_for_status()
            dates_data = resp.json()
            latest_date = dates_data.get("latest_issue_date", datetime.now().strftime("%Y-%m-%d"))

            # Download the full title XML (we'll filter to Part 712)
            xml_url = f"{ECFR_API_BASE}/full/{latest_date}/title-10.xml"
            logger.info(f"Downloading from {xml_url}")

            resp = await client.get(xml_url)
            resp.raise_for_status()

            return resp.text

    def _parse_sections(self, xml_content: str) -> dict[str, tuple[str, str]]:
        """
        Parse sections from eCFR XML.

        Args:
            xml_content: Raw XML string.

        Returns:
            Dict mapping section number to (title, content) tuple.
        """
        sections: dict[str, tuple[str, str]] = {}

        try:
            # Parse XML
            root = ET.fromstring(xml_content)

            # Find Part 712 in the XML structure
            # eCFR structure: TITLE > CHAPTER > SUBCHAPTER > PART > SUBPART > SECTION
            # or: DIV1 > DIV2 > ... > DIV8 for some formats

            # Try different possible structures
            for section_elem in self._find_sections(root):
                section_num = self._extract_section_number(section_elem)
                if section_num and section_num in HRP_SECTIONS:
                    title = self._extract_title(section_elem, section_num)
                    content = self._extract_content(section_elem)
                    if content:
                        sections[section_num] = (title, content)

        except ET.ParseError as e:
            logger.error(f"XML parse error: {e}")

        # If XML parsing didn't work, try regex fallback
        if not sections:
            sections = self._parse_sections_regex(xml_content)

        return sections

    def _find_sections(self, root: ET.Element) -> list:
        """Find all section elements in XML."""
        sections = []

        # Try finding SECTION elements
        for elem in root.iter():
            tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
            if tag.upper() == "SECTION" or tag.upper() in ("DIV8", "DIV9"):
                sections.append(elem)

        return sections

    def _extract_section_number(self, elem: ET.Element) -> str | None:
        """Extract section number from element."""
        # Try SECTNO element
        for child in elem:
            tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
            if tag.upper() == "SECTNO":
                text = (child.text or "").strip()
                # Extract number from "§ 712.11" or "712.11"
                match = re.search(r"712\.(\d+)", text)
                if match:
                    return f"712.{match.group(1)}"

        # Try HEAD element
        for child in elem:
            tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
            if tag.upper() == "HEAD":
                text = (child.text or "").strip()
                match = re.search(r"712\.(\d+)", text)
                if match:
                    return f"712.{match.group(1)}"

        # Try N attribute
        n_attr = elem.get("N", "")
        match = re.search(r"712\.(\d+)", n_attr)
        if match:
            return f"712.{match.group(1)}"

        return None

    def _extract_title(self, elem: ET.Element, section_num: str) -> str:
        """Extract section title from element."""
        # Try SUBJECT element
        for child in elem:
            tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
            if tag.upper() == "SUBJECT":
                return (child.text or "").strip()

        # Try HEAD element (after section number)
        for child in elem:
            tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
            if tag.upper() == "HEAD":
                text = (child.text or "").strip()
                # Remove section number prefix
                text = re.sub(r"^§?\s*712\.\d+\s*", "", text)
                if text:
                    return text

        # Fall back to known titles
        return HRP_SECTIONS.get(section_num, "")

    def _extract_content(self, elem: ET.Element) -> str:
        """Extract text content from element."""
        parts = []

        for child in elem.iter():
            tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
            if tag.upper() in ("P", "FP", "AMDPAR", "NOTE"):
                text = "".join(child.itertext()).strip()
                if text:
                    parts.append(text)

        return "\n\n".join(parts)

    def _parse_sections_regex(self, xml_content: str) -> dict[str, tuple[str, str]]:
        """Fallback regex parsing for section content."""
        sections: dict[str, tuple[str, str]] = {}

        # Try to find sections using regex patterns
        # Pattern: §712.XX followed by title and content
        pattern = r"§\s*712\.(\d+)\s+([^\n]+)\n([\s\S]*?)(?=§\s*712\.\d+|$)"

        for match in re.finditer(pattern, xml_content):
            section_num = f"712.{match.group(1)}"
            if section_num in HRP_SECTIONS:
                title = match.group(2).strip()
                content = match.group(3).strip()
                # Clean up content
                content = re.sub(r"<[^>]+>", "", content)  # Remove HTML tags
                content = re.sub(r"\s+", " ", content)  # Normalize whitespace
                if content:
                    sections[section_num] = (title or HRP_SECTIONS[section_num], content)

        return sections

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
