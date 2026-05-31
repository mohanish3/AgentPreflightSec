from __future__ import annotations

import shutil
from pathlib import Path

from typer.testing import CliRunner

from agentpreflight.cli.main import app

ROOT = Path(__file__).resolve().parents[1]


def test_fix_header_shows_total_findings(tmp_path: Path) -> None:
    target = tmp_path / "poisoned"
    shutil.copytree(ROOT / "demo" / "poisoned", target)
    runner = CliRunner()
    result = runner.invoke(app, ["fix", str(target)])
    assert result.exit_code == 0
    assert "findings=" in result.output


def test_fix_header_findings_count_equals_scan_findings(tmp_path: Path) -> None:
    target = tmp_path / "poisoned"
    shutil.copytree(ROOT / "demo" / "poisoned", target)
    runner = CliRunner()
    from agentpreflight.scanner import scan_path
    scan = scan_path(target, profile="strict")
    result = runner.invoke(app, ["fix", str(target)])
    assert result.exit_code == 0
    assert f"findings={len(scan.findings)}" in result.output


def test_fix_quiet_dry_run_shows_summary_line(tmp_path: Path) -> None:
    target = tmp_path / "poisoned"
    shutil.copytree(ROOT / "demo" / "poisoned", target)
    runner = CliRunner()
    result = runner.invoke(app, ["fix", str(target), "--quiet"])
    assert result.exit_code == 0
    assert "fixable=" in result.output


def test_fix_quiet_dry_run_hides_table(tmp_path: Path) -> None:
    """Quiet dry-run must not print the findings table."""
    target = tmp_path / "poisoned"
    shutil.copytree(ROOT / "demo" / "poisoned", target)
    runner = CliRunner()
    quiet = runner.invoke(app, ["fix", str(target), "--quiet"])
    normal = runner.invoke(app, ["fix", str(target)])
    assert quiet.exit_code == 0
    assert normal.exit_code == 0
    # Normal dry-run prints the table (more output); quiet is much shorter
    assert len(quiet.output) < len(normal.output)
    # Quiet must not contain "dry_run=true" table footer line
    assert "dry_run=true" not in quiet.output


def test_fix_quiet_apply_shows_changed_count(tmp_path: Path) -> None:
    target = tmp_path / "poisoned"
    shutil.copytree(ROOT / "demo" / "poisoned", target)
    runner = CliRunner()
    result = runner.invoke(app, ["fix", str(target), "--apply", "--quiet"])
    assert result.exit_code == 0
    assert "changed=" in result.output


def test_fix_quiet_apply_hides_per_file_list(tmp_path: Path) -> None:
    """Quiet apply must not list individual file paths."""
    target_q = tmp_path / "poisoned_quiet"
    target_v = tmp_path / "poisoned_verbose"
    shutil.copytree(ROOT / "demo" / "poisoned", target_q)
    shutil.copytree(ROOT / "demo" / "poisoned", target_v)
    runner = CliRunner()
    quiet = runner.invoke(app, ["fix", str(target_q), "--apply", "--quiet"])
    verbose = runner.invoke(app, ["fix", str(target_v), "--apply"])
    assert quiet.exit_code == 0
    assert verbose.exit_code == 0
    # Verbose lists file paths (many lines); quiet is much shorter
    quiet_lines = [l for l in quiet.output.strip().splitlines() if l.strip()]
    verbose_lines = [l for l in verbose.output.strip().splitlines() if l.strip()]
    assert len(quiet_lines) < len(verbose_lines)


def test_fix_quiet_apply_no_file_paths_in_output(tmp_path: Path) -> None:
    """Quiet apply must not list individual changed file paths (no .py/.json lines)."""
    target = tmp_path / "poisoned"
    shutil.copytree(ROOT / "demo" / "poisoned", target)
    runner = CliRunner()
    result = runner.invoke(app, ["fix", str(target), "--apply", "--quiet"])
    assert result.exit_code == 0
    # Every non-empty line should be a summary token line, not a bare file path
    for line in result.output.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        # No line should be a bare file path (contains .py or .json but no = token)
        if ("=" not in line) and ("." in line):
            assert False, f"bare file path leaked into quiet output: {line!r}"


def test_fix_non_quiet_apply_still_lists_files(tmp_path: Path) -> None:
    """Regression: non-quiet apply still shows individual changed file paths."""
    target = tmp_path / "poisoned"
    shutil.copytree(ROOT / "demo" / "poisoned", target)
    runner = CliRunner()
    result = runner.invoke(app, ["fix", str(target), "--apply"])
    assert result.exit_code == 0
    assert "changed=" in result.output
    lines = [l for l in result.output.strip().splitlines() if l.strip()]
    # More than 2 lines: header + changed= + one per file
    assert len(lines) > 2


def test_fix_quiet_prove_still_shows_rescan(tmp_path: Path) -> None:
    """--quiet does not suppress --prove rescan summary."""
    target = tmp_path / "poisoned"
    shutil.copytree(ROOT / "demo" / "poisoned", target)
    runner = CliRunner()
    result = runner.invoke(app, ["fix", str(target), "--apply", "--prove", "--quiet"])
    assert result.exit_code == 0
    assert "rescan" in result.output
    assert "delta=" in result.output
