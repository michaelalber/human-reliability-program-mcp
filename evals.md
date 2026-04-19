# human-reliability-program-mcp — Evals

---

## Eval Philosophy

Evals are not a finishing step — they are **safety infrastructure**. Write them before the agent starts. Run them after every model update or significant prompt change. A passing test suite ≠ done; tests verify code correctness, evals verify output is actually good relative to project intent.

A passing eval is measurable, repeatable, and would survive scrutiny from an HRP certifying official who needs accurate 10 CFR Part 712 guidance.

Evals answer: *"Is the output actually good?"* — not *"does it look reasonable?"*

---

## Test Cases

### Test Case 1: Regulation Search Tool Implementation

- **Input / Prompt:** "Implement `search_10cfr712` — full-text search across 10 CFR Part 712 returning ranked `RegulationChunk` results with CFR citations."
- **Known-Good Output:** A tool function in `src/hrp_mcp/tools/regulations.py` that accepts a `query: str` and `limit: int`, calls `RagService.search()`, routes through `audit.py`, and returns a list of `RegulationChunk` Pydantic models with populated `cfr_reference` fields.
- **Pass Criteria:**
  - [ ] `pytest tests/test_tools/test_regulations.py` — all tests pass
  - [ ] Every result has a non-empty `cfr_reference` field matching pattern `§712.\d+`
  - [ ] Tool invocation appears in `logs/audit.jsonl` with `tool_name`, `timestamp`, and sanitized parameters
  - [ ] `ruff check src/` — zero new issues
  - [ ] `mypy src/` — zero new errors
  - [ ] No `xml.etree.ElementTree` import introduced
- **Last Run:** — | **Result:** —
- **Notes:** —

---

### Test Case 2: Section Retrieval Tool

- **Input / Prompt:** "Implement `get_section` — retrieve a specific 10 CFR Part 712 section by reference (e.g., `712.11`, `712.15`) returning the full section text and metadata."
- **Known-Good Output:** A tool that accepts `section: str`, validates the format, looks up via vector store or static reference data, routes through audit, and returns a `RegulationChunk` or raises a typed `HRPError` (not a bare exception) when the section is not found.
- **Pass Criteria:**
  - [ ] `get_section("712.11")` returns a result with `cfr_reference` containing `712.11`
  - [ ] `get_section("999.99")` raises `HRPError` with a descriptive message — not a 500 / unhandled exception
  - [ ] `pytest tests/test_tools/test_regulations.py` — all tests pass
  - [ ] Audit log entry created for both success and error cases
  - [ ] `ruff check src/ tests/` and `mypy src/` — clean
- **Last Run:** — | **Result:** —
- **Notes:** —

---

### Test Case 3: Certification Requirements Query

- **Input / Prompt:** "Implement `get_certification_requirements` — return the initial HRP certification requirements from §712.11 as a structured `CertificationRequirement` Pydantic model."
- **Known-Good Output:** Tool returns a populated `CertificationRequirement` model with all §712.11 fields. The data matches the public eCFR text — no invented or paraphrased requirements. CFR citation is present.
- **Pass Criteria:**
  - [ ] `pytest tests/test_tools/test_certification.py` — all tests pass
  - [ ] Returned model includes `cfr_reference = "§712.11"` (or equivalent)
  - [ ] No regulatory text is fabricated — all content traceable to ingested eCFR source
  - [ ] `bandit -r src/ -c pyproject.toml` — zero new high/critical issues
  - [ ] Audit log entry present
- **Last Run:** — | **Result:** —
- **Notes:** —

---

### Test Case 4: New Tool Added Without Bypassing Audit

- **Input / Prompt:** Any request to add a new MCP tool to any tool module.
- **Known-Good Output:** The new tool function calls `audit_log(...)` before returning — not an afterthought, not skipped on error paths.
- **Pass Criteria:**
  - [ ] `grep -r "audit_log\|audit\.log" src/hrp_mcp/tools/` — every tool file has at least one audit call
  - [ ] Error path also logs to audit (audit entry created even when the tool raises)
  - [ ] `pytest` — all tests pass including any new test for the new tool
- **Last Run:** — | **Result:** —
- **Notes:** Pattern to enforce: audit call must appear inside every tool function, not just in the success branch.

---

## Taste Rules (Encoded Rejections)

| # | Pattern to Reject | Why It Fails | Rule |
|---|---|---|---|
| 1 | MCP tool returns a prose string instead of a Pydantic model | Bypasses structured contract; LLM can't reliably extract fields; breaks .NET integration | Tools always return Pydantic models — never `str` or `dict` |
| 2 | Regulatory text included in tool output without a `cfr_reference` field | Unverifiable; could be hallucinated; creates liability | Every regulatory result must carry a `cfr_reference` traceable to the ingested eCFR source |
| 3 | `import xml.etree.ElementTree` anywhere in `src/` | XXE attack surface; violates a Persistent Decision | Always `import defusedxml.ElementTree as ET` |
| 4 | Tool function that doesn't call `audit.py` on every code path | Silent invocations violate the audit-ready posture required for a federal environment | Audit call must be unconditional — wrap in try/finally if needed |
| 5 | Test file created after the production file | Violates TDD discipline (global rule); caught in PR review | Write the failing test first, then the implementation |

---

## CI Gate

The CI pipeline result is a first-class eval input. The agent must not declare a task complete if any gate below fails.

- **Lint:** `ruff check src/ tests/` — zero issues
- **Format check:** `ruff format --check src/ tests/` — clean
- **Type check:** `mypy src/` — zero errors
- **Tests:** `pytest --cov=src/hrp_mcp --cov-report=term-missing` — all pass, ≥ 80% coverage
- **Dependency audit:** `pip-audit --skip-editable --desc on --ignore-vuln CVE-2025-69872` — zero new vulnerabilities
- **Security — Bandit:** `bandit -r src/ -c pyproject.toml` — zero high or critical issues
- **Security — Semgrep:** `semgrep scan --config p/python --error src/` — zero errors
- **Security — Trivy:** filesystem scan, CRITICAL/HIGH severity — zero findings

> Append CI gate results as a sub-item of each Test Case entry on every run.

---

## Rejection Log

> Running log of rejected outputs. Review weekly to extract new Taste Rules above.
> Never delete entries — they are the institutional memory of what "wrong" looks like.

*(No entries yet — add here when outputs are rejected.)*
