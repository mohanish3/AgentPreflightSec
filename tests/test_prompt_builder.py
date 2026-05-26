from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from agentpreflight.cli.main import app
from agentpreflight.remediator.prompt_builder import build_prompt_pack
from agentpreflight.scanner import scan_path

ROOT = Path(__file__).resolve().parents[1]


def test_prompt_pack_redacts_secret_patterns() -> None:
    result = scan_path(ROOT / "demo" / "poisoned", profile="strict")

    prompt_pack = build_prompt_pack(result.findings, max_findings=10)

    assert "AgentPreflight Codex remediation prompt pack" in prompt_pack
    assert "sk-poisonedfixture" not in prompt_pack
    assert "REDACTED" in prompt_pack


def test_prompts_cli_writes_prompt_pack(tmp_path: Path) -> None:
    runner = CliRunner()
    output = tmp_path / "prompts.md"

    result = runner.invoke(app, ["prompts", str(ROOT / "demo" / "poisoned"), "--output", str(output)])

    assert result.exit_code == 0
    assert output.exists()
    text = output.read_text(encoding="utf-8")
    assert "System prompt" in text
    assert "AP-MCP-001" in text
