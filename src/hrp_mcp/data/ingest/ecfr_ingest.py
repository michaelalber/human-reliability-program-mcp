"""eCFR ingestion for 10 CFR Parts 707, 710, 712 using structure API."""

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import httpx
from defusedxml import ElementTree as ET  # noqa: N817

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element  # nosec B405 - type hint only

from hrp_mcp.data.ingest.base import BaseIngestor, IngestResult
from hrp_mcp.models.regulations import RegulationChunk, SourceType
from hrp_mcp.rag.chunking import ChunkMetadata, RegulationChunker
from hrp_mcp.services import get_embedding_service, get_vector_store

logger = logging.getLogger(__name__)

# eCFR API base URL
ECFR_API_BASE = "https://www.ecfr.gov/api/versioner/v1"

# Part configurations (source type mapping, fallback sections kept for reference)
CFR_PARTS = {
    707: {
        "name": "Workplace Substance Abuse Programs",
        "source": SourceType.CFR_707,
    },
    710: {
        "name": "Procedures for Determining Eligibility for Access",
        "source": SourceType.CFR_710,
    },
    712: {
        "name": "Human Reliability Program",
        "source": SourceType.CFR_712,
    },
}


class CFRPartIngestor(BaseIngestor):
    """Ingestor for 10 CFR Parts 707, 710, 712 from eCFR using structure API."""

    def __init__(self, part: int = 712, batch_size: int = 50):
        """
        Initialize the CFR part ingestor.

        Args:
            part: CFR part number (707, 710, or 712).
            batch_size: Number of chunks to add at once.
        """
        if part not in CFR_PARTS:
            raise ValueError(f"Unsupported part: {part}. Must be one of {list(CFR_PARTS.keys())}")

        self.part = part
        self.part_config = CFR_PARTS[part]
        self.batch_size = batch_size
        self._chunker = RegulationChunker(max_tokens=512, overlap_tokens=50)
        self._sections_cache: dict[str, str] | None = None

    @property
    def source_type(self) -> SourceType:
        """Get the source type for this part."""
        return self.part_config["source"]

    async def _fetch_structure(self) -> dict[str, str]:
        """
        Fetch section structure from eCFR API.

        Returns:
            Dict mapping section number to title (e.g., {"712.1": "Purpose"}).
        """
        if self._sections_cache is not None:
            return self._sections_cache

        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            # Get the latest date for Title 10
            titles_url = f"{ECFR_API_BASE}/titles"
            resp = await client.get(titles_url)
            resp.raise_for_status()
            titles_data = resp.json()

            latest_date = None
            for title in titles_data.get("titles", []):
                if title.get("number") == 10:
                    latest_date = title.get("up_to_date_as_of")
                    break

            if not latest_date:
                latest_date = datetime.now().strftime("%Y-%m-%d")
                logger.warning(f"Could not find Title 10 date, using {latest_date}")

            # Fetch structure JSON
            structure_url = f"{ECFR_API_BASE}/structure/{latest_date}/title-10.json"
            logger.info(f"Fetching structure from {structure_url}")
            resp = await client.get(structure_url)
            resp.raise_for_status()
            structure = resp.json()

            # Find our part and extract sections
            sections = self._extract_sections_from_structure(structure)
            self._sections_cache = sections

            logger.info(f"Found {len(sections)} sections for Part {self.part}")
            return sections

    def _extract_sections_from_structure(self, structure: dict) -> dict[str, str]:
        """
        Extract section numbers and titles from structure JSON.

        Args:
            structure: The full Title 10 structure JSON.

        Returns:
            Dict mapping section number to title.
        """
        sections: dict[str, str] = {}

        def find_part(node: dict, part_num: int) -> dict | None:
            """Recursively find a part in the structure."""
            if str(node.get("identifier", "")) == str(part_num):
                return node
            for child in node.get("children", []):
                result = find_part(child, part_num)
                if result:
                    return result
            return None

        def extract_sections(node: dict) -> None:
            """Recursively extract all sections from a node."""
            if node.get("type") == "section":
                identifier = node.get("identifier", "")
                # label_description has the title without the section number
                title = node.get("label_description", "")
                if identifier and title:
                    sections[identifier] = title
            for child in node.get("children", []):
                extract_sections(child)

        # Find our part
        part_node = find_part(structure, self.part)
        if part_node:
            extract_sections(part_node)

        return sections

    async def ingest(self, source_path: str | None = None) -> IngestResult:
        """
        Ingest 10 CFR Part from local file or by downloading.

        Args:
            source_path: Optional path to XML file. If None, downloads from eCFR.

        Returns:
            IngestResult with statistics.
        """
        result = IngestResult()

        try:
            # First, fetch the structure to get section list
            section_titles = await self._fetch_structure()

            if not section_titles:
                result.add_error(f"No sections found in structure for Part {self.part}")
                return result

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
            sections = self._parse_sections(xml_content, section_titles)
            result.sections_ingested = len(sections)

            if not sections:
                result.add_error(f"No sections found in XML for Part {self.part}")
                return result

            # Chunk and embed
            all_chunks: list[RegulationChunk] = []
            for section_num, (title, content) in sections.items():
                metadata = ChunkMetadata(
                    section=section_num,
                    title=title,
                    citation=f"10 CFR {section_num}",
                    source=self.source_type,
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
                f"Ingested Part {self.part}: {result.sections_ingested} sections, "
                f"created {result.chunks_created} chunks"
            )

        except Exception as e:
            result.add_error(str(e))
            logger.exception(f"Ingestion failed for Part {self.part}")

        return result

    async def download(self, target_path: str) -> str:
        """
        Download 10 CFR Part XML to local path.

        Args:
            target_path: Directory to save the XML file.

        Returns:
            Path to the downloaded file.
        """
        target_dir = Path(target_path)
        target_dir.mkdir(parents=True, exist_ok=True)

        xml_content = await self._download_xml()

        today = datetime.now().strftime("%Y-%m-%d")
        file_path = target_dir / f"10cfr{self.part}_{today}.xml"
        file_path.write_text(xml_content, encoding="utf-8")

        logger.info(f"Downloaded 10 CFR {self.part} to {file_path}")
        return str(file_path)

    async def _download_xml(self) -> str:
        """Download Title 10 XML from eCFR."""
        async with httpx.AsyncClient(timeout=300.0, follow_redirects=True) as client:
            # First, get the list of titles to find the latest date for Title 10
            titles_url = f"{ECFR_API_BASE}/titles"
            resp = await client.get(titles_url)
            resp.raise_for_status()
            titles_data = resp.json()

            # Find Title 10 and get its latest date
            latest_date = None
            for title in titles_data.get("titles", []):
                if title.get("number") == 10:
                    latest_date = title.get("up_to_date_as_of")
                    break

            if not latest_date:
                latest_date = datetime.now().strftime("%Y-%m-%d")
                logger.warning(f"Could not find Title 10 date, using {latest_date}")

            # Download the full title XML (we'll filter to our part)
            xml_url = f"{ECFR_API_BASE}/full/{latest_date}/title-10.xml"
            logger.info(f"Downloading from {xml_url}")

            resp = await client.get(xml_url)
            resp.raise_for_status()

            return resp.text

    def _parse_sections(
        self, xml_content: str, section_titles: dict[str, str]
    ) -> dict[str, tuple[str, str]]:
        """
        Parse sections from eCFR XML.

        Args:
            xml_content: Raw XML string.
            section_titles: Dict mapping section number to title from structure API.

        Returns:
            Dict mapping section number to (title, content) tuple.
        """
        sections: dict[str, tuple[str, str]] = {}

        try:
            # Parse XML
            root = ET.fromstring(xml_content)

            # Find sections in the XML structure
            for section_elem in self._find_sections(root):
                section_num = self._extract_section_number(section_elem)
                if section_num and section_num in section_titles:
                    title = self._extract_title(section_elem, section_num, section_titles)
                    content = self._extract_content(section_elem)
                    if content:
                        sections[section_num] = (title, content)

        except ET.ParseError as e:
            logger.error(f"XML parse error: {e}")

        # If XML parsing didn't work well, try regex fallback
        if len(sections) < len(section_titles) // 2:
            logger.info("XML parsing found few sections, trying regex fallback")
            regex_sections = self._parse_sections_regex(xml_content, section_titles)
            # Merge, preferring XML-parsed sections
            for section_num, data in regex_sections.items():
                if section_num not in sections:
                    sections[section_num] = data

        return sections

    def _find_sections(self, root: Element) -> list:
        """Find all section elements in XML."""
        sections = []

        # Try finding SECTION elements
        for elem in root.iter():
            tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
            if tag.upper() == "SECTION" or tag.upper() in ("DIV8", "DIV9"):
                sections.append(elem)

        return sections

    def _extract_section_number(self, elem: Element) -> str | None:
        """Extract section number from element."""
        pattern = rf"{self.part}\.(\d+)"

        # Try SECTNO element
        for child in elem:
            tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
            if tag.upper() == "SECTNO":
                text = (child.text or "").strip()
                match = re.search(pattern, text)
                if match:
                    return f"{self.part}.{match.group(1)}"

        # Try HEAD element
        for child in elem:
            tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
            if tag.upper() == "HEAD":
                text = (child.text or "").strip()
                match = re.search(pattern, text)
                if match:
                    return f"{self.part}.{match.group(1)}"

        # Try N attribute
        n_attr = elem.get("N", "")
        match = re.search(pattern, n_attr)
        if match:
            return f"{self.part}.{match.group(1)}"

        return None

    def _extract_title(
        self, elem: Element, section_num: str, section_titles: dict[str, str]
    ) -> str:
        """Extract section title from element or use structure API title."""
        # Try SUBJECT element
        for child in elem:
            tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
            if tag.upper() == "SUBJECT":
                text = (child.text or "").strip()
                if text:
                    return text

        # Try HEAD element (after section number)
        for child in elem:
            tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
            if tag.upper() == "HEAD":
                text = (child.text or "").strip()
                # Remove section number prefix
                text = re.sub(rf"^§?\s*{self.part}\.\d+\s*", "", text)
                if text:
                    return text

        # Fall back to structure API title
        return section_titles.get(section_num, "")

    def _extract_content(self, elem: Element) -> str:
        """Extract text content from element."""
        parts = []

        for child in elem.iter():
            tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
            if tag.upper() in ("P", "FP", "AMDPAR", "NOTE"):
                text = "".join(child.itertext()).strip()
                if text:
                    parts.append(text)

        return "\n\n".join(parts)

    def _parse_sections_regex(
        self, xml_content: str, section_titles: dict[str, str]
    ) -> dict[str, tuple[str, str]]:
        """Fallback regex parsing for section content."""
        sections: dict[str, tuple[str, str]] = {}

        # Try to find sections using regex patterns
        # Pattern: §XXX.XX followed by title and content
        pattern = rf"§\s*{self.part}\.(\d+)\s+([^\n]+)\n([\s\S]*?)(?=§\s*{self.part}\.\d+|$)"

        for match in re.finditer(pattern, xml_content):
            section_num = f"{self.part}.{match.group(1)}"
            if section_num in section_titles:
                title = match.group(2).strip()
                content = match.group(3).strip()
                # Clean up content
                content = re.sub(r"<[^>]+>", "", content)  # Remove HTML tags
                content = re.sub(r"\s+", " ", content)  # Normalize whitespace
                if content:
                    sections[section_num] = (
                        title or section_titles.get(section_num, ""),
                        content,
                    )

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


# Backward compatibility alias
HRPIngestor = CFRPartIngestor
