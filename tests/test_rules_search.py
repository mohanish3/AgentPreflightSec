from __future__ import annotations

from typer.testing import CliRunner

from agentpreflight.cli.main import app


def test_rules_search_exec_finds_code_rule() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "search", "exec"])
    assert result.exit_code == 0
    assert "AP-CODE-001" in result.output


def test_rules_search_shell_finds_code_rule() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "search", "shell"])
    assert result.exit_code == 0
    assert "AP-CODE-001" in result.output


def test_rules_search_mcp_finds_mcp_rules() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "search", "mcp"])
    assert result.exit_code == 0
    assert "AP-MCP-001" in result.output


def test_rules_search_case_insensitive() -> None:
    runner = CliRunner()
    lower = runner.invoke(app, ["rules", "search", "exec"])
    upper = runner.invoke(app, ["rules", "search", "EXEC"])
    assert lower.exit_code == 0
    assert upper.exit_code == 0
    assert lower.output == upper.output


def test_rules_search_no_match_shows_message() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "search", "XYZZY_NOMATCH_99999"])
    assert result.exit_code == 0
    assert "no rules" in result.output.lower() or "0 rules" in result.output.lower()


def test_rules_search_secret_finds_sec_rules() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "search", "secret"])
    assert result.exit_code == 0
    # AP-SEC-001 or AP-SEC-002 should appear (private key / api token / env file)
    assert "AP-SEC" in result.output


def test_rules_search_shows_severity_column() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "search", "exec"])
    assert result.exit_code == 0
    # table has a severity column
    assert "critical" in result.output or "high" in result.output


def test_rules_search_shows_category_column() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "search", "shell"])
    assert result.exit_code == 0
    assert "unsafe_exec" in result.output or "category" in result.output.lower()


def test_rules_search_matches_category_field() -> None:
    runner = CliRunner()
    # unsafe_exec is a category name
    result = runner.invoke(app, ["rules", "search", "unsafe_exec"])
    assert result.exit_code == 0
    assert "AP-CODE-001" in result.output


def test_rules_search_http_finds_net_rule() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "search", "http"])
    assert result.exit_code == 0
    # AP-NET rules cover plain HTTP
    assert "AP-NET" in result.output
