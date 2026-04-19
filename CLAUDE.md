# human-reliability-program-mcp — Project Context

> This is the **project-level** CLAUDE.md for Claude Code.
> It supplements the global `~/.claude/CLAUDE.md` — it does NOT replace it.
> Global standards (TDD, Python coding style, security rules, quality gates) live in the global file.
> This file contains only what is specific to THIS project.

---

## Project Overview

- **Name:** human-reliability-program-mcp
- **Purpose:** FastMCP-based MCP server giving AI assistants structured access to 10 CFR Part 712 (DOE/NNSA Human Reliability Program) regulations — certification requirements, medical standards, and procedural guidance.
- **Phase:** Build (Alpha — v0.1.0)
- **Definition of success:** HRP administrators and certifying officials can answer any 10 CFR Part 712 question through an AI assistant, with responses grounded in citations traceable to the public eCFR source.

---

## Technology Stack

| Component | Choice |
|---|---|
| Language | Python 3.10 (also tested 3.11, 3.12) |
| MCP Framework | FastMCP ≥ 0.4.0 |
| Vector Store | ChromaDB ≥ 0.4.0 (embedded, no external service) |
| Embeddings | sentence-transformers ≥ 2.2.0 (`all-MiniLM-L6-v2`) |
| Data Models / Config | Pydantic v2 + pydantic-settings (`HRP_*` env vars) |
| HTTP Client | httpx ≥ 0.25.0 (async; eCFR API only) |
| Document Processing | docling ≥ 2.0.0, beautifulsoup4, defusedxml ≥ 0.7.0 |
| Token Counting | tiktoken ≥ 0.5.0 |
| Test Framework | pytest + pytest-asyncio (`asyncio_mode = "auto"`) + pytest-cov |
| Lint / Format | Ruff (line length 100) |
| Type Checking | mypy strict mode |
| Security Scan | bandit + semgrep + CodeQL + Trivy (CI) |
| Dependency Audit | pip-audit (weekly CI schedule) |
| CI/CD | GitHub Actions — `.github/workflows/ci.yml` + `.github/workflows/security.yml` |
| Package Manager | pip / uv (`uv.lock` present) |
| Container | Docker Compose (`docker-compose.yml`, `docker-compose.dev.yml`) |

---

## Architecture

```
src/hrp_mcp/
├── server.py              # FastMCP entry point; registers all tools; exports main()
├── config.py              # pydantic-settings; all config via HRP_* env vars
├── audit.py               # JSONL audit log; every tool invocation must route through here
├── models/
│   ├── hrp.py             # 13 HRP Pydantic domain classes
│   ├── regulations.py     # RegulationChunk, HRPSubpart, SourceType
│   └── errors.py          # Typed HRP exceptions
├── services/
│   ├── rag.py             # RAG orchestration (search → embed → retrieve)
│   ├── vector_store.py    # ChromaDB operations
│   └── embeddings.py      # sentence-transformers wrapper
├── tools/
│   ├── regulations.py     # search_10cfr712, get_section, get_subpart, explain_term
│   ├── certification.py   # get_certification_requirements, get_recertification_requirements, …
│   ├── medical.py         # get_medical_standards, get_psychological_evaluation, …
│   ├── testing.py         # get_drug_testing_requirements, get_alcohol_testing_requirements, …
│   └── procedures.py      # get_temporary_removal_process, get_appeal_process, …
├── resources/
│   └── reference_data.py  # Static HRP sections, definitions
├── rag/
│   └── chunking.py        # Document chunking strategies
└── data/ingest/
    ├── ecfr_ingest.py     # eCFR XML ingestion (httpx → defusedxml → ChromaDB)
    └── handbook_ingest.py # DOE handbook PDF ingestion (docling)
```

**Non-obvious constraints:**
- Transport defaults to `stdio` (Claude Desktop). Switching to `streamable-http` is via env var only — never change the code default without discussion.
- ChromaDB is embedded. `data/chroma/` is the persisted vector store — never delete it in test code.
- All XML parsing MUST use `defusedxml` — never `xml.etree.ElementTree` directly.
- Audit log (`logs/audit.jsonl`) is append-only; never truncate or delete in any code path.
- `asyncio_mode = "auto"` in pytest — no `@pytest.mark.asyncio` decorator needed.

---

## Commands

```bash
# Install
pip install -e ".[dev]"

# Run server (stdio — default for Claude Desktop)
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

---

## Key Files

| File | Why It Matters |
|---|---|
| `src/hrp_mcp/server.py` | FastMCP entry point; registers all tools and starts the server |
| `src/hrp_mcp/config.py` | All configuration via pydantic-settings; read before touching env vars |
| `src/hrp_mcp/audit.py` | JSONL audit logger; every tool call must go through here — do not bypass |
| `src/hrp_mcp/models/hrp.py` | 13 Pydantic domain models — the canonical data contract for all tool outputs |
| `src/hrp_mcp/models/regulations.py` | `RegulationChunk`, `HRPSubpart`, `SourceType` — RAG data types |
| `src/hrp_mcp/services/rag.py` | RAG orchestration layer; search → embed → retrieve → return chunks |
| `src/hrp_mcp/tools/regulations.py` | Most-used tool module; reference pattern for implementing other tools |
| `tests/conftest.py` | Shared pytest fixtures; read before adding new fixtures |

---

## Project-Specific Security Rules

These extend (do not replace) the global security rules:

- Use `defusedxml` for all XML parsing — never `xml.etree.ElementTree` (XXE prevention)
- Use structured Pydantic models for all MCP tool inputs and outputs — never raw `str` or `dict`
- Sanitize search parameters — redact PII fields (SSN, DOB, passwords, tokens) in audit logs
- Treat all tool query strings as potentially containing personnel-sensitive information
- Audit log every tool invocation with correlation ID — including error paths
- Bind HTTP transport to `127.0.0.1` by default; never `0.0.0.0` without explicit approval
- No PII, personnel records, or individual HRP data is stored or processed — regulatory text only

---

## MCP Tools

### Regulation Tools (`src/hrp_mcp/tools/regulations.py`)
- `search_10cfr712` — Full-text RAG search of 10 CFR Part 712
- `get_section` — Retrieve specific section (e.g., `712.11`, `712.15`)
- `get_subpart` — Retrieve full subpart (A: Procedures, B: Medical Standards)
- `explain_term` — HRP glossary/definitions lookup (§712.3)

### Certification Tools (`src/hrp_mcp/tools/certification.py`)
- `get_certification_requirements` — Initial certification requirements (§712.11)
- `get_recertification_requirements` — Annual recertification process (§712.12)
- `check_disqualifying_factors` — Evaluate potential disqualifying conditions
- `get_hrp_position_types` — HRP position categories and access levels (§712.10)

### Medical Standards Tools (`src/hrp_mcp/tools/medical.py`)
- `get_medical_standards` — Medical assessment requirements (§712.30–712.38)
- `get_psychological_evaluation` — Psychological evaluation criteria
- `check_medical_condition` — Evaluate condition against HRP standards
- `get_doe_physician_role` — Designated Physician responsibilities

### Testing Tools (`src/hrp_mcp/tools/testing.py`)
- `get_drug_testing_requirements` — Drug testing procedures (§712.15)
- `get_alcohol_testing_requirements` — Alcohol testing procedures
- `get_testing_frequency` — Random testing intervals and triggers
- `get_substance_list` — Controlled substances tested

### Procedural Tools (`src/hrp_mcp/tools/procedures.py`)
- `get_temporary_removal_process` — Temporary removal procedures (§712.19)
- `get_permanent_removal_process` — Permanent removal/revocation (§712.20)
- `get_reinstatement_process` — Reinstatement after removal (§712.21)
- `get_appeal_process` — Administrative review procedures (§712.22–712.25)

### Administrative Tools (distributed across tool modules)
- `get_hrp_roles` — HRP official roles (Manager, Certifying Official, etc.)
- `get_supervisory_review` — Supervisory review requirements (§712.14)
- `get_management_evaluation` — Management evaluation process (§712.16)
- `get_security_review` — DOE personnel security review requirements (§712.17)

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `HRP_MCP_TRANSPORT` | `stdio` | Transport: `stdio` or `streamable-http` |
| `HRP_MCP_HOST` | `127.0.0.1` | HTTP server host |
| `HRP_MCP_PORT` | `8000` | HTTP server port |
| `HRP_EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence transformer model |
| `HRP_CHROMA_PERSIST_DIR` | `./data/chroma` | ChromaDB storage path |
| `HRP_LOG_LEVEL` | `INFO` | Logging level |
| `HRP_AUDIT_LOG_PATH` | `./logs/audit.jsonl` | Audit log location |

---

## Integration Points

### Claude Desktop (Local — stdio)
```json
{
  "mcpServers": {
    "hrp": {
      "command": "hrp-mcp"
    }
  }
}
```

### .NET Application (HTTP — streamable-http)
- Connect to `http://localhost:8000/mcp` via MCP C# SDK or streaming HTTP client
- Pass user context in MCP request metadata for audit correlation

---

## Key HRP Domain Concepts

### Four Annual Components
1. **Supervisory Review** (§712.14) — Ongoing behavioral observation
2. **Medical Assessment** (§712.13) — Physical and psychological evaluation
3. **Management Evaluation** (§712.16) — Holistic reliability determination
4. **DOE Security Review** (§712.17) — Personnel security determination

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

---

## Available Tools (MCP)

- `mcp__grounded-code-mcp__search_knowledge` — search `python` collection for FastMCP, Pydantic v2, pytest patterns before writing code; search `gov` collection for NIST / DOE compliance context
- `mcp__grounded-code-mcp__search_code_examples` — find code examples in `python` language for FastMCP and async patterns

---

## Persistent Decisions

| Date | Decision | Rationale |
|---|---|---|
| 2025-01-11 | Local-first: no external embedding or vector store services | Data privacy — HRP queries may reference personnel-sensitive context; nothing leaves the network |
| 2025-01-11 | FastMCP over raw MCP SDK | Async-native tool registration with less boilerplate |
| 2025-01-11 | ChromaDB embedded (not server mode) | Eliminates external service dependency for local / Claude Desktop deployment |
| 2025-01-11 | `defusedxml` mandatory for all XML parsing | eCFR delivers XML; XXE attack surface eliminated at library level |
| 2025-01-11 | Structured Pydantic outputs for all tools | Tools return data; LLM formats for the user — separation of concerns |
| 2025-01-11 | `stdio` transport as default; `streamable-http` opt-in via env var | Claude Desktop requires stdio; HTTP is for .NET integration |
| 2025-01-11 | Audit log every tool invocation (JSONL, append-only) | Audit-ready posture for federal environment |
| 2025-01-12 | Bind HTTP transport to `127.0.0.1` only | Prevent accidental external exposure |

---

## Open Loops

- [ ] Handbook ingestion (`handbook_ingest.py`) — DOE handbook PDF not yet ingested; only eCFR XML is in the vector store
- [ ] Snyk integration not yet wired into CI (global CLAUDE.md requires it for new first-party code)

---

## Project Boot Ritual

At the start of every session:

1. Read this file (`CLAUDE.md`), `intent.md`, and `constraints.md`.
2. Confirm context — state: current phase, active task (if any), top 3 constraints, open loops.
3. Do NOT begin work until context is confirmed.

---

## References

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [MCP Specification](https://modelcontextprotocol.io)
- [10 CFR Part 712 — eCFR](https://www.ecfr.gov/current/title-10/chapter-III/part-712)
- [10 CFR Part 712 — Cornell LII](https://www.law.cornell.edu/cfr/text/10/part-712)
- [DOE HRP Information Collection](https://www.energy.gov/ehss/omb-1910-5122-human-reliability-program-description-collections)
- [10 CFR 712 PDF (2024)](https://www.govinfo.gov/content/pkg/CFR-2024-title10-vol4/pdf/CFR-2024-title10-vol4-part712.pdf)
