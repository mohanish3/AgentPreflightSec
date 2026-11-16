"""Tests for the trust-score deduction breakdown (v3: single source of truth).

These pin the contract that the deduction breakdown is always self-consistent
and that profile escalation is recorded under the *effective* severity, not the
original one. On the current code the strict-profile cases FAIL because a
`medium` finding escalated to `high` in strict mode deducts 15 points (the high
value) but records them under the `medium` key.
"""
from __future__ import annotations

from agentpreflight.models import Finding
from agentpreflight.scorer import trust_score as ts


def _finding(sev: str, id_: str | None = None) -> Finding:
    return Finding(
        id=id_ or f"AP-{sev.upper()}",
        severity=sev,
        category="code",
        title="t",
        path="p.py",
        evidence="e",
        risk="r",
        fix="f",
    )


def test_effective_severity_helper_exists_and_escalates() -> None:
    # (4) a named helper must exist and encode the escalation table.
    assert hasattr(ts, "effective_severity"), (
        "v3 helper effective_severity(sev, profile) is missing"
    )
    assert ts.effective_severity("medium", "strict") == "high"
    assert ts.effective_severity("medium", "balanced") == "medium"
    # non-escalated severities pass straight through in any profile
    assert ts.effective_severity("high", "strict") == "high"
    assert ts.effective_severity("critical", "strict") == "critical"
    assert ts.effective_severity("low", "balanced") == "low"


def test_strict_medium_escalated_recorded_as_high() -> None:
    # (1) strict + [medium] -> a single 'high' entry of 15, no 15-pt 'medium'.
    detail = ts.score([_finding("medium")], profile="strict")
    by_sev = {e["severity"]: e for e in detail.deductions}
    assert "medium" not in by_sev, (
        f"strict profile must not keep an escalated deduction under 'medium': {detail.deductions}"
    )
    assert by_sev.get("high") == {"severity": "high", "count": 1, "points": 15}, (
        f"strict + [medium] should deduce 15 under 'high', got: {detail.deductions}"
    )


def test_balanced_profile_unchanged() -> None:
    # (2) balanced profile behaviour is unchanged (no escalation there).
    detail = ts.score([_finding("medium")], profile="balanced")
    assert detail.deductions == [{"severity": "medium", "count": 1, "points": 7}]
    assert detail.final == 93


def test_deduction_invariant_holds_in_both_profiles() -> None:
    # (3) the self-consistency invariant: for every breakdown entry,
    # points == count * DEDUCTIONS[severity], across a mixed finding set in
    # BOTH profiles. The strict case fails on the current code because the
    # escalated 15 points are mislabeled as 'medium' (15 != 1 * 7).
    for profile in ("balanced", "strict"):
        findings = [_finding(sev, id_=f"AP-{sev.upper()}-{i}") for i, sev in enumerate(
            ("medium", "high", "low", "critical")
        )]
        detail = ts.score(findings, profile=profile)
        for entry in detail.deductions:
            expected = entry["count"] * ts.DEDUCTIONS[entry["severity"]]
            assert entry["points"] == expected, (
                f"profile={profile}: entry {entry} violates "
                f"points == count * DEDUCTIONS[severity] (expected {expected})"
            )
