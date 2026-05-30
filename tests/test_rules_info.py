from __future__ import annotations

from typer.testing import CliRunner

from agentpreflight.cli.main import app
from agentpreflight.rules.catalog import ALL_RULES


def test_rules_info_known_rule_shows_id() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "info", "AP-CODE-001"])
    assert result.exit_code == 0
    assert "AP-CODE-001" in result.output


def test_rules_info_shows_severity() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "info", "AP-CODE-001"])
    assert result.exit_code == 0
    assert "critical" in result.output


def test_rules_info_shows_category() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "info", "AP-MCP-001"])
    assert result.exit_code == 0
    assert "tool_poisoning" in result.output


def test_rules_info_case_insensitive() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "info", "ap-code-001"])
    assert result.exit_code == 0
    assert "AP-CODE-001" in result.output


def test_rules_info_unknown_rule_exits_1() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "info", "AP-FAKE-999"])
    assert result.exit_code == 1


def test_rules_info_unknown_rule_shows_error_text() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "info", "AP-FAKE-999"])
    assert "AP-FAKE-999" in result.output or "unknown" in result.output.lower()


def test_rules_info_shows_description() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "info", "AP-CODE-001"])
    assert result.exit_code == 0
    # description should contain something meaningful about shell/exec
    assert "shell" in result.output.lower() or "exec" in result.output.lower()


def test_rules_info_shows_remediation() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "info", "AP-CODE-001"])
    assert result.exit_code == 0
    assert "fix" in result.output.lower() or "replace" in result.output.lower()


def test_rules_info_shows_references() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "info", "AP-CODE-001"])
    assert result.exit_code == 0
    assert "OWASP" in result.output or "CWE" in result.output


def test_rules_info_shows_applies_to() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "info", "AP-CODE-001"])
    assert result.exit_code == 0
    assert "code_py" in result.output or "code_js" in result.output


def test_rules_info_quick_fix_hint() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "info", "AP-SEC-002"])
    assert result.exit_code == 0
    assert "AP-SEC-002" in result.output
    # Should include a fix command hint
    assert "agentpreflight" in result.output


def test_rules_info_all_21_rules_are_findable() -> None:
    runner = CliRunner()
    for rule in ALL_RULES:
        result = runner.invoke(app, ["rules", "info", rule.id])
        assert result.exit_code == 0, f"rules info {rule.id} failed: {result.output}"
        assert rule.id in result.output
        assert rule.severity in result.output
