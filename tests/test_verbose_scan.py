from __future__ import annotations

import json
import shutil
from pathlib import Path

from typer.testing import CliRunner

from agentpreflight.cli.main import app

ROOT = Path(__file__).resolve().parents[1]


def test_scan_verbose_shows_finding_source_line(tmp_path: Path) -> None:
    (tmp_path / "run.py").write_text("import os\nos.system('rm -rf /')\n", encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(app, ["scan", str(tmp_path), "--verbose"])
    assert result.exit_code == 0
    assert "os.system" in result.output


def test_scan_verbose_shows_context_lines(tmp_path: Path) -> None:
    (tmp_path / "evil.py").write_text(
        "x = 1\n"
        "y = 2\n"
        "os.system('ls')\n"
        "z = 3\n",
        encoding="utf-8",
    )
    runner = CliRunner()
    result = runner.invoke(app, ["scan", str(tmp_path), "--verbose"])
    assert result.exit_code == 0
    # Context lines around the finding should appear
    assert "x = 1" in result.output or "y = 2" in result.output or "z = 3" in result.output


def test_scan_verbose_shows_finding_line_marker(tmp_path: Path) -> None:
    (tmp_path / "run.py").write_text("os.system('whoami')\n", encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(app, ["scan", str(tmp_path), "--verbose"])
    assert result.exit_code == 0
    assert "→" in result.output


def test_scan_verbose_clean_target_no_snippet_block() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["scan", str(ROOT / "demo" / "clean"), "--verbose"])
    assert result.exit_code == 0
    assert "no issues found" in result.output
    # No snippet markers on clean scan
    assert "→" not in result.output


def test_scan_verbose_json_format_ignores_snippets(tmp_path: Path) -> None:
    """--verbose has no effect on JSON output; output must still parse cleanly."""
    (tmp_path / "evil.py").write_text("os.system('ls')\n", encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(app, ["scan", str(tmp_path), "--format", "json", "--verbose"])
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["tool"] == "AgentPreflight"


def test_scan_verbose_quiet_flag_ignores_snippets(tmp_path: Path) -> None:
    """--verbose is suppressed by --quiet; output stays one line."""
    (tmp_path / "evil.py").write_text("os.system('ls')\n", encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(app, ["scan", str(tmp_path), "--quiet", "--verbose"])
    assert result.exit_code == 0
    lines = [l for l in result.output.strip().splitlines() if l.strip()]
    assert len(lines) == 1
    assert "trust_score=" in lines[0]


def test_scan_verbose_poisoned_demo_shows_source(tmp_path: Path) -> None:
    target = tmp_path / "poisoned"
    shutil.copytree(ROOT / "demo" / "poisoned", target)
    runner = CliRunner()
    result = runner.invoke(app, ["scan", str(target), "--verbose"])
    assert result.exit_code == 0
    # Poisoned demo has run.py and server.py with os.system calls that have line numbers
    assert "→" in result.output


def test_scan_verbose_multiple_findings_same_file_no_duplicate_lines(tmp_path: Path) -> None:
    """Two findings close together should not print the same line twice."""
    code = (
        "import os\n"
        "os.system('a')\n"
        "os.system('b')\n"
    )
    (tmp_path / "multi.py").write_text(code, encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(app, ["scan", str(tmp_path), "--verbose"])
    assert result.exit_code == 0
    # Line 1 "import os" should appear at most once even though both findings reference it
    assert result.output.count("import os") <= 1
