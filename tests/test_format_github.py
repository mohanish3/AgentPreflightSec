from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from agentpreflight.cli.main import app

ROOT = Path(__file__).resolve().parents[1]
POISONED = str(ROOT / "demo" / "poisoned")
CLEAN = str(ROOT / "demo" / "clean")

_RUNNER = CliRunner()


def test_format_github_exits_zero_on_clean() -> None:
    result = _RUNNER.invoke(app, ["scan", CLEAN, "--format", "github"])
    assert result.exit_code == 0


def test_format_github_outputs_annotation_on_poisoned() -> None:
    result = _RUNNER.invoke(app, ["scan", POISONED, "--format", "github"])
    assert result.exit_code == 0
    # GitHub annotation lines start with ::error or ::warning or ::notice
    assert "::" in result.output


def test_format_github_critical_uses_error_level() -> None:
    result = _RUNNER.invoke(app, ["scan", POISONED, "--format", "github"])
    assert result.exit_code == 0
    assert "::error" in result.output


def test_format_github_annotation_includes_file() -> None:
    result = _RUNNER.invoke(app, ["scan", POISONED, "--format", "github"])
    assert result.exit_code == 0
    assert "file=" in result.output


def test_format_github_annotation_includes_rule_id() -> None:
    result = _RUNNER.invoke(app, ["scan", POISONED, "--format", "github"])
    assert result.exit_code == 0
    assert "AP-" in result.output


def test_format_github_clean_produces_no_annotations() -> None:
    result = _RUNNER.invoke(app, ["scan", CLEAN, "--format", "github"])
    assert result.exit_code == 0
    assert "::" not in result.output


def test_format_github_respects_fail_on_exit_code() -> None:
    """--fail-on still controls exit code with github format."""
    result = _RUNNER.invoke(app, ["scan", POISONED, "--format", "github", "--fail-on", "high"])
    assert result.exit_code == 1


def test_format_github_exit_zero_overrides() -> None:
    result = _RUNNER.invoke(
        app, ["scan", POISONED, "--format", "github", "--fail-on", "high", "--exit-zero"]
    )
    assert result.exit_code == 0


def test_format_github_writable_to_file(tmp_path) -> None:
    out = tmp_path / "annotations.txt"
    result = _RUNNER.invoke(
        app, ["scan", POISONED, "--format", "github", "--output", str(out)]
    )
    assert result.exit_code == 0
    assert out.exists()
    content = out.read_text(encoding="utf-8")
    assert "::error" in content


def test_format_github_medium_uses_warning_level() -> None:
    result = _RUNNER.invoke(app, ["scan", POISONED, "--format", "github"])
    assert result.exit_code == 0
    # Poisoned has medium findings — should produce ::warning
    assert "::warning" in result.output
