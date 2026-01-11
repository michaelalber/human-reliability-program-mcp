#!/usr/bin/env python3
"""Script to ingest 10 CFR Parts 707, 710, 712 regulations and HRP Handbook into the vector store."""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from hrp_mcp.data.ingest import CFRPartIngestor, HandbookIngestor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Available parts
AVAILABLE_PARTS = [707, 710, 712]


async def ingest_part(part: int, download: bool, data_dir: Path) -> dict:
    """Ingest a single CFR part."""
    logger.info(f"Processing 10 CFR Part {part}...")
    ingestor = CFRPartIngestor(part=part)

    # Download if requested
    if download:
        logger.info(f"Downloading Part {part} from eCFR...")
        source_path = await ingestor.download(str(data_dir))
        logger.info(f"Downloaded to: {source_path}")
    else:
        source_path = None

    # Ingest
    logger.info(f"Starting ingestion for Part {part}...")
    result = await ingestor.ingest(source_path)

    return {
        "part": part,
        "sections": result.sections_ingested,
        "chunks": result.chunks_created,
        "errors": result.errors,
        "success": result.success,
    }


async def ingest_handbook(source_path: str | None) -> dict:
    """Ingest the HRP Handbook PDF."""
    logger.info("Processing HRP Handbook...")
    ingestor = HandbookIngestor()

    # Ingest
    logger.info("Starting handbook ingestion...")
    result = await ingestor.ingest(source_path)

    return {
        "part": "handbook",
        "sections": result.sections_ingested,
        "chunks": result.chunks_created,
        "errors": result.errors,
        "success": result.success,
    }


async def main() -> int:
    """Run the ingestion process."""
    parser = argparse.ArgumentParser(
        description="Ingest 10 CFR Parts 707, 710, 712 regulations and HRP Handbook into the vector store."
    )
    parser.add_argument(
        "--parts",
        type=str,
        default="712",
        help="Comma-separated list of parts to ingest (707,710,712). Default: 712",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Ingest all parts (707, 710, 712).",
    )
    parser.add_argument(
        "--handbook",
        type=str,
        metavar="PATH",
        help="Path to HRP Handbook PDF file to ingest.",
    )
    parser.add_argument(
        "--source",
        type=str,
        help="Path to local XML file (only for single CFR part ingestion).",
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

    # Determine which CFR parts to ingest
    ingest_cfr_parts = not args.handbook  # Skip CFR if only doing handbook

    if ingest_cfr_parts:
        if args.all:
            parts = AVAILABLE_PARTS
        else:
            parts = [int(p.strip()) for p in args.parts.split(",")]
            for p in parts:
                if p not in AVAILABLE_PARTS:
                    logger.error(f"Invalid part: {p}. Available parts: {AVAILABLE_PARTS}")
                    return 1
    else:
        parts = []

    # Clear existing data if requested
    if args.clear:
        logger.info("Clearing existing vector store data...")
        from hrp_mcp.services import get_vector_store

        vector_store = get_vector_store()
        vector_store.delete_all()
        logger.info("Vector store cleared.")

    # Setup data directory
    data_dir = Path(__file__).parent.parent / "data" / "regulations"
    data_dir.mkdir(parents=True, exist_ok=True)

    # Ingest results tracking
    total_sections = 0
    total_chunks = 0
    all_errors = []
    processed_sources = []

    # Ingest CFR parts
    for part in parts:
        result = await ingest_part(part, args.download, data_dir)
        total_sections += result["sections"]
        total_chunks += result["chunks"]
        all_errors.extend(result["errors"])
        processed_sources.append(f"10 CFR {part}")

        logger.info(
            f"Part {part}: {result['sections']} sections, {result['chunks']} chunks"
        )

    # Ingest HRP Handbook if requested
    if args.handbook:
        result = await ingest_handbook(args.handbook)
        total_sections += result["sections"]
        total_chunks += result["chunks"]
        all_errors.extend(result["errors"])
        processed_sources.append("HRP Handbook")

        logger.info(
            f"HRP Handbook: {result['sections']} sections, {result['chunks']} chunks"
        )

    # Report summary
    logger.info("=" * 50)
    logger.info("Ingestion Summary:")
    logger.info(f"  Sources processed: {processed_sources}")
    logger.info(f"  Total sections: {total_sections}")
    logger.info(f"  Total chunks: {total_chunks}")

    if all_errors:
        logger.warning(f"  Errors ({len(all_errors)}):")
        for error in all_errors[:10]:
            logger.warning(f"    - {error}")
        if len(all_errors) > 10:
            logger.warning(f"    ... and {len(all_errors) - 10} more")

    return 0 if not all_errors else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
