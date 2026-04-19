# human-reliability-program-mcp — Constraints

---

## Must Do

- Load and confirm context (`AGENTS.md`, `intent.md`, `constraints.md`) before every session.
- Read the active Jira issue / task spec before beginning any in-flight task.
- Write three verifiable acceptance criteria before beginning any significant subtask.
- Confirm understanding before executing any irreversible action (delete vector store, deploy, push).
- Add a `# VERIFY:` comment rather than guess when uncertain about a regulatory fact, function signature, or API behavior.
- Route every MCP tool invocation through `src/hrp_mcp/audit.py` — no tool may bypass the audit log.
- Use `defusedxml` for all XML parsing; never import `xml.etree.ElementTree` in `src/`.
- Validate all inputs at system boundaries using Pydantic models — never pass raw strings into downstream services.
- Write the test file before or alongside the production file — never after.
- End every session with a fully passing test state (`pytest` clean, `ruff check` clean, `mypy src/` clean).

---

## Must NOT Do

- Do not begin a task that has no verifiable acceptance criteria.
- Do not re-litigate decisions already logged in `AGENTS.md` or `intent.md` Persistent Decisions.
- Do not add a new external network dependency — the local-first constraint is a Persistent Decision; escalate if a use case seems to require one.
- Do not store, log, or transmit any PII or personnel-sensitive data — the vector store contains only public regulatory text.
- Do not hardcode secrets, tokens, or credentials — all config via `HRP_*` environment variables.
- Do not commit `.env` files, generated files, or build artifacts.
- Do not change the default transport from `stdio` without explicit human approval.
- Do not delete or truncate `logs/audit.jsonl` in any code path — it is append-only.
- Do not use `xml.etree.ElementTree` directly — always `defusedxml`.
- Do not use `.Result` or `.Wait()` on async methods — async is end-to-end.
- Do not move a Jira issue to Done or Closed — that is a human action only.
- Do not invent or paraphrase regulatory text without a direct CFR section citation.

---

## Preferences

- Prefer a new discrete MCP tool over expanding an existing one — tools are the unit of permission and audit.
- Prefer asking one clarifying question over assuming and proceeding.
- Prefer the `grounded-code-mcp` knowledge base (`python` collection) over training data for FastMCP, Pydantic v2, and pytest patterns.
- Prefer editing an existing file over creating a new one.
- Prefer brevity over completeness unless depth is explicitly requested.
- Prefer flagging a regulatory ambiguity with `[VERIFY:]` over authoring an interpretation.
- When adding a new tool, model it on `src/hrp_mcp/tools/regulations.py` — follow the existing pattern.

---

## Escalate Rather Than Decide

- Any output intended for external distribution (regulatory guidance documents, emails, stakeholder reports).
- Any action that conflicts with a logged Persistent Decision in `AGENTS.md` or `intent.md`.
- Any request where acceptance criteria cannot be met within stated constraints.
- Any change to the audit log path, format, or schema.
- Any change to the default MCP transport or host binding.
- Any security-relevant decision not explicitly covered by existing constraints.
- Any new dependency that contacts an external network endpoint.

---

## Code Quality Gates

- **Test coverage (business logic):** ≥ 80% — run `pytest --cov=src/hrp_mcp --cov-report=term-missing`
- **Test coverage (security-critical paths — audit, input validation):** ≥ 95%
- **Cyclomatic complexity (per method):** < 10
- **Code duplication:** ≤ 3%
- **Lint:** `ruff check src/ tests/` — zero issues
- **Type check:** `mypy src/` — zero errors (strict mode)
- **Security scan:** `bandit -r src/ -c pyproject.toml` — zero high or critical issues
- **Commit format:** Conventional Commits — `feat:`, `fix:`, `refactor:`, `chore:`, `test:`, `docs:`
- **Commit scope:** Atomic — one logical change per commit; no bundling unrelated changes
