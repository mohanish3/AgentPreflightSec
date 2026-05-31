from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from agentpreflight.cli.main import app

ROOT = Path(__file__).resolve().parents[1]


def test_bench_throughput_token_present() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["bench", str(ROOT / "demo" / "clean"), "--runs", "1"])
    assert result.exit_code == 0
    assert "throughput=" in result.output


def test_bench_throughput_format() -> None:
    """throughput token must be "throughput=N/s" where N is a non-negative number."""
    runner = CliRunner()
    result = runner.invoke(app, ["bench", str(ROOT / "demo" / "clean"), "--runs", "1"])
    assert result.exit_code == 0
    token = next((t for t in result.output.split() if t.startswith("throughput=")), None)
    assert token is not None, "throughput= token not found"
    value_str = token.split("=")[1]
    assert value_str.endswith("/s"), f"expected /s suffix, got: {value_str!r}"
    numeric = float(value_str.rstrip("/s").rstrip("/").rsplit("/", 1)[0])
    assert numeric >= 0


def test_bench_throughput_nonzero_for_poisoned() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["bench", str(ROOT / "demo" / "poisoned"), "--runs", "2"])
    assert result.exit_code == 0
    token = next((t for t in result.output.split() if t.startswith("throughput=")), None)
    assert token is not None
    value_str = token.split("=")[1].replace("/s", "")
    assert float(value_str) > 0


def test_bench_existing_fields_unchanged() -> None:
    """Adding throughput must not remove existing bench output fields."""
    runner = CliRunner()
    result = runner.invoke(app, ["bench", str(ROOT / "demo" / "clean"), "--runs", "2"])
    assert result.exit_code == 0
    assert "bench target=" in result.output
    assert "runs=2" in result.output
    assert "avg=" in result.output
    assert "min=" in result.output
    assert "max=" in result.output
