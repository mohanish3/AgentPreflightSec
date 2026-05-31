from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from agentpreflight.cli.main import app

ROOT = Path(__file__).resolve().parents[1]


def test_scan_output_uses_relative_not_absolute_path() -> None:
    """target= line should not contain the full Windows absolute path."""
    runner = CliRunner()
    result = runner.invoke(app, ["scan", str(ROOT / "demo" / "poisoned")])
    assert result.exit_code == 0
    # Relative path should appear (forward-slash posix form)
    assert "demo/poisoned" in result.output or "demo\\poisoned" in result.output


def test_scan_output_target_no_line_break_in_path() -> None:
    """Absolute paths with spaces in directory names break terminal output.
    Relative path avoids that entirely."""
    runner = CliRunner()
    result = runner.invoke(app, ["scan", str(ROOT / "demo" / "clean")])
    assert result.exit_code == 0
    # The broken-path pattern 'Mohanish \nMhatre' or similar should not appear
    # (path should not contain the Windows username with embedded whitespace)
    lines = result.output.splitlines()
    target_line = next((line for line in lines if "AgentPreflight target=" in line), "")
    assert target_line, "target= line not found"
    # Should not contain a backslash + volume letter (absolute Windows path)
    # when we can express it as relative
    assert "demo" in target_line


def test_fix_available_line_uses_relative_path() -> None:
    """fix_available hint at bottom of scan output should use relative path."""
    runner = CliRunner()
    result = runner.invoke(app, ["scan", str(ROOT / "demo" / "poisoned")])
    assert result.exit_code == 0
    fix_line = next((line for line in result.output.splitlines() if "fix_available=" in line), "")
    assert fix_line, "fix_available= line not found"
    assert "demo/poisoned" in fix_line or "demo\\poisoned" in fix_line


def test_scan_clean_target_line_is_readable() -> None:
    """Clean scan target= line should be a single readable path."""
    runner = CliRunner()
    result = runner.invoke(app, ["scan", str(ROOT / "demo" / "clean")])
    assert result.exit_code == 0
    lines = result.output.splitlines()
    target_line = next((line for line in lines if "AgentPreflight target=" in line), "")
    # Should be on a single line (no mid-path wrapping due to spaces)
    assert "target=" in target_line
    assert "demo" in target_line
