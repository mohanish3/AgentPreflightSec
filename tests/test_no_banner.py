from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from agentpreflight.cli.main import app

ROOT = Path(__file__).resolve().parents[1]
POISONED = str(ROOT / "demo" / "poisoned")
CLEAN = str(ROOT / "demo" / "clean")

# "Pre-deployment" is unique to the banner — not in table output or any rule output
_BANNER_MARKER = "Pre-deployment"


def test_default_scan_shows_banner() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["scan", CLEAN])
    assert result.exit_code == 0
    assert _BANNER_MARKER in result.output


def test_no_banner_suppresses_banner() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["scan", CLEAN, "--no-banner"])
    assert result.exit_code == 0
    assert _BANNER_MARKER not in result.output


def test_no_banner_still_shows_table_output() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["scan", CLEAN, "--no-banner"])
    assert result.exit_code == 0
    assert "trust_score=" in result.output
    assert "verdict=" in result.output


def test_no_banner_on_poisoned_still_shows_findings() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["scan", POISONED, "--no-banner"])
    assert result.exit_code == 0
    assert "findings=" in result.output
    assert _BANNER_MARKER not in result.output


def test_quiet_still_suppresses_banner_without_no_banner_flag() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["scan", CLEAN, "--quiet"])
    assert result.exit_code == 0
    assert _BANNER_MARKER not in result.output
    lines = [l for l in result.output.strip().splitlines() if l.strip()]
    assert len(lines) == 1


def test_no_banner_with_fail_on() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["scan", POISONED, "--no-banner", "--fail-on", "high"])
    assert result.exit_code == 1
    assert _BANNER_MARKER not in result.output
    assert "FAIL" in result.output


def test_no_banner_json_format_unchanged() -> None:
    """--no-banner has no effect on non-table formats."""
    runner = CliRunner()
    import json
    with_banner = runner.invoke(app, ["scan", CLEAN, "--format", "json"])
    without_banner = runner.invoke(app, ["scan", CLEAN, "--format", "json", "--no-banner"])
    assert with_banner.exit_code == 0
    assert without_banner.exit_code == 0
    assert json.loads(with_banner.output) == json.loads(without_banner.output)
