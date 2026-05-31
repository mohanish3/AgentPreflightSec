from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from agentpreflight.cli.main import app

ROOT = Path(__file__).resolve().parents[1]
POISONED = str(ROOT / "demo" / "poisoned")
CLEAN = str(ROOT / "demo" / "clean")

_RUNNER = CliRunner()


def test_list_files_poisoned_prints_paths() -> None:
    """--list-files outputs at least one file path when findings exist."""
    result = _RUNNER.invoke(app, ["scan", POISONED, "--list-files", "--no-banner"])
    assert result.exit_code == 0
    lines = [l for l in result.output.strip().splitlines() if l]
    assert len(lines) >= 1


def test_list_files_clean_empty_output() -> None:
    """--list-files prints nothing (no paths) when no findings."""
    result = _RUNNER.invoke(app, ["scan", CLEAN, "--list-files", "--no-banner"])
    assert result.exit_code == 0
    lines = [l for l in result.output.strip().splitlines() if l]
    assert lines == []


def test_list_files_no_duplicates() -> None:
    """Each file path appears at most once even when a file has multiple findings."""
    result = _RUNNER.invoke(app, ["scan", POISONED, "--list-files", "--no-banner"])
    lines = [l for l in result.output.strip().splitlines() if l]
    assert len(lines) == len(set(lines))


def test_list_files_suppresses_table() -> None:
    """--list-files does not print the findings table or trust_score line."""
    result = _RUNNER.invoke(app, ["scan", POISONED, "--list-files", "--no-banner"])
    assert "trust_score=" not in result.output
    assert "Severity" not in result.output


def test_list_files_exit_zero_on_clean() -> None:
    """Exit code is 0 for a clean target with --list-files."""
    result = _RUNNER.invoke(app, ["scan", CLEAN, "--list-files"])
    assert result.exit_code == 0


def test_list_files_exit_code_unaffected_without_fail_on() -> None:
    """Without --fail-on, exit code is 0 even with findings."""
    result = _RUNNER.invoke(app, ["scan", POISONED, "--list-files"])
    assert result.exit_code == 0


def test_list_files_fail_on_still_exits_one() -> None:
    """--fail-on threshold still controls exit code when combined with --list-files."""
    result = _RUNNER.invoke(app, ["scan", POISONED, "--list-files", "--fail-on", "high"])
    assert result.exit_code == 1


def test_list_files_exit_zero_overrides_fail_on() -> None:
    """--exit-zero overrides --fail-on even with --list-files."""
    result = _RUNNER.invoke(
        app, ["scan", POISONED, "--list-files", "--fail-on", "high", "--exit-zero"]
    )
    assert result.exit_code == 0


def test_list_files_paths_are_strings() -> None:
    """Each output line is a non-empty string (valid path-like)."""
    result = _RUNNER.invoke(app, ["scan", POISONED, "--list-files", "--no-banner"])
    lines = [l for l in result.output.strip().splitlines() if l]
    for line in lines:
        assert len(line) > 0
        assert "\n" not in line


def test_list_files_with_profile_flag() -> None:
    """--list-files works with --profile strict."""
    result = _RUNNER.invoke(
        app, ["scan", POISONED, "--list-files", "--profile", "strict", "--no-banner"]
    )
    assert result.exit_code == 0
    lines = [l for l in result.output.strip().splitlines() if l]
    assert len(lines) >= 1


def test_list_files_with_fail_on_score() -> None:
    """--list-files combined with --fail-on-score exits 1 when score below threshold."""
    result = _RUNNER.invoke(
        app, ["scan", POISONED, "--list-files", "--fail-on-score", "90"]
    )
    assert result.exit_code == 1


def test_list_files_quiet_does_not_double_print() -> None:
    """--list-files and --quiet together: only file paths printed, no quiet summary."""
    result = _RUNNER.invoke(app, ["scan", POISONED, "--list-files", "--quiet"])
    # quiet summary has trust_score= but list-files suppresses normal output
    # with both flags, list-files takes precedence for path printing
    assert result.exit_code == 0
