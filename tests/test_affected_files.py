from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from agentpreflight.cli.main import app

ROOT = Path(__file__).resolve().parents[1]
POISONED = str(ROOT / "demo" / "poisoned")
CLEAN = str(ROOT / "demo" / "clean")


def test_affected_files_shown_in_table_output_for_poisoned() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["scan", POISONED])
    assert result.exit_code == 0
    assert "affected_files=" in result.output


def test_affected_files_nonzero_for_poisoned() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["scan", POISONED])
    assert result.exit_code == 0
    # Extract affected_files=N value
    for token in result.output.split():
        if token.startswith("affected_files="):
            n = int(token.split("=")[1])
            assert n > 0
            return
    raise AssertionError("affected_files= token not found in output")


def test_affected_files_zero_for_clean() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["scan", CLEAN])
    assert result.exit_code == 0
    for token in result.output.split():
        if token.startswith("affected_files="):
            n = int(token.split("=")[1])
            assert n == 0
            return
    # If no findings, affected_files=0 should still appear in summary
    raise AssertionError("affected_files= token not found in output")


def test_affected_files_consistent_with_findings() -> None:
    """affected_files count must be <= number of findings and <= artifacts_scanned."""
    runner = CliRunner()
    result = runner.invoke(app, ["scan", POISONED, "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    findings = data["findings"]
    unique_paths = len({f["path"] for f in findings})
    # Scan the table output to verify the display is consistent
    table_result = runner.invoke(app, ["scan", POISONED])
    assert f"affected_files={unique_paths}" in table_result.output


def test_affected_files_not_in_json_output_keys() -> None:
    """JSON schema must not be changed — affected_files is display-only."""
    runner = CliRunner()
    result = runner.invoke(app, ["scan", POISONED, "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    # summary dict should NOT have affected_files (display-only)
    assert "affected_files" not in data.get("summary", {})


def test_affected_files_not_shown_in_quiet_mode() -> None:
    """Quiet mode is one line — affected_files is a table-format concern only."""
    runner = CliRunner()
    result = runner.invoke(app, ["scan", POISONED, "--quiet"])
    assert result.exit_code == 0
    lines = [line for line in result.output.strip().splitlines() if line.strip()]
    assert len(lines) == 1
