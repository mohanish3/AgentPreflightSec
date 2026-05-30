from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from agentpreflight.cli.main import app

ROOT = Path(__file__).resolve().parents[1]


def test_output_table_format_exits_with_error(tmp_path: Path) -> None:
    """--output with default table format must error, not silently write empty file."""
    out_file = tmp_path / "report.txt"
    runner = CliRunner()
    result = runner.invoke(app, ["scan", str(ROOT / "demo" / "poisoned"), "--output", str(out_file)])
    assert result.exit_code != 0
    assert "table" in result.output.lower() or "format" in result.output.lower()


def test_output_table_format_does_not_write_empty_file(tmp_path: Path) -> None:
    """The empty-file silent bug: file must NOT exist (or not be empty) after the error."""
    out_file = tmp_path / "report.txt"
    runner = CliRunner()
    runner.invoke(app, ["scan", str(ROOT / "demo" / "poisoned"), "--output", str(out_file)])
    # File should not exist at all (we error before writing)
    assert not out_file.exists() or out_file.stat().st_size > 0


def test_output_json_format_writes_file(tmp_path: Path) -> None:
    out_file = tmp_path / "report.json"
    runner = CliRunner()
    result = runner.invoke(app, ["scan", str(ROOT / "demo" / "poisoned"), "--format", "json", "--output", str(out_file)])
    assert result.exit_code == 0
    assert out_file.exists()
    assert out_file.stat().st_size > 0
    payload = json.loads(out_file.read_text(encoding="utf-8"))
    assert payload["tool"] == "AgentPreflight"


def test_output_sarif_format_writes_file(tmp_path: Path) -> None:
    out_file = tmp_path / "report.sarif"
    runner = CliRunner()
    result = runner.invoke(app, ["scan", str(ROOT / "demo" / "poisoned"), "--format", "sarif", "--output", str(out_file)])
    assert result.exit_code == 0
    assert out_file.exists()
    payload = json.loads(out_file.read_text(encoding="utf-8"))
    assert payload["version"] == "2.1.0"


def test_output_markdown_format_writes_file(tmp_path: Path) -> None:
    out_file = tmp_path / "pr-comment.md"
    runner = CliRunner()
    result = runner.invoke(app, ["scan", str(ROOT / "demo" / "poisoned"), "--format", "markdown", "--output", str(out_file)])
    assert result.exit_code == 0
    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8")
    assert "AgentPreflight" in content


def test_output_error_shows_format_alternatives(tmp_path: Path) -> None:
    """Error message must mention the valid formats so user knows what to use."""
    out_file = tmp_path / "report.txt"
    runner = CliRunner()
    result = runner.invoke(app, ["scan", str(ROOT / "demo" / "poisoned"), "--output", str(out_file)])
    assert result.exit_code != 0
    # Should mention at least one of the valid formats
    assert any(fmt in result.output for fmt in ("markdown", "json", "sarif"))
