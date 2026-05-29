from __future__ import annotations
from agentpreflight.models import Finding, ScoreDetail

DEDUCTIONS = {"critical": 30, "high": 15, "medium": 7, "low": 2}

VERDICTS = [(85, "pass"), (70, "warn"), (0, "fail")]


def _apply_caps(score: int, findings: list[Finding]) -> tuple[int, list[str]]:
    caps_applied = []

    severity_set = {f.severity for f in findings}
    category_set = {f.category for f in findings}

    has_critical = "critical" in severity_set
    high_count = sum(1 for f in findings if f.severity == "high")
    has_secret = "secrets" in category_set
    has_unsafe_shell = any(f.id == "AP-CODE-001" for f in findings)
    has_network_egress = any(f.id in ("AP-CODE-005", "AP-NET-001") for f in findings)
    has_unicode = any(f.id == "AP-SKILL-002" for f in findings)
    has_prompt_override = any(f.id in ("AP-MCP-001", "AP-SKILL-001") for f in findings)
    has_privileged_access = any(f.id == "AP-MCP-005" for f in findings)
    has_remote_fetch = any(f.id in ("AP-SKILL-003", "AP-CODE-003") for f in findings)

    if has_critical and score > 50:
        score = 50
        caps_applied.append("any_critical_cap_50")

    if high_count >= 3 and score > 60:
        score = 60
        caps_applied.append("three_high_cap_60")

    if has_secret and score > 55:
        score = 55
        caps_applied.append("secret_cap_55")

    if has_unsafe_shell and has_network_egress and score > 45:
        score = 45
        caps_applied.append("shell_network_combo_cap_45")

    if has_unicode and has_prompt_override and score > 50:
        score = 50
        caps_applied.append("unicode_override_combo_cap_50")

    if has_privileged_access and has_remote_fetch and score > 45:
        score = 45
        caps_applied.append("privileged_remote_combo_cap_45")

    return score, caps_applied


def score(findings: list[Finding], profile: str = "balanced") -> ScoreDetail:
    base = 100
    deduction_log: dict[str, int] = {"critical": 0, "high": 0, "medium": 0, "low": 0}

    for f in findings:
        sev = f.severity
        if profile == "strict" and sev == "medium":
            sev = "high"
        deduction_log[sev] += DEDUCTIONS.get(sev, 0)

    raw = base - sum(deduction_log.values())
    raw = max(0, raw)

    raw, caps_applied = _apply_caps(raw, findings)

    effective_counts: dict[str, int] = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for f in findings:
        eff = f.severity
        if profile == "strict" and eff == "medium":
            eff = "high"
        effective_counts[eff] += 1

    deductions_list = [
        {"severity": bucket, "count": effective_counts[bucket], "points": pts}
        for bucket, pts in deduction_log.items()
        if pts > 0
    ]

    return ScoreDetail(
        base=base,
        deductions=deductions_list,
        caps_applied=caps_applied,
        final=raw,
    )


def verdict(score_val: int) -> str:
    for threshold, label in VERDICTS:
        if score_val >= threshold:
            return label
    return "fail"
