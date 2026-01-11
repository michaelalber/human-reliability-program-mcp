#!/usr/bin/env python3
"""Script to ingest 10 CFR Part 712 regulations into the vector store."""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from hrp_mcp.data.ingest import HRPIngestor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> int:
    """Run the ingestion process."""
    parser = argparse.ArgumentParser(
        description="Ingest 10 CFR Part 712 regulations into the vector store."
    )
    parser.add_argument(
        "--source",
        type=str,
        help="Path to local XML file. If not provided, downloads from eCFR.",
    )
    parser.add_argument(
        "--download",
        action="store_true",
        help="Download regulations from eCFR and save to data/regulations/",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing data before ingesting.",
    )

    args = parser.parse_args()

    ingestor = HRPIngestor()

    # Clear existing data if requested
    if args.clear:
        logger.info("Clearing existing vector store data...")
        from hrp_mcp.services import get_vector_store
        vector_store = get_vector_store()
        vector_store.delete_all()
        logger.info("Vector store cleared.")

    # Download if requested
    if args.download:
        logger.info("Downloading regulations from eCFR...")
        data_dir = Path(__file__).parent.parent / "data" / "regulations"
        data_dir.mkdir(parents=True, exist_ok=True)
        source_path = await ingestor.download(str(data_dir))
        logger.info(f"Downloaded to: {source_path}")
    else:
        source_path = args.source

    # Ingest
    logger.info("Starting ingestion...")
    result = await ingestor.ingest(source_path)

    # Report results
    logger.info(f"Ingestion complete:")
    logger.info(f"  Sections ingested: {result.sections_ingested}")
    logger.info(f"  Chunks created: {result.chunks_created}")

    if result.errors:
        logger.warning(f"  Errors ({len(result.errors)}):")
        for error in result.errors[:10]:
            logger.warning(f"    - {error}")
        if len(result.errors) > 10:
            logger.warning(f"    ... and {len(result.errors) - 10} more")

    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
