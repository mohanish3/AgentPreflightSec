from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from agentpreflight.cli.main import app

ROOT = Path(__file__).resolve().parents[1]


def test_bench_command_reports_scan_timing() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["bench", str(ROOT / "demo" / "clean"), "--runs", "2"])

    assert result.exit_code == 0
    assert "bench target=" in result.output
    assert "runs=2" in result.output
