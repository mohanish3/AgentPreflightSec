from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from agentpreflight.cli.main import app

ROOT = Path(__file__).resolve().parents[1]
POISONED = str(ROOT / "demo" / "poisoned")
CLEAN = str(ROOT / "demo" / "clean")


def test_exit_zero_overrides_fail_on() -> None:
    """--exit-zero causes exit 0 even when --fail-on threshold is met."""
    runner = CliRunner()
    result = runner.invoke(app, ["scan", POISONED, "--fail-on", "high", "--exit-zero"])
    assert result.exit_code == 0


def test_without_exit_zero_fail_on_still_exits_one() -> None:
    """Regression: without --exit-zero, --fail-on still exits 1."""
    runner = CliRunner()
    result = runner.invoke(app, ["scan", POISONED, "--fail-on", "high"])
    assert result.exit_code == 1


def test_exit_zero_fail_line_still_printed() -> None:
    """FAIL threshold line still appears under --exit-zero (accurate reporting)."""
    runner = CliRunner()
    result = runner.invoke(app, ["scan", POISONED, "--fail-on", "high", "--exit-zero"])
    assert result.exit_code == 0
    assert "FAIL" in result.output
    assert "threshold=high" in result.output


def test_exit_zero_clean_target_exits_zero() -> None:
    """Clean target with --exit-zero and --fail-on → exit 0 (no threshold met anyway)."""
    runner = CliRunner()
    result = runner.invoke(app, ["scan", CLEAN, "--fail-on", "high", "--exit-zero"])
    assert result.exit_code == 0


def test_exit_zero_without_fail_on_has_no_effect() -> None:
    """--exit-zero without --fail-on changes nothing (already exits 0)."""
    runner = CliRunner()
    result = runner.invoke(app, ["scan", POISONED, "--exit-zero"])
    assert result.exit_code == 0


def test_exit_zero_json_format_ci_sarif_pattern() -> None:
    """CI pattern: --format sarif --exit-zero → valid output + exit 0 regardless of findings."""
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["scan", POISONED, "--format", "json", "--fail-on", "critical", "--exit-zero"],
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["tool"] == "AgentPreflight"
    assert len(data["findings"]) > 0


def test_exit_zero_quiet_mode() -> None:
    """--exit-zero works with --quiet."""
    runner = CliRunner()
    result = runner.invoke(app, ["scan", POISONED, "--quiet", "--fail-on", "high", "--exit-zero"])
    assert result.exit_code == 0
    lines = [line for line in result.output.strip().splitlines() if line.strip()]
    assert len(lines) == 1


def test_exit_zero_critical_threshold() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["scan", POISONED, "--fail-on", "critical", "--exit-zero"])
    assert result.exit_code == 0


def test_exit_zero_output_otherwise_unchanged() -> None:
    """Output content is identical with/without --exit-zero (only exit code differs)."""
    runner = CliRunner()
    with_flag = runner.invoke(app, ["scan", POISONED, "--no-banner", "--fail-on", "high", "--exit-zero"])
    without_flag = runner.invoke(app, ["scan", POISONED, "--no-banner", "--fail-on", "high"])
    assert with_flag.exit_code == 0
    assert without_flag.exit_code == 1
    # Output text must be identical — only the exit code differs
    assert with_flag.output == without_flag.output
