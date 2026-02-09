"""Tests for audit logging functionality.

Tests cover parameter sanitization, result summarization,
audit log writing, and the audit_log decorator.
"""

import json
from unittest.mock import patch

import pytest

from hrp_mcp.audit import (
    _sanitize_params,
    _summarize_result,
    _write_audit_log,
    audit_log,
    get_audit_entries,
)
from hrp_mcp.models.errors import AuditLogError

# --- Parameter Sanitization Tests ---


class TestSanitizeParams:
    """Tests for _sanitize_params function."""

    def test_should_redact_password(self):
        """Test that password fields are redacted."""
        params = {"username": "john", "password": "secret123"}
        result = _sanitize_params(params)

        assert result["username"] == "john"
        assert result["password"] == "[REDACTED]"  # noqa: S105

    def test_should_redact_token(self):
        """Test that token fields are redacted."""
        params = {"api_token": "abc123", "data": "value"}
        result = _sanitize_params(params)

        assert result["api_token"] == "[REDACTED]"  # noqa: S105
        assert result["data"] == "value"

    def test_should_redact_key(self):
        """Test that key fields are redacted."""
        params = {"api_key": "xyz789", "query": "test"}
        result = _sanitize_params(params)

        assert result["api_key"] == "[REDACTED]"
        assert result["query"] == "test"

    def test_should_redact_secret(self):
        """Test that secret fields are redacted."""
        params = {"client_secret": "shhh", "name": "test"}
        result = _sanitize_params(params)

        assert result["client_secret"] == "[REDACTED]"  # noqa: S105

    def test_should_redact_credential(self):
        """Test that credential fields are redacted."""
        params = {"user_credential": "cred123"}
        result = _sanitize_params(params)

        assert result["user_credential"] == "[REDACTED]"

    def test_should_redact_ssn(self):
        """Test that SSN fields are redacted."""
        params = {"ssn": "123-45-6789", "name": "John Doe"}
        result = _sanitize_params(params)

        assert result["ssn"] == "[REDACTED]"
        assert result["name"] == "John Doe"

    def test_should_redact_dob(self):
        """Test that DOB fields are redacted."""
        params = {"dob": "1990-01-01", "name": "Jane"}
        result = _sanitize_params(params)

        assert result["dob"] == "[REDACTED]"

    def test_should_be_case_insensitive(self):
        """Test that redaction is case-insensitive."""
        params = {"PASSWORD": "secret", "Api_Token": "token123"}
        result = _sanitize_params(params)

        assert result["PASSWORD"] == "[REDACTED]"  # noqa: S105
        assert result["Api_Token"] == "[REDACTED]"  # noqa: S105

    def test_should_truncate_long_strings(self):
        """Test that long strings are truncated."""
        long_value = "x" * 2000
        params = {"content": long_value}
        result = _sanitize_params(params)

        assert len(result["content"]) == 1000 + len("...[truncated]")
        assert result["content"].endswith("...[truncated]")

    def test_should_preserve_short_strings(self):
        """Test that short strings are preserved."""
        params = {"query": "short query"}
        result = _sanitize_params(params)

        assert result["query"] == "short query"

    def test_should_handle_non_string_values(self):
        """Test handling of non-string values."""
        params = {"count": 42, "enabled": True, "data": None}
        result = _sanitize_params(params)

        assert result["count"] == 42
        assert result["enabled"] is True
        assert result["data"] is None

    def test_should_handle_empty_params(self):
        """Test handling of empty params dict."""
        result = _sanitize_params({})
        assert result == {}


# --- Result Summarization Tests ---


class TestSummarizeResult:
    """Tests for _summarize_result function."""

    def test_should_handle_none(self):
        """Test summarization of None result."""
        assert _summarize_result(None) == "None"

    def test_should_handle_short_string(self):
        """Test summarization of short string."""
        result = _summarize_result("short result")
        assert result == "short result"

    def test_should_truncate_long_string(self):
        """Test truncation of long string result."""
        long_string = "x" * 500
        result = _summarize_result(long_string)

        assert len(result) == 200 + len("...[truncated]")
        assert result.endswith("...[truncated]")

    def test_should_summarize_list(self):
        """Test summarization of list result."""
        result = _summarize_result([1, 2, 3, 4, 5])
        assert result == "List with 5 items"

    def test_should_summarize_empty_list(self):
        """Test summarization of empty list."""
        result = _summarize_result([])
        assert result == "List with 0 items"

    def test_should_summarize_dict(self):
        """Test summarization of dict result."""
        result = _summarize_result({"a": 1, "b": 2, "c": 3})
        assert "Dict with keys:" in result
        assert "a" in result

    def test_should_limit_dict_keys_shown(self):
        """Test that dict summary limits keys shown."""
        large_dict = {f"key_{i}": i for i in range(10)}
        result = _summarize_result(large_dict)

        # Should only show first 5 keys
        assert result.count("key_") <= 5

    def test_should_handle_other_types(self):
        """Test summarization of other types."""
        result = _summarize_result(42)
        assert result == "int"

        result = _summarize_result(3.14)
        assert result == "float"


# --- Audit Log Writing Tests ---


class TestWriteAuditLog:
    """Tests for _write_audit_log function."""

    def test_should_write_entry_to_file(self, tmp_path):
        """Test writing audit entry to file."""
        log_file = tmp_path / "audit.jsonl"

        with patch("hrp_mcp.audit.settings") as mock_settings:
            mock_settings.audit_log_path = str(log_file)

            entry = {"tool": "test_tool", "status": "success"}
            _write_audit_log(entry)

            assert log_file.exists()
            content = log_file.read_text()
            parsed = json.loads(content.strip())
            assert parsed["tool"] == "test_tool"

    def test_should_append_to_existing_file(self, tmp_path):
        """Test appending to existing audit log."""
        log_file = tmp_path / "audit.jsonl"
        log_file.write_text('{"existing": "entry"}\n')

        with patch("hrp_mcp.audit.settings") as mock_settings:
            mock_settings.audit_log_path = str(log_file)

            entry = {"tool": "new_tool"}
            _write_audit_log(entry)

            lines = log_file.read_text().strip().split("\n")
            assert len(lines) == 2

    def test_should_create_parent_directories(self, tmp_path):
        """Test creation of parent directories."""
        log_file = tmp_path / "nested" / "dir" / "audit.jsonl"

        with patch("hrp_mcp.audit.settings") as mock_settings:
            mock_settings.audit_log_path = str(log_file)

            entry = {"tool": "test"}
            _write_audit_log(entry)

            assert log_file.exists()

    def test_should_raise_on_write_error(self, tmp_path):
        """Test that AuditLogError is raised on write failure."""
        # Use an invalid path (directory instead of file)
        log_dir = tmp_path / "audit_dir"
        log_dir.mkdir()

        with patch("hrp_mcp.audit.settings") as mock_settings:
            mock_settings.audit_log_path = str(log_dir)

            with pytest.raises(AuditLogError):
                _write_audit_log({"tool": "test"})


# --- Audit Log Decorator Tests ---


class TestAuditLogDecorator:
    """Tests for audit_log decorator."""

    @pytest.mark.asyncio
    async def test_should_log_async_function_success(self, tmp_path):
        """Test logging of successful async function."""
        log_file = tmp_path / "audit.jsonl"

        with patch("hrp_mcp.audit.settings") as mock_settings:
            mock_settings.audit_log_path = str(log_file)

            @audit_log
            async def async_tool(query: str) -> str:
                return f"result for {query}"

            result = await async_tool(query="test")

            assert result == "result for test"
            assert log_file.exists()

            entry = json.loads(log_file.read_text().strip())
            assert entry["tool"] == "async_tool"
            assert entry["status"] == "success"

    @pytest.mark.asyncio
    async def test_should_log_async_function_error(self, tmp_path):
        """Test logging of async function error."""
        log_file = tmp_path / "audit.jsonl"

        with patch("hrp_mcp.audit.settings") as mock_settings:
            mock_settings.audit_log_path = str(log_file)

            @audit_log
            async def failing_tool() -> None:
                raise ValueError("Something went wrong")

            with pytest.raises(ValueError):
                await failing_tool()

            entry = json.loads(log_file.read_text().strip())
            assert entry["status"] == "error"
            assert entry["error_type"] == "ValueError"

    def test_should_log_sync_function_success(self, tmp_path):
        """Test logging of successful sync function."""
        log_file = tmp_path / "audit.jsonl"

        with patch("hrp_mcp.audit.settings") as mock_settings:
            mock_settings.audit_log_path = str(log_file)

            @audit_log
            def sync_tool(name: str) -> dict:
                return {"name": name}

            result = sync_tool(name="test")

            assert result == {"name": "test"}
            entry = json.loads(log_file.read_text().strip())
            assert entry["tool"] == "sync_tool"
            assert entry["status"] == "success"

    def test_should_log_sync_function_error(self, tmp_path):
        """Test logging of sync function error."""
        log_file = tmp_path / "audit.jsonl"

        with patch("hrp_mcp.audit.settings") as mock_settings:
            mock_settings.audit_log_path = str(log_file)

            @audit_log
            def failing_sync() -> None:
                raise RuntimeError("Sync error")

            with pytest.raises(RuntimeError):
                failing_sync()

            entry = json.loads(log_file.read_text().strip())
            assert entry["status"] == "error"
            assert entry["error_type"] == "RuntimeError"

    def test_should_sanitize_params_in_log(self, tmp_path):
        """Test that parameters are sanitized in log."""
        log_file = tmp_path / "audit.jsonl"

        with patch("hrp_mcp.audit.settings") as mock_settings:
            mock_settings.audit_log_path = str(log_file)

            @audit_log
            def tool_with_sensitive(password: str, query: str) -> str:
                return "done"

            tool_with_sensitive(password="secret123", query="search")  # noqa: S106

            entry = json.loads(log_file.read_text().strip())
            assert entry["params"]["password"] == "[REDACTED]"  # noqa: S105
            assert entry["params"]["query"] == "search"


# --- Get Audit Entries Tests ---


class TestGetAuditEntries:
    """Tests for get_audit_entries function."""

    def test_should_return_empty_for_missing_file(self, tmp_path):
        """Test that empty list is returned when file doesn't exist."""
        with patch("hrp_mcp.audit.settings") as mock_settings:
            mock_settings.audit_log_path = str(tmp_path / "nonexistent.jsonl")

            result = get_audit_entries()
            assert result == []

    def test_should_read_entries(self, tmp_path):
        """Test reading entries from audit log."""
        log_file = tmp_path / "audit.jsonl"
        entries = [
            {"tool": "tool1", "timestamp": "2024-01-01"},
            {"tool": "tool2", "timestamp": "2024-01-02"},
        ]
        log_file.write_text("\n".join(json.dumps(e) for e in entries) + "\n")

        with patch("hrp_mcp.audit.settings") as mock_settings:
            mock_settings.audit_log_path = str(log_file)

            result = get_audit_entries()
            assert len(result) == 2

    def test_should_respect_limit(self, tmp_path):
        """Test that limit parameter is respected."""
        log_file = tmp_path / "audit.jsonl"
        entries = [{"tool": f"tool{i}"} for i in range(10)]
        log_file.write_text("\n".join(json.dumps(e) for e in entries) + "\n")

        with patch("hrp_mcp.audit.settings") as mock_settings:
            mock_settings.audit_log_path = str(log_file)

            result = get_audit_entries(limit=3)
            assert len(result) == 3

    def test_should_filter_by_tool(self, tmp_path):
        """Test filtering entries by tool name."""
        log_file = tmp_path / "audit.jsonl"
        entries = [
            {"tool": "search"},
            {"tool": "get_section"},
            {"tool": "search"},
        ]
        log_file.write_text("\n".join(json.dumps(e) for e in entries) + "\n")

        with patch("hrp_mcp.audit.settings") as mock_settings:
            mock_settings.audit_log_path = str(log_file)

            result = get_audit_entries(tool_filter="search")
            assert len(result) == 2
            assert all(e["tool"] == "search" for e in result)

    def test_should_return_most_recent_first(self, tmp_path):
        """Test that entries are returned most recent first."""
        log_file = tmp_path / "audit.jsonl"
        entries = [
            {"tool": "first", "order": 1},
            {"tool": "second", "order": 2},
            {"tool": "third", "order": 3},
        ]
        log_file.write_text("\n".join(json.dumps(e) for e in entries) + "\n")

        with patch("hrp_mcp.audit.settings") as mock_settings:
            mock_settings.audit_log_path = str(log_file)

            result = get_audit_entries()
            assert result[0]["order"] == 3  # Most recent first
            assert result[-1]["order"] == 1
