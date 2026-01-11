"""Document chunking strategies for HRP regulation text."""

import re
from dataclasses import dataclass

import tiktoken

from hrp_mcp.models.regulations import (
    HRPSubpart,
    RegulationChunk,
    SourceType,
    get_subpart_for_section,
)


@dataclass
class ChunkMetadata:
    """Metadata for a text chunk during processing."""

    section: str
    title: str = ""
    citation: str = ""
    source: SourceType = SourceType.CFR_712


class RegulationChunker:
    """Section-aware chunking for HRP regulation text.

    Chunks regulation text while trying to preserve section boundaries
    and maintain semantic coherence.
    """

    def __init__(
        self,
        max_tokens: int = 512,
        overlap_tokens: int = 50,
        tokenizer: str = "cl100k_base",
    ):
        """
        Initialize the chunker.

        Args:
            max_tokens: Maximum tokens per chunk (default 512).
            overlap_tokens: Token overlap between chunks (default 50).
            tokenizer: tiktoken tokenizer to use (default cl100k_base for OpenAI).
        """
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens
        self._tokenizer = tiktoken.get_encoding(tokenizer)

    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken."""
        return len(self._tokenizer.encode(text))

    def chunk_text(
        self,
        text: str,
        metadata: ChunkMetadata,
    ) -> list[RegulationChunk]:
        """
        Chunk text into appropriately sized pieces.

        Args:
            text: The regulation text to chunk.
            metadata: Metadata about the source section.

        Returns:
            List of RegulationChunk objects.
        """
        # Only set subpart for 10 CFR 712
        subpart = None
        if metadata.source == SourceType.CFR_712:
            subpart = get_subpart_for_section(metadata.section)

        # If text fits in one chunk, return it
        if self.count_tokens(text) <= self.max_tokens:
            chunk_id = self._make_chunk_id(metadata.section, metadata.source, 0)
            return [
                RegulationChunk(
                    id=chunk_id,
                    source=metadata.source,
                    subpart=subpart,
                    section=metadata.section,
                    title=metadata.title,
                    content=text.strip(),
                    citation=metadata.citation,
                    chunk_index=0,
                )
            ]

        # Otherwise, split into chunks with overlap
        return self._split_with_overlap(text, metadata, subpart)

    def _split_with_overlap(
        self,
        text: str,
        metadata: ChunkMetadata,
        subpart: HRPSubpart | None,
    ) -> list[RegulationChunk]:
        """Split text into overlapping chunks."""
        chunks: list[RegulationChunk] = []

        # Split by paragraphs first to maintain coherence
        paragraphs = self._split_paragraphs(text)

        current_chunk_text = ""
        current_tokens = 0
        chunk_index = 0

        for paragraph in paragraphs:
            para_tokens = self.count_tokens(paragraph)

            # If single paragraph exceeds max, split by sentences
            if para_tokens > self.max_tokens:
                if current_chunk_text:
                    # Save current chunk first
                    chunk_id = self._make_chunk_id(metadata.section, metadata.source, chunk_index)
                    chunks.append(
                        RegulationChunk(
                            id=chunk_id,
                            source=metadata.source,
                            subpart=subpart,
                            section=metadata.section,
                            title=metadata.title,
                            content=current_chunk_text.strip(),
                            citation=metadata.citation,
                            chunk_index=chunk_index,
                        )
                    )
                    chunk_index += 1
                    current_chunk_text = ""
                    current_tokens = 0

                # Split long paragraph by sentences
                sentence_chunks = self._split_long_paragraph(
                    paragraph, metadata, subpart, chunk_index
                )
                chunks.extend(sentence_chunks)
                chunk_index += len(sentence_chunks)
                continue

            # Check if adding paragraph would exceed limit
            if current_tokens + para_tokens > self.max_tokens:
                # Save current chunk
                if current_chunk_text:
                    chunk_id = self._make_chunk_id(metadata.section, metadata.source, chunk_index)
                    chunks.append(
                        RegulationChunk(
                            id=chunk_id,
                            source=metadata.source,
                            subpart=subpart,
                            section=metadata.section,
                            title=metadata.title,
                            content=current_chunk_text.strip(),
                            citation=metadata.citation,
                            chunk_index=chunk_index,
                        )
                    )
                    chunk_index += 1

                    # Start new chunk with overlap from previous
                    overlap_text = self._get_overlap_text(current_chunk_text)
                    current_chunk_text = overlap_text + "\n\n" + paragraph
                    current_tokens = self.count_tokens(current_chunk_text)
                else:
                    current_chunk_text = paragraph
                    current_tokens = para_tokens
            else:
                # Add to current chunk
                if current_chunk_text:
                    current_chunk_text += "\n\n" + paragraph
                else:
                    current_chunk_text = paragraph
                current_tokens += para_tokens

        # Don't forget the last chunk
        if current_chunk_text:
            chunk_id = self._make_chunk_id(metadata.section, metadata.source, chunk_index)
            chunks.append(
                RegulationChunk(
                    id=chunk_id,
                    source=metadata.source,
                    subpart=subpart,
                    section=metadata.section,
                    title=metadata.title,
                    content=current_chunk_text.strip(),
                    citation=metadata.citation,
                    chunk_index=chunk_index,
                )
            )

        return chunks

    def _split_paragraphs(self, text: str) -> list[str]:
        """Split text by paragraph boundaries."""
        # Split on double newlines, preserve single newlines
        paragraphs = re.split(r"\n\s*\n", text)
        return [p.strip() for p in paragraphs if p.strip()]

    def _split_long_paragraph(
        self,
        paragraph: str,
        metadata: ChunkMetadata,
        subpart: HRPSubpart | None,
        start_index: int,
    ) -> list[RegulationChunk]:
        """Split a very long paragraph by sentences."""
        chunks: list[RegulationChunk] = []

        # Simple sentence splitting (handles common cases)
        sentences = re.split(r"(?<=[.!?])\s+", paragraph)

        current_chunk_text = ""
        current_tokens = 0
        chunk_index = start_index

        for sentence in sentences:
            sentence_tokens = self.count_tokens(sentence)

            if current_tokens + sentence_tokens > self.max_tokens:
                if current_chunk_text:
                    chunk_id = self._make_chunk_id(metadata.section, metadata.source, chunk_index)
                    chunks.append(
                        RegulationChunk(
                            id=chunk_id,
                            source=metadata.source,
                            subpart=subpart,
                            section=metadata.section,
                            title=metadata.title,
                            content=current_chunk_text.strip(),
                            citation=metadata.citation,
                            chunk_index=chunk_index,
                        )
                    )
                    chunk_index += 1

                current_chunk_text = sentence
                current_tokens = sentence_tokens
            else:
                if current_chunk_text:
                    current_chunk_text += " " + sentence
                else:
                    current_chunk_text = sentence
                current_tokens += sentence_tokens

        if current_chunk_text:
            chunk_id = self._make_chunk_id(metadata.section, metadata.source, chunk_index)
            chunks.append(
                RegulationChunk(
                    id=chunk_id,
                    source=metadata.source,
                    subpart=subpart,
                    section=metadata.section,
                    title=metadata.title,
                    content=current_chunk_text.strip(),
                    citation=metadata.citation,
                    chunk_index=chunk_index,
                )
            )

        return chunks

    def _get_overlap_text(self, text: str) -> str:
        """Get the last N tokens of text for overlap."""
        tokens = self._tokenizer.encode(text)
        if len(tokens) <= self.overlap_tokens:
            return text
        overlap_tokens = tokens[-self.overlap_tokens :]
        return self._tokenizer.decode(overlap_tokens)

    def _make_chunk_id(
        self,
        section: str,
        source: SourceType,
        chunk_index: int,
    ) -> str:
        """Generate a unique chunk ID."""
        # Normalize section for ID
        section_normalized = section.replace(".", "-")
        # Use source prefix (e.g., "10cfr712", "10cfr710")
        return f"{source.value}:{section_normalized}:chunk-{chunk_index:03d}"
