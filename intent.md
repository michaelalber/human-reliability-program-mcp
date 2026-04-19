# human-reliability-program-mcp — Intent

---

## Agent Architecture

**This project uses:** Coding harness

**Reason:** Single-developer, human-in-the-loop project; each feature is implemented task-by-task with the human reviewing before merge — no need for autonomous multi-session dark factory operation.

---

## Primary Goal

Enable DOE/NNSA Human Reliability Program administrators and certifying officials to answer any 10 CFR Part 712 question — certification requirements, medical standards, drug/alcohol testing procedures, removal and reinstatement processes — through an AI assistant, with responses grounded in citations to the public eCFR source and delivered in under 60 seconds.

[VERIFY: Is the "60 seconds" target accurate? Revise if there is a different SLA.]

---

## Values (What We Optimize For)

1. **Correctness** — regulatory citations must be accurate; a wrong answer in an HRP context has real personnel consequences
2. **Security** — local-first data handling; no PII or personnel data leaves the network; all tool invocations audited
3. **Maintainability** — code must be readable by a future engineer unfamiliar with HRP domain
4. **Performance** — embedding search and tool response must feel fast enough for interactive use
5. **Speed of delivery** — important but never at the cost of the four above

---

## Tradeoff Rules

| Conflict | Resolution |
|---|---|
| Speed vs. correctness | Correctness. Flag explicitly if timeline requires compromise. |
| Completeness vs. brevity | Brevity unless depth is explicitly requested. |
| Adding a new tool vs. expanding an existing one | Prefer a new discrete tool — tools are the unit of permission and audit; don't conflate concerns |
| Local model accuracy vs. a larger external model | Always local; accuracy tradeoff is acceptable — the constraint is non-negotiable |
| Structured output vs. formatted prose in tool return | Always structured (Pydantic model); let the LLM format for the user |
| Covering an edge case in code vs. deferring to a `[VERIFY:]` comment | Write the `[VERIFY:]` comment — do not invent HRP regulatory details |

---

## Decision Boundaries

### Decide Autonomously

- Formatting, structure, naming within established Python and project conventions
- Tool selection for read-only exploration (Grep, Glob, Read)
- Refactoring within an approved, scoped task
- Adding a `[VERIFY:]` comment rather than guessing a regulatory fact or function signature
- Choosing between equivalent Pydantic field types when both are valid

### Escalate to Human

- Any output intended for external distribution (regulatory guidance documents, emails, stakeholder reports)
- Any irreversible action (delete vector store data, force-push, deploy to production)
- Any request that contradicts a logged Persistent Decision in `AGENTS.md`
- Scope changes beyond the stated task
- When acceptance criteria cannot be met within stated constraints
- Any change to the audit logging path or format — audit integrity is non-negotiable
- Adding a new external network dependency (the local-first constraint is a Persistent Decision)
- Modifying the default transport from `stdio` — this affects Claude Desktop integration

---

## What "Good" Looks Like

A good output for this project:

- Returns structured Pydantic data with a direct CFR citation (e.g., `§712.11(a)(3)`) — not vague prose
- Passes `pytest`, `ruff check`, `mypy src/`, and `bandit -r src/ -c pyproject.toml` with zero new issues
- Follows the existing tool pattern in `src/hrp_mcp/tools/regulations.py` — new tools are shaped the same way
- Every tool invocation routes through `audit.py` — no tool bypasses the audit log
- Uses `defusedxml` for any XML parsing, never `xml.etree.ElementTree` directly
- Test added before or alongside production code; test file exists before the implementation file

---

## Anti-Patterns (What Bad Looks Like)

- Returning prose summaries from MCP tools instead of structured Pydantic models — the LLM formats, the tool returns data
- Inventing or paraphrasing regulatory text without a direct CFR citation — hallucinated HRP guidance is a liability
- Adding an `import xml.etree.ElementTree` anywhere in `src/` — always `defusedxml`
- Writing a tool that skips the audit log — any tool invocation not in `logs/audit.jsonl` is a compliance gap
- Using `.Result` or `.Wait()` on async methods — async is end-to-end; no sync blocking
- Marking a task complete without running the full test suite

---

## Persistent Decisions

| Date | Decision | Rationale |
|---|---|---|
| 2025-01-11 | Coding harness architecture (not dark factory) | Single developer; human reviews every output before merge |
| 2025-01-11 | Local-first: all embeddings and vector store run locally | HRP queries may reference personnel-sensitive context; data must not leave the network |
| 2025-01-11 | Structured Pydantic outputs for all MCP tools | Separation of concerns: tools return data, LLM formats for the user |

---

## Open Loops

- [ ] [VERIFY: Is there a specific SLA or response-time target beyond "interactive"?]
- [ ] [VERIFY: Is there a planned .NET application that will consume the HTTP transport? If so, capture integration requirements here.]
- [ ] Handbook ingestion not yet complete — DOE handbook PDF chunks not in vector store; tools may return incomplete results for handbook-specific questions
