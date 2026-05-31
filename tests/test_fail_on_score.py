from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from agentpreflight.cli.main import app

ROOT = Path(__file__).resolve().parents[1]
POISONED = str(ROOT / "demo" / "poisoned")
CLEAN = str(ROOT / "demo" / "clean")

_RUNNER = CliRunner()


def test_fail_on_score_poisoned_below_threshold_exits_one() -> None:
    """Poisoned repo (score ~0) with --fail-on-score 50 exits 1."""
    result = _RUNNER.invoke(app, ["scan", POISONED, "--no-banner", "--fail-on-score", "50"])
    assert result.exit_code == 1


def test_fail_on_score_clean_above_threshold_exits_zero() -> None:
    """Clean repo (score 100) with --fail-on-score 50 exits 0."""
    result = _RUNNER.invoke(app, ["scan", CLEAN, "--no-banner", "--fail-on-score", "50"])
    assert result.exit_code == 0


def test_fail_on_score_prints_fail_message_with_threshold() -> None:
    """FAIL message and threshold value appear in output when score is below threshold."""
    result = _RUNNER.invoke(app, ["scan", POISONED, "--no-banner", "--fail-on-score", "50"])
    assert "FAIL" in result.output
    assert "50" in result.output


def test_fail_on_score_exit_zero_overrides() -> None:
    """--exit-zero overrides --fail-on-score so exit code is 0."""
    result = _RUNNER.invoke(
        app,
        ["scan", POISONED, "--no-banner", "--fail-on-score", "50", "--exit-zero"],
    )
    assert result.exit_code == 0


def test_fail_on_score_100_fails_on_any_finding() -> None:
    """--fail-on-score 100 fails if trust_score < 100 (i.e., any finding present)."""
    result = _RUNNER.invoke(app, ["scan", POISONED, "--no-banner", "--fail-on-score", "100"])
    assert result.exit_code == 1


def test_fail_on_score_1_clean_passes() -> None:
    """--fail-on-score 1 passes for clean repo (score 100 >= 1)."""
    result = _RUNNER.invoke(app, ["scan", CLEAN, "--no-banner", "--fail-on-score", "1"])
    assert result.exit_code == 0


def test_fail_on_score_invalid_above_100() -> None:
    """Score threshold > 100 is an invalid parameter."""
    result = _RUNNER.invoke(app, ["scan", CLEAN, "--no-banner", "--fail-on-score", "101"])
    assert result.exit_code != 0


def test_fail_on_score_invalid_below_1() -> None:
    """Score threshold < 1 is invalid (0 would never trigger; omit the flag instead)."""
    result = _RUNNER.invoke(app, ["scan", CLEAN, "--no-banner", "--fail-on-score", "0"])
    assert result.exit_code != 0


def test_fail_on_score_combined_with_fail_on_severity() -> None:
    """--fail-on and --fail-on-score can coexist; poisoned repo triggers both."""
    result = _RUNNER.invoke(
        app,
        ["scan", POISONED, "--no-banner", "--fail-on", "high", "--fail-on-score", "50"],
    )
    assert result.exit_code == 1


def test_fail_on_score_quiet_mode_exits_one() -> None:
    """--fail-on-score works in --quiet mode."""
    result = _RUNNER.invoke(
        app,
        ["scan", POISONED, "--quiet", "--fail-on-score", "50"],
    )
    assert result.exit_code == 1


def test_fail_on_score_clean_quiet_exits_zero() -> None:
    """--fail-on-score with clean target in quiet mode exits 0."""
    result = _RUNNER.invoke(
        app,
        ["scan", CLEAN, "--quiet", "--fail-on-score", "50"],
    )
    assert result.exit_code == 0
