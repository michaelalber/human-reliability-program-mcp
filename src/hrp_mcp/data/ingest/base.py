"""Base classes for data ingestion."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class IngestResult:
    """Result of a data ingestion operation."""

    sections_ingested: int = 0
    chunks_created: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        """Return True if ingestion was successful."""
        return self.chunks_created > 0

    def add_error(self, error: str) -> None:
        """Add an error message."""
        self.errors.append(error)


class BaseIngestor(ABC):
    """Abstract base class for data ingestors."""

    @abstractmethod
    async def ingest(self, source_path: str | None = None) -> IngestResult:
        """
        Ingest data from a source.

        Args:
            source_path: Optional path to source file. If None, may download.

        Returns:
            IngestResult with statistics and any errors.
        """
        pass

    @abstractmethod
    async def download(self, target_path: str) -> str:
        """
        Download source data to a local path.

        Args:
            target_path: Directory to save downloaded files.

        Returns:
            Path to the downloaded file.
        """
        pass
