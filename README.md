# Human Reliability Program MCP Server

[![CI](https://github.com/michaelalber/human-reliability-program-mcp/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/michaelalber/human-reliability-program-mcp/actions/workflows/ci.yml)
[![Security](https://github.com/michaelalber/human-reliability-program-mcp/actions/workflows/security.yml/badge.svg?branch=main)](https://github.com/michaelalber/human-reliability-program-mcp/actions/workflows/security.yml)

MCP server providing AI assistant tools for DOE/NNSA Human Reliability Program (10 CFR Part 712) administration.

## Features

### Regulation Tools
- `search_10cfr712` - Full-text search of 10 CFR Part 712
- `get_section` - Retrieve specific section (e.g., 712.11, 712.15)
- `get_subpart` - Retrieve full subpart (A: Procedures, B: Medical Standards)
- `explain_term` - HRP glossary/definitions lookup (712.3)

### Certification Tools
- `get_certification_requirements` - Initial certification requirements (712.11)
- `get_recertification_requirements` - Annual recertification process (712.12)
- `check_disqualifying_factors` - Evaluate potential disqualifying conditions
- `get_hrp_position_types` - HRP position categories and access levels (712.10)

### Medical Standards Tools (Subpart B)
- `get_medical_standards` - Medical assessment requirements (712.30-712.38)
- `get_psychological_evaluation` - Psychological evaluation criteria
- `check_medical_condition` - Evaluate condition against HRP standards
- `get_doe_physician_role` - Designated Physician responsibilities

### Testing Tools
- `get_drug_testing_requirements` - Drug testing procedures (712.15)
- `get_alcohol_testing_requirements` - Alcohol testing procedures
- `get_testing_frequency` - Random testing intervals and triggers
- `get_substance_list` - Controlled substances tested

### Procedural Tools
- `get_temporary_removal_process` - Temporary removal procedures (712.19)
- `get_permanent_removal_process` - Permanent removal/revocation (712.20)
- `get_reinstatement_process` - Reinstatement after removal (712.21)
- `get_appeal_process` - Administrative review procedures (712.22-712.25)

## Quick Start

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install
pip install -e .

# Ingest regulations
python scripts/ingest_regulations.py --download

# Run server (stdio transport)
hrp-mcp

# Run server (HTTP transport)
HRP_MCP_TRANSPORT=streamable-http hrp-mcp
```

### Using Docker

```bash
docker compose up -d
```

The server will be available at `http://localhost:8000`.

## Data Source

Regulations are sourced from the public [eCFR](https://www.ecfr.gov/current/title-10/chapter-III/part-712).

## Configuration

Environment variables (prefix: `HRP_`):

| Variable | Default | Description |
|----------|---------|-------------|
| `HRP_MCP_TRANSPORT` | `stdio` | Transport: `stdio` or `streamable-http` |
| `HRP_MCP_HOST` | `127.0.0.1` | HTTP server host |
| `HRP_MCP_PORT` | `8000` | HTTP server port |
| `HRP_EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence transformer model |
| `HRP_CHROMA_PERSIST_DIR` | `./data/chroma` | ChromaDB storage |
| `HRP_LOG_LEVEL` | `INFO` | Logging level |
| `HRP_AUDIT_LOG_PATH` | `./logs/audit.jsonl` | Audit log location |

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check src/ tests/

# Type check
mypy src/
```

See [CLAUDE.md](CLAUDE.md) for architecture documentation.

## Security Notes

- This server provides access to publicly available 10 CFR Part 712 regulations
- No sensitive personnel data, PII, or individual HRP records are stored or processed
- Vector store contains only public regulatory text
- Audit logging available for tracking tool usage

## Author

Michael K Alber ([@michaelalber](https://github.com/michaelalber))

## License

Apache License 2.0 - see [LICENSE](LICENSE)
