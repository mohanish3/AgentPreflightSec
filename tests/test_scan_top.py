from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from agentpreflight.cli.main import app

ROOT = Path(__file__).resolve().parents[1]
POISONED = str(ROOT / "demo" / "poisoned")
CLEAN = str(ROOT / "demo" / "clean")


def test_scan_top_1_shows_one_row() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["scan", POISONED, "--top", "1"])
    assert result.exit_code == 0
    # "...and N more" truncation message should appear when findings > 1
    assert "more finding" in result.output


def test_scan_top_1_truncation_message_accurate() -> None:
    runner = CliRunner()
    full = runner.invoke(app, ["scan", POISONED])
    top1 = runner.invoke(app, ["scan", POISONED, "--top", "1"])
    assert full.exit_code == 0
    assert top1.exit_code == 0
    # Extract total findings count from full scan
    for token in full.output.split():
        if token.startswith("findings="):
            total = int(token.split("=")[1])
            break
    else:
        raise AssertionError("findings= token not found")
    # top=1 should say "and {total-1} more"
    assert f"and {total - 1} more" in top1.output


def test_scan_top_0_shows_all_findings() -> None:
    runner = CliRunner()
    full = runner.invoke(app, ["scan", POISONED])
    unlimited = runner.invoke(app, ["scan", POISONED, "--top", "0"])
    assert full.exit_code == 0
    assert unlimited.exit_code == 0
    # No truncation message when --top 0
    assert "more finding" not in unlimited.output


def test_scan_default_top_is_20() -> None:
    """Default behavior unchanged — _MAX_TABLE_ROWS=20."""
    runner = CliRunner()
    default = runner.invoke(app, ["scan", POISONED])
    explicit = runner.invoke(app, ["scan", POISONED, "--top", "20"])
    assert default.exit_code == 0
    assert explicit.exit_code == 0
    assert default.output == explicit.output


def test_scan_top_clean_no_truncation_message() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["scan", CLEAN, "--top", "1"])
    assert result.exit_code == 0
    assert "more finding" not in result.output


def test_scan_top_does_not_affect_json_output() -> None:
    """--top only affects table display, not json format."""
    runner = CliRunner()
    full_json = runner.invoke(app, ["scan", POISONED, "--format", "json"])
    top1_json = runner.invoke(app, ["scan", POISONED, "--format", "json", "--top", "1"])
    assert full_json.exit_code == 0
    assert top1_json.exit_code == 0
    # JSON output should be identical regardless of --top
    assert full_json.output == top1_json.output
