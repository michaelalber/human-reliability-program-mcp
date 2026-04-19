# human-reliability-program-mcp — Project Context

> This is the **project-level** AGENTS.md for OpenCode.
> It supplements the global `~/.config/opencode/AGENTS.md` — it does NOT replace it.
> Global standards (coding style, security rules, quality gates, TDD discipline) live in the global file.
> This file contains only what is specific to THIS project.

---

## Project Overview

- **Name:** human-reliability-program-mcp
- **Purpose:** FastMCP-based MCP server giving AI assistants structured access to 10 CFR Part 712 (DOE/NNSA Human Reliability Program) regulations — certification requirements, medical standards, and procedural guidance.
- **Phase:** Build (Alpha — v0.1.0)
- **Jira project key:** [VERIFY: Jira project key, if tracked]
- **Confluence space:** [VERIFY: Confluence space URL, if tracked]
- **Definition of success:** HRP administrators and certifying officials can answer any 10 CFR Part 712 question through an AI assistant in under 60 seconds, with citations traceable to the public eCFR source.

---

## Technology Stack

- **Language:** Python 3.10 (also tested on 3.11, 3.12)
- **MCP framework:** FastMCP ≥ 0.4.0
- **Vector store:** ChromaDB ≥ 0.4.0 (embedded, no external service)
- **Embeddings:** sentence-transformers ≥ 2.2.0 (`all-MiniLM-L6-v2`)
- **Data models / config:** Pydantic v2 + pydantic-settings (`HRP_*` env vars)
- **HTTP client:** httpx ≥ 0.25.0 (async; used for eCFR API only)
- **Document processing:** docling ≥ 2.0.0, beautifulsoup4 ≥ 4.12.0, defusedxml ≥ 0.7.0
- **Token counting:** tiktoken ≥ 0.5.0
- **Test framework:** pytest + pytest-asyncio (`asyncio_mode = "auto"`) + pytest-cov
- **Linting / formatting:** Ruff (line length 100, rules E W F I N B C4 UP S T20 SIM RUF)
- **Type checking:** mypy strict mode
- **Security scan:** bandit + semgrep + CodeQL + Trivy (in CI)
- **Dependency audit:** pip-audit (weekly CI schedule)
- **CI/CD:** GitHub Actions — `.github/workflows/ci.yml` (lint, type-check, test matrix 3.10–3.12, dep-audit) + `.github/workflows/security.yml` (weekly semgrep/bandit/CodeQL/Trivy)
- **Package manager:** pip / uv (`uv.lock` present); install with `pip install -e ".[dev]"`
- **Container:** Docker Compose (`docker-compose.yml`, `docker-compose.dev.yml`)

---

## Architecture

- **Pattern:** Tool-based vertical slice — each HRP domain (regulations, certification, medical, testing, procedures) is a discrete module under `src/hrp_mcp/tools/`. No cross-tool imports.
- **Entry point:** `src/hrp_mcp/server.py` — FastMCP server, registers all tools, exposes `main()` as `hrp-mcp` CLI entry point.
- **Key directories:**
  - `src/hrp_mcp/tools/` — one file per HRP domain; each file contains all MCP tools for that domain
  - `src/hrp_mcp/services/` — RAG orchestration (`rag.py`), ChromaDB operations (`vector_store.py`), embeddings wrapper (`embeddings.py`)
  - `src/hrp_mcp/models/` — Pydantic data models: `hrp.py` (13 domain classes), `regulations.py` (RegulationChunk, HRPSubpart, SourceType), `errors.py`
  - `src/hrp_mcp/data/ingest/` — ingestion pipeline: `ecfr_ingest.py` (eCFR API), `handbook_ingest.py` (DOE PDF)
  - `src/hrp_mcp/rag/chunking.py` — document chunking strategies
  - `src/hrp_mcp/audit.py` — JSONL audit log; every tool invocation is logged with timestamp, tool name, sanitized parameters, result summary
  - `src/hrp_mcp/config.py` — pydantic-settings; all config via `HRP_*` env vars
  - `tests/` — mirrors `src/` structure: `test_tools/`, `test_services/`, `test_data/`, `test_rag/`
- **Non-obvious constraints:**
  - Transport defaults to `stdio` (Claude Desktop); switch to `streamable-http` via env var — never change the default without discussion.
  - ChromaDB is embedded (no external service). The `data/chroma/` directory is the persisted vector store — do not delete it in tests.
  - All XML parsing MUST use `defusedxml` — never `xml.etree.ElementTree` directly (XXE prevention).
  - Audit log path (`logs/audit.jsonl`) is append-only; never truncate or delete in code paths.
  - `asyncio_mode = "auto"` — no `@pytest.mark.asyncio` decorator needed on test functions.

---

## Key Files

| File | Why It Matters |
|---|---|
| `src/hrp_mcp/server.py` | FastMCP entry point; registers all tools and starts the server |
| `src/hrp_mcp/config.py` | All configuration via pydantic-settings; read this before touching env vars |
| `src/hrp_mcp/audit.py` | JSONL audit logger; every tool call must go through here — do not bypass |
| `src/hrp_mcp/models/hrp.py` | 13 Pydantic domain models — the canonical data contract for all tool outputs |
| `src/hrp_mcp/models/regulations.py` | `RegulationChunk`, `HRPSubpart`, `SourceType` — RAG data types |
| `src/hrp_mcp/services/rag.py` | RAG orchestration layer; search → embed → retrieve → return chunks |
| `src/hrp_mcp/tools/regulations.py` | Most-used tool module; reference pattern for other tool implementations |
| `tests/conftest.py` | Shared pytest fixtures; read before adding new fixtures |

---

## Persistent Decisions

| Date | Decision | Rationale |
|---|---|---|
| 2025-01-11 | Local-first: no external embedding or vector store services | Data privacy — HRP queries may reference personnel-sensitive context; nothing leaves the network |
| 2025-01-11 | FastMCP over raw MCP SDK | FastMCP provides async-native tool registration with less boilerplate |
| 2025-01-11 | ChromaDB embedded (not server mode) | Eliminates an external service dependency for local / Claude Desktop deployment |
| 2025-01-11 | `defusedxml` mandatory for all XML parsing | eCFR delivers XML; XXE attack surface must be eliminated at the library level |
| 2025-01-11 | Structured Pydantic outputs for all tools | Let the LLM format for the user; tools return structured data, not prose |
| 2025-01-11 | `stdio` transport as default; `streamable-http` opt-in via env var | Claude Desktop requires stdio; HTTP is for .NET integration — keep the simpler path as the default |
| 2025-01-11 | Audit log every tool invocation (JSONL, append-only) | Audit-ready posture for federal environment; required even though no PII is stored |
| 2025-01-12 | Bind HTTP transport to `127.0.0.1` only | Prevent accidental external exposure; follows DOE security posture |

---

## Open Loops

- [ ] Handbook ingestion (`handbook_ingest.py`) — DOE handbook PDF not yet ingested; only eCFR XML is in the vector store
- [ ] Snyk integration not yet wired into CI (global CLAUDE.md requires it for new first-party code)
- [ ] [VERIFY: Any in-flight Jira issues or feature work currently in progress?]

---

## Team

| Name | Role | Notes |
|---|---|---|
| Michael K. Alber | Author / Tech Lead | Reviews all PRs; michael.k.alber@gmail.com |
| [VERIFY: additional team members?] | | |

---

## Available Tools

- **grounded-code-mcp** (`search_knowledge`, `search_code_examples`) — authoritative local KB; search `python` collection for FastMCP, Pydantic v2, pytest patterns before writing code
- **Bash** — run tests (`pytest`), linters (`ruff check`, `mypy`), security scan (`bandit -r src/ -c pyproject.toml`)
- **Read / Write / Edit / Grep / Glob** — file operations and code search
- **Skill** — invoke `python-arch-review`, `tdd-cycle`, `python-security-review` skills as needed

---

## Project Boot Ritual

At the start of every session:

1. Read this file (`AGENTS.md`), `intent.md`, and `constraints.md`.
2. Check the active Jira issue (if any) for the current task spec and acceptance criteria.
3. Confirm context — state: current phase, active task (if any), top 3 constraints, open loops.
4. Do NOT begin work until context is confirmed.
