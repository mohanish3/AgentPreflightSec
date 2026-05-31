from __future__ import annotations

from typer.testing import CliRunner

from agentpreflight.cli.main import app
from agentpreflight.rules.catalog import ALL_RULES

_RUNNER = CliRunner()


def test_explain_shows_rule_id() -> None:
    rule = ALL_RULES[0]
    result = _RUNNER.invoke(app, ["explain", rule.id])
    assert result.exit_code == 0
    assert rule.id in result.output


def test_explain_shows_severity() -> None:
    rule = ALL_RULES[0]
    result = _RUNNER.invoke(app, ["explain", rule.id])
    assert result.exit_code == 0
    assert rule.severity in result.output


def test_explain_shows_description() -> None:
    rule = ALL_RULES[0]
    result = _RUNNER.invoke(app, ["explain", rule.id])
    assert result.exit_code == 0
    # Check at least one word from description appears
    words = [w for w in rule.description.split() if len(w) >= 5]
    assert any(w in result.output for w in words)


def test_explain_shows_remediation() -> None:
    rule = ALL_RULES[0]
    result = _RUNNER.invoke(app, ["explain", rule.id])
    assert result.exit_code == 0
    words = [w for w in rule.remediation.split() if len(w) >= 5]
    assert any(w in result.output for w in words)


def test_explain_case_insensitive() -> None:
    rule = ALL_RULES[0]
    lower = _RUNNER.invoke(app, ["explain", rule.id.lower()])
    upper = _RUNNER.invoke(app, ["explain", rule.id])
    assert lower.exit_code == 0
    assert upper.exit_code == 0
    assert rule.id in lower.output
    assert rule.id in upper.output


def test_explain_unknown_rule_exits_nonzero() -> None:
    result = _RUNNER.invoke(app, ["explain", "AP-FAKE-999"])
    assert result.exit_code != 0


def test_explain_unknown_rule_shows_error() -> None:
    result = _RUNNER.invoke(app, ["explain", "AP-FAKE-999"])
    assert "error" in result.output.lower() or "unknown" in result.output.lower()


def test_explain_works_for_all_rules() -> None:
    for rule in ALL_RULES:
        result = _RUNNER.invoke(app, ["explain", rule.id])
        assert result.exit_code == 0, f"explain failed for {rule.id}: {result.output}"
        assert rule.id in result.output


def test_explain_shows_fix_hint() -> None:
    """Output includes agentpreflight fix quick-fix hint."""
    rule = ALL_RULES[0]
    result = _RUNNER.invoke(app, ["explain", rule.id])
    assert result.exit_code == 0
    assert "fix" in result.output.lower()
