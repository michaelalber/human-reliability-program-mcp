# Human Reliability Program MCP Server

## Project Overview

A FastMCP-based Model Context Protocol server providing AI assistant capabilities for DOE/NNSA Human Reliability Program (HRP) administrators and certifying officials. Enables querying of 10 CFR Part 712 regulations, certification requirements, medical standards, and program procedures.

The Human Reliability Program ensures that individuals with access to Category I special nuclear material (SNM), nuclear explosive devices, or HRP-designated facilities meet stringent reliability, safety, and security standards.

## Tech Stack

- **Runtime**: Python 3.10+
- **Framework**: FastMCP (MCP SDK)
- **Vector Store**: ChromaDB (local, no external dependencies)
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2 for efficiency, or BGE for quality)
- **Document Processing**: pypdf, python-docx, unstructured
- **HTTP Client**: httpx (async)
- **Testing**: pytest, pytest-asyncio
- **Linting**: Ruff (linting + formatting)

## Architecture

```
src/
├── hrp_mcp/
│   ├── __init__.py
│   ├── server.py              # FastMCP server entry point
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── regulations.py     # 10 CFR 712 search tools
│   │   ├── certification.py   # Certification/recertification procedures
│   │   ├── medical.py         # Medical standards (Subpart B)
│   │   ├── testing.py         # Drug/alcohol testing requirements
│   │   └── procedures.py      # Removal, reinstatement, appeals
│   ├── resources/
│   │   ├── __init__.py
│   │   └── reference_docs.py  # Static reference materials
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── embeddings.py      # Embedding generation
│   │   ├── vectorstore.py     # ChromaDB operations
│   │   └── chunking.py        # Document chunking strategies
│   └── config.py              # Settings via pydantic-settings
├── scripts/
│   ├── ingest_regulations.py  # Load 10 CFR 712 into vector store
│   └── update_guidance.py     # Fetch DOE guidance documents
├── data/
│   ├── regulations/           # 10 CFR 712 source documents
│   ├── guidance/              # DOE orders and guidance
│   └── chroma/                # Vector store persistence
└── tests/
    ├── conftest.py
    ├── test_tools/
    └── test_rag/
```

## Key Design Decisions

1. **Local-first**: All inference-adjacent operations (embeddings, vector store) run locally. No data leaves the network unless explicitly configured for external LLM APIs.

2. **Tool-based architecture**: Each HRP function is a discrete MCP tool with clear input/output contracts. Enables granular permissions and audit logging.

3. **Async throughout**: FastMCP is async-native. All I/O operations use async patterns for responsiveness.

4. **Structured outputs**: Tools return structured data (Pydantic models) rather than raw text where possible. Let the LLM format for the user.

5. **Audit-ready**: Every tool invocation logs: timestamp, tool name, parameters (sanitized), user context (if available), result summary.

## MCP Tools to Implement

### Regulation Tools
- `search_10cfr712` - Full-text search of 10 CFR Part 712
- `get_section` - Retrieve specific section (e.g., 712.11, 712.15)
- `get_subpart` - Retrieve full subpart (A: Procedures, B: Medical Standards)
- `explain_term` - HRP glossary/definitions lookup (§712.3)

### Certification Tools
- `get_certification_requirements` - Initial certification requirements (§712.11)
- `get_recertification_requirements` - Annual recertification process (§712.12)
- `check_disqualifying_factors` - Evaluate potential disqualifying conditions
- `get_hrp_position_types` - HRP position categories and access levels (§712.10)

### Medical Standards Tools (Subpart B)
- `get_medical_standards` - Medical assessment requirements (§712.30-712.38)
- `get_psychological_evaluation` - Psychological evaluation criteria
- `check_medical_condition` - Evaluate condition against HRP standards
- `get_doe_physician_role` - Designated Physician responsibilities

### Testing Tools
- `get_drug_testing_requirements` - Drug testing procedures (§712.15)
- `get_alcohol_testing_requirements` - Alcohol testing procedures
- `get_testing_frequency` - Random testing intervals and triggers
- `get_substance_list` - Controlled substances tested

### Procedural Tools
- `get_temporary_removal_process` - Temporary removal procedures (§712.19)
- `get_permanent_removal_process` - Permanent removal/revocation (§712.20)
- `get_reinstatement_process` - Reinstatement after removal (§712.21)
- `get_appeal_process` - Administrative review procedures (§712.22-712.25)

### Administrative Tools
- `get_hrp_roles` - HRP official roles (Manager, Certifying Official, etc.)
- `get_supervisory_review` - Supervisory review requirements (§712.14)
- `get_management_evaluation` - Management evaluation process (§712.16)
- `get_security_review` - DOE personnel security review requirements (§712.17)

## Environment Variables

```bash
# Required
HRP_CHROMA_PERSIST_DIR=./data/chroma

# MCP Transport (stdio, streamable-http, or sse)
HRP_MCP_TRANSPORT=stdio          # Default: stdio for Claude Desktop
HRP_MCP_HOST=127.0.0.1           # Host for HTTP transports
HRP_MCP_PORT=8000                # Port for HTTP transports

# Optional - for external LLM (if not using local)
OPENAI_API_KEY=                  # If using OpenAI embeddings
ANTHROPIC_API_KEY=               # If calling Claude from tools

# Logging
HRP_LOG_LEVEL=INFO
HRP_AUDIT_LOG_PATH=./logs/audit.jsonl
```

## Development Commands

```bash
# Create virtual environment (Python 3.10+)
python3.10 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -e ".[dev]"

# Run MCP server (stdio mode for Claude Desktop)
python -m hrp_mcp.server

# Run with Streamable HTTP for web integration
HRP_MCP_TRANSPORT=streamable-http python -m hrp_mcp.server

# Ingest regulations from eCFR
python scripts/ingest_regulations.py --download

# Run tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=term-missing

# Lint
ruff check src/ tests/

# Lint and auto-fix
ruff check --fix src/ tests/

# Format code
ruff format src/ tests/

# Type checking
mypy src/
```

## Docker Deployment

```bash
# Build Docker image
docker build -t hrp-mcp .

# Run with Docker Compose (HTTP transport)
docker-compose up -d

# Run standalone (stdio transport)
docker run --rm -it hrp-mcp

# View logs
docker-compose logs -f
```

## Security Considerations

- This server handles sensitive personnel reliability information. Deploy only on approved DOE/NNSA networks.
- Audit logging is mandatory for production use per DOE Order requirements.
- Vector store contains regulation and guidance text only—no PII or individual HRP records.
- All access should comply with site-specific HRP implementation procedures.
- Consult with ISSM/ISSO before deployment on any classified or controlled network.

## Integration Points

### Claude Desktop (Local Development)
```json
{
  "mcpServers": {
    "hrp": {
      "command": "/path/to/human-reliability-program-mcp/.venv/bin/python",
      "args": ["-m", "hrp_mcp.server"],
      "cwd": "/path/to/human-reliability-program-mcp"
    }
  }
}
```

### .NET Application (Production)
- Connect via Streamable HTTP transport to `http://localhost:8000/mcp`
- Use MCP C# SDK or HTTP client with streaming support
- Pass user context in MCP request metadata for audit logging

## Key HRP Concepts

### Four Annual Components
1. **Supervisory Review** (§712.14) - Ongoing behavioral observation
2. **Medical Assessment** (§712.13) - Physical and psychological evaluation
3. **Management Evaluation** (§712.16) - Holistic reliability determination
4. **DOE Security Review** (§712.17) - Personnel security determination

### HRP Positions (§712.10)
- Access to Category I SNM
- Access to nuclear explosive devices
- Nuclear explosive duties
- HRP-designated positions with significant national security impact

### Disqualifying Factors
- Hallucinogen use within past 5 years
- Failure of drug/alcohol tests
- Significant medical/psychological conditions
- Security concerns from personnel review

## References

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [MCP Specification](https://modelcontextprotocol.io)
- [10 CFR Part 712 - Human Reliability Program](https://www.ecfr.gov/current/title-10/chapter-III/part-712)
- [10 CFR Part 712 (Cornell LII)](https://www.law.cornell.edu/cfr/text/10/part-712)
- [DOE HRP Information Collection](https://www.energy.gov/ehss/omb-1910-5122-human-reliability-program-description-collections)
- [10 CFR 712 PDF (2024)](https://www.govinfo.gov/content/pkg/CFR-2024-title10-vol4/pdf/CFR-2024-title10-vol4-part712.pdf)
