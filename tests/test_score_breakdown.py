from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from agentpreflight.cli.main import app

ROOT = Path(__file__).resolve().parents[1]


def test_score_breakdown_shown_on_fail() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["scan", str(ROOT / "demo" / "poisoned"), "--profile", "strict"])
    assert result.exit_code == 0
    # Should show score deduction breakdown when trust_score < 100
    assert "score:" in result.output or "deductions:" in result.output or "critical×" in result.output


def test_score_breakdown_not_shown_on_pass() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["scan", str(ROOT / "demo" / "clean"), "--profile", "strict"])
    assert result.exit_code == 0
    # Clean scan passes — no deduction breakdown needed
    assert "critical×" not in result.output
    assert "deductions:" not in result.output


def test_score_breakdown_hidden_in_quiet_mode() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["scan", str(ROOT / "demo" / "poisoned"), "--quiet"])
    assert result.exit_code == 0
    lines = [l for l in result.output.strip().splitlines() if l.strip()]
    assert len(lines) == 1  # quiet stays one line even with breakdown feature


def test_score_breakdown_hidden_in_json_format() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["scan", str(ROOT / "demo" / "poisoned"), "--format", "json"])
    assert result.exit_code == 0
    import json
    payload = json.loads(result.output)
    assert payload["tool"] == "AgentPreflight"
