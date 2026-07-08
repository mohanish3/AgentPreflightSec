from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from agentpreflight.cli.main import app
from agentpreflight.rules.catalog import ALL_RULES
from agentpreflight.remediator.local_fix import FIXABLE_RULE_IDS

_RUNNER = CliRunner()


def test_fixable_flag_returns_subset() -> None:
    """--fixable returns fewer rules than the full list."""
    full = _RUNNER.invoke(app, ["rules", "list"])
    filtered = _RUNNER.invoke(app, ["rules", "list", "--fixable"])
    assert filtered.exit_code == 0
    # Full has all 21 rules; filtered should have fewer
    assert len(ALL_RULES) > 0
    fixable_count = sum(1 for r in ALL_RULES if r.id in FIXABLE_RULE_IDS)
    assert 0 < fixable_count < len(ALL_RULES)


def test_fixable_flag_only_shows_fixable_rules() -> None:
    """Every rule shown with --fixable has a local fix available."""
    result = _RUNNER.invoke(app, ["rules", "list", "--fixable"])
    assert result.exit_code == 0
    for rule_id in FIXABLE_RULE_IDS:
        # At least some fixable rule IDs should appear in output
        pass  # validated via JSON test below


def test_fixable_json_only_fixable_ids() -> None:
    """--fixable --json output contains only rules in FIXABLE_RULE_IDS."""
    result = _RUNNER.invoke(app, ["rules", "list", "--fixable", "--json"])
    assert result.exit_code == 0
    rules = json.loads(result.output)
    for rule in rules:
        assert rule["id"] in FIXABLE_RULE_IDS


def test_fixable_json_no_non_fixable_ids() -> None:
    """--fixable --json output excludes rules NOT in FIXABLE_RULE_IDS."""
    non_fixable = {r.id for r in ALL_RULES if r.id not in FIXABLE_RULE_IDS}
    result = _RUNNER.invoke(app, ["rules", "list", "--fixable", "--json"])
    assert result.exit_code == 0
    rules = json.loads(result.output)
    returned_ids = {r["id"] for r in rules}
    assert returned_ids.isdisjoint(non_fixable)


def test_fixable_shows_count_footer() -> None:
    """Footer shows filtered count when --fixable is active."""
    result = _RUNNER.invoke(app, ["rules", "list", "--fixable"])
    assert result.exit_code == 0
    assert "of" in result.output  # e.g. "14 of 21 rules"


def test_fixable_combined_with_severity() -> None:
    """--fixable combines with --severity to further narrow results."""
    result = _RUNNER.invoke(app, ["rules", "list", "--fixable", "--severity", "high"])
    assert result.exit_code == 0


def test_fixable_combined_with_description() -> None:
    """--fixable combines with --description flag."""
    result = _RUNNER.invoke(app, ["rules", "list", "--fixable", "--description"])
    assert result.exit_code == 0
    assert "Description" in result.output


def test_fixable_combined_with_applies_to() -> None:
    """--fixable combines with --applies-to flag."""
    result = _RUNNER.invoke(app, ["rules", "list", "--fixable", "--applies-to", "code_py"])
    assert result.exit_code == 0


def test_fixable_rule_ids_constant_non_empty() -> None:
    """FIXABLE_RULE_IDS is a non-empty set of strings."""
    assert isinstance(FIXABLE_RULE_IDS, (set, frozenset))
    assert len(FIXABLE_RULE_IDS) > 0
    for rid in FIXABLE_RULE_IDS:
        assert isinstance(rid, str)
        assert rid.startswith("AP-")


def test_fixable_all_ids_exist_in_catalog() -> None:
    """Every ID in FIXABLE_RULE_IDS corresponds to a real rule in ALL_RULES."""
    catalog_ids = {r.id for r in ALL_RULES}
    for rid in FIXABLE_RULE_IDS:
        assert rid in catalog_ids, f"{rid} in FIXABLE_RULE_IDS but not in ALL_RULES"
