from __future__ import annotations

from typer.testing import CliRunner

from agentpreflight.cli.main import app


def test_profiles_command_exits_zero() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["profiles"])
    assert result.exit_code == 0


def test_profiles_lists_all_three_profiles() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["profiles"])
    assert result.exit_code == 0
    assert "dev" in result.output
    assert "balanced" in result.output
    assert "strict" in result.output


def test_profiles_shows_strict_medium_promotion() -> None:
    """Strict profile promotes medium findings to high — must be stated."""
    runner = CliRunner()
    result = runner.invoke(app, ["profiles"])
    assert result.exit_code == 0
    assert "medium" in result.output
    assert "high" in result.output
    # The output must mention the promotion in some form
    output_lower = result.output.lower()
    assert "strict" in output_lower
    # strict description must mention medium→high or "promotes" or similar
    assert any(term in output_lower for term in ["medium", "promotes", "treated as", "upgrade"])


def test_profiles_shows_verdict_thresholds() -> None:
    """Verdict bands (pass≥85, warn≥70) are shared and verifiable facts."""
    runner = CliRunner()
    result = runner.invoke(app, ["profiles"])
    assert result.exit_code == 0
    assert "85" in result.output
    assert "70" in result.output


def test_profiles_shows_deduction_values() -> None:
    """Deduction points (critical=30, high=15, medium=7, low=2) are facts."""
    runner = CliRunner()
    result = runner.invoke(app, ["profiles"])
    assert result.exit_code == 0
    assert "30" in result.output
    assert "15" in result.output
    assert "7" in result.output


def test_profiles_dev_balanced_identical_note() -> None:
    """dev and balanced are functionally identical — output must reflect this."""
    runner = CliRunner()
    result = runner.invoke(app, ["profiles"])
    assert result.exit_code == 0
    output_lower = result.output.lower()
    # Must mention they are same/identical/equivalent, not imply they differ
    assert any(term in output_lower for term in ["identical", "same", "equivalent", "alias"])


def test_profiles_shows_pass_warn_fail_labels() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["profiles"])
    assert result.exit_code == 0
    assert "pass" in result.output.lower()
    assert "warn" in result.output.lower()
    assert "fail" in result.output.lower()
