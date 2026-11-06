from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _make_finding(rule_id: str = "AP-MCP-001", path: str = "mcp.json", fix_available: bool = True):
    from agentpreflight.models import Finding

    return Finding(
        id=rule_id,
        severity="critical",
        category="mcp",
        title="Tool description prompt injection",
        path=path,
        evidence="Hidden instruction in description",
        risk="Agent hijack",
        fix="Rewrite description as neutral text.",
        fix_available=fix_available,
        line=5,
    )


def test_codex_fix_raises_import_error_without_openai():
    """run_codex_fix raises ImportError when openai package is not installed."""
    from agentpreflight.remediator.codex_fix import run_codex_fix

    with patch.dict("sys.modules", {"openai": None}):
        with pytest.raises(ImportError, match="openai package required"):
            run_codex_fix([_make_finding()])


def test_codex_fix_raises_value_error_without_api_key():
    """run_codex_fix raises ValueError when OPENAI_API_KEY is not set."""
    from agentpreflight.remediator.codex_fix import run_codex_fix

    mock_openai = MagicMock()
    with patch.dict("sys.modules", {"openai": mock_openai}):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("OPENAI_API_KEY", None)
            with pytest.raises(ValueError, match="OPENAI_API_KEY"):
                run_codex_fix([_make_finding()])


def test_codex_fix_skips_findings_without_fix_available():
    """run_codex_fix returns empty list when no findings have fix_available=True."""
    from agentpreflight.remediator.codex_fix import run_codex_fix

    mock_openai_mod = MagicMock()
    with patch.dict("sys.modules", {"openai": mock_openai_mod}):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            patches = run_codex_fix([_make_finding(fix_available=False)])
    assert patches == []


def test_codex_fix_returns_patches_with_mocked_client(tmp_path):
    """run_codex_fix calls chat.completions.create and returns CodexPatch objects."""
    from agentpreflight.remediator.codex_fix import CodexPatch, run_codex_fix

    proposed_text = '"description": "Search repository files and return matching lines."'

    mock_choice = SimpleNamespace(message=SimpleNamespace(content=proposed_text))
    mock_response = SimpleNamespace(choices=[mock_choice])
    mock_client_instance = MagicMock()
    mock_client_instance.chat.completions.create.return_value = mock_response

    mock_openai_mod = MagicMock()
    mock_openai_mod.OpenAI.return_value = mock_client_instance

    with patch.dict("sys.modules", {"openai": mock_openai_mod}):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            patches = run_codex_fix([_make_finding()], max_findings=1)

    assert len(patches) == 1
    assert isinstance(patches[0], CodexPatch)
    assert patches[0].finding_id == "AP-MCP-001"
    assert "description" in patches[0].proposed
    mock_client_instance.chat.completions.create.assert_called_once()
    call_kwargs = mock_client_instance.chat.completions.create.call_args
    assert call_kwargs.kwargs["model"] == "codex-mini-latest"
    assert call_kwargs.kwargs["temperature"] == 0


def test_codex_fix_filters_by_allowed_rules():
    """run_codex_fix only processes findings in the allowed set."""
    from agentpreflight.remediator.codex_fix import run_codex_fix

    proposed_text = "fixed"
    mock_choice = SimpleNamespace(message=SimpleNamespace(content=proposed_text))
    mock_response = SimpleNamespace(choices=[mock_choice])
    mock_client_instance = MagicMock()
    mock_client_instance.chat.completions.create.return_value = mock_response

    mock_openai_mod = MagicMock()
    mock_openai_mod.OpenAI.return_value = mock_client_instance

    findings = [_make_finding("AP-MCP-001"), _make_finding("AP-CODE-001")]
    with patch.dict("sys.modules", {"openai": mock_openai_mod}):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            patches = run_codex_fix(findings, allowed={"AP-MCP-001"})

    assert len(patches) == 1
    assert patches[0].finding_id == "AP-MCP-001"
