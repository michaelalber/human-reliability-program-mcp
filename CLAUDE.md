# Human Reliability Program MCP Server

## Project Overview

A FastMCP-based Model Context Protocol server providing AI assistant capabilities for DOE/NNSA Human Reliability Program (HRP) administrators and certifying officials. Enables querying of 10 CFR Part 712 regulations, certification requirements, medical standards, and program procedures.

**Key design decisions:**
- **Local-first**: Embeddings and vector store run locally. No data leaves the network.
- **Tool-based architecture**: Each HRP function is a discrete MCP tool with clear contracts. Enables granular permissions and audit logging.
- **Async throughout**: FastMCP is async-native. All I/O uses async patterns.
- **Structured outputs**: Tools return Pydantic models. Let the LLM format for the user.
- **Audit-ready**: Every tool invocation logs timestamp, tool name, sanitized parameters, and result summary.

## Tech Stack

| Component | Choice |
|-----------|--------|
| MCP Framework | FastMCP (>=0.4.0) |
| Vector Store | ChromaDB (embedded, no external service) |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Data Models | Pydantic 2.0+ |
| Config | pydantic-settings (HRP_* env vars) |
| HTTP Client | httpx (async, for eCFR API) |
| Document Processing | docling, beautifulsoup4, lxml, defusedxml |
| Token Counting | tiktoken (chunking) |
| Testing | pytest, pytest-asyncio, pytest-cov |
| Linting | Ruff (linting + formatting) |
| Type Checking | mypy (strict) |
| Security | bandit |

## Architecture

```
src/hrp_mcp/
├── __init__.py
├── server.py              # FastMCP server entry point
├── config.py              # Settings via pydantic-settings
├── audit.py               # JSONL audit logging
├── models/
│   ├── errors.py          # Custom exceptions
│   ├── hrp.py             # HRP data models (13 Pydantic classes)
│   └── regulations.py     # RegulationChunk, HRPSubpart, SourceType
├── services/
│   ├── embeddings.py      # sentence-transformers wrapper
│   ├── vector_store.py    # ChromaDB operations
│   └── rag.py             # RAG orchestration
├── tools/
│   ├── regulations.py     # 10 CFR 712 search tools
│   ├── certification.py   # Certification/recertification
│   ├── medical.py         # Medical standards (Subpart B)
│   ├── testing.py         # Drug/alcohol testing
│   └── procedures.py      # Removal, reinstatement, appeals
├── resources/
│   └── reference_data.py  # Static HRP sections, definitions
├── rag/
│   └── chunking.py        # Document chunking strategies
└── data/ingest/
    ├── base.py            # Abstract base ingestor
    ├── ecfr_ingest.py     # eCFR data ingestion
    └── handbook_ingest.py # DOE handbook ingestion
```

## Commands

```bash
# Setup
pip install -e ".[dev]"

# Run server (stdio - default for Claude Desktop)
hrp-mcp

# Run server (HTTP)
HRP_MCP_TRANSPORT=streamable-http hrp-mcp

# Test
pytest
pytest --cov=src/hrp_mcp --cov-report=term-missing

# Lint
ruff check src/ tests/
ruff format --check src/ tests/

# Type check
mypy src/

# Security scan
bandit -r src/ -c pyproject.toml

# Data ingestion
python scripts/ingest_regulations.py --download

# Docker
docker compose up -d
docker compose logs -f
docker compose down
```

## Development Principles

### TDD is Mandatory
1. **Never write production code without a failing test first**
2. Cycle: RED (write failing test) → GREEN (minimal code to pass) → REFACTOR
3. Run tests before committing: `pytest`
4. Coverage target: 80% minimum for business logic, 95% for security-critical code

### Security-By-Design
- Validate all inputs at system boundaries
- Use defusedxml for all XML parsing (prevents XXE attacks)
- Use structured Pydantic models for all MCP tool inputs and outputs
- Sanitize search parameters — redact PII fields (SSN, DOB, passwords, tokens) in audit logs
- Treat tool queries as potentially containing personnel-sensitive information
- Audit log all tool invocations with correlation IDs
- Bind HTTP transport to `127.0.0.1` by default
- Never include secrets in source code — use environment variables
- All rules align with [OWASP Top 10 (2025)](https://owasp.org/Top10/2025/) guidance

### YAGNI (You Aren't Gonna Need It)
- Start with direct implementations
- Add abstractions only when complexity demands it
- Create interfaces only when multiple implementations exist
- No dependency injection containers
- Prefer composition over inheritance

## Code Standards

- Type hints on all signatures
- Google-style docstrings for public methods
- Arrange-Act-Assert test pattern
- `pathlib.Path` over string paths
- Specific exceptions, never bare `except:`
- Async for I/O-bound operations
- Pydantic models for all data structures

## Quality Gates

- **Cyclomatic Complexity**: Methods <10, classes <20
- **Code Coverage**: 80% minimum for business logic, 95% for security-critical code
- **Maintainability Index**: Target 70+
- **Code Duplication**: Maximum 3%

## Git Workflow

- Commit after each GREEN phase
- Commit message format: `feat|fix|test|refactor: brief description`
- Don't commit failing tests (RED phase is local only)

## Testing Patterns

```python
# Arrange-Act-Assert pattern
@pytest.mark.asyncio
async def test_search_returns_regulation_chunks():
    # Arrange
    service = RagService()

    # Act
    results = await service.search("certification requirements", limit=5)

    # Assert
    assert len(results) > 0
    assert "712" in results[0].cfr_reference
```

### Test Categories

- `tests/test_tools/` - Tool implementation tests
- `tests/test_services/` - Service layer tests
- `tests/test_data/` - Ingestion pipeline tests
- `tests/test_rag/` - RAG/chunking tests

## MCP Tools

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

| Variable | Default | Description |
|----------|---------|-------------|
| `HRP_MCP_TRANSPORT` | `stdio` | Transport: `stdio` or `streamable-http` |
| `HRP_MCP_HOST` | `127.0.0.1` | HTTP server host |
| `HRP_MCP_PORT` | `8000` | HTTP server port |
| `HRP_EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence transformer model |
| `HRP_CHROMA_PERSIST_DIR` | `./data/chroma` | ChromaDB storage |
| `HRP_LOG_LEVEL` | `INFO` | Logging level |
| `HRP_AUDIT_LOG_PATH` | `./logs/audit.jsonl` | Audit log location |

## Integration Points

### Claude Desktop (Local)
```json
{
  "mcpServers": {
    "hrp": {
      "command": "hrp-mcp"
    }
  }
}
```

### .NET Application (Production)
- Connect via Streamable HTTP transport to `http://localhost:8000/mcp`
- Use MCP C# SDK or HTTP client with streaming support
- Pass user context in MCP request metadata for audit logging

## Security Considerations

- This server provides access to **publicly available** 10 CFR Part 712 regulations from eCFR.
- No sensitive personnel data, PII, or individual HRP records are stored or processed.
- Vector store contains only public regulatory text.
- Audit logging is available for tracking tool usage if needed.

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
