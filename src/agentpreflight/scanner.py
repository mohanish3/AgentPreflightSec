from __future__ import annotations

from collections import Counter
from pathlib import Path

from agentpreflight.collectors.path_collector import collect
from agentpreflight.models import ScanResult
from agentpreflight.normalizers.unicode import normalize_all
from agentpreflight.rules.catalog import ALL_RULES
from agentpreflight.rules.engine import RuleEngine
from agentpreflight.scorer.trust_score import score, verdict
from agentpreflight.suppressions import (
    apply_inline_suppressions,
    apply_suppressions,
    default_suppression_file,
    load_suppressions,
)


def scan_path(
    target: str | Path,
    profile: str = "balanced",
    suppression_file: str | Path | None = None,
) -> ScanResult:
    artifacts = normalize_all(collect(target))
    findings = RuleEngine(ALL_RULES).run(artifacts)
    target_root = Path(target).resolve()
    findings, inline_suppressed = apply_inline_suppressions(findings, artifacts)
    if suppression_file is None:
        suppression_file = default_suppression_file(target)
    suppressions = load_suppressions(suppression_file)
    findings, file_suppressed = apply_suppressions(findings, suppressions, target_root)
    suppressed = inline_suppressed + file_suppressed
    score_detail = score(findings, profile=profile)
    severity_counts = Counter(f.severity for f in findings)
    summary = {
        "artifacts_scanned": len(artifacts),
        "findings": len(findings),
        "critical": severity_counts.get("critical", 0),
        "high": severity_counts.get("high", 0),
        "medium": severity_counts.get("medium", 0),
        "low": severity_counts.get("low", 0),
        "suppressed": len(suppressed),
    }
    return ScanResult(
        target=str(Path(target).resolve()),
        profile=profile,
        trust_score=score_detail.final,
        verdict=verdict(score_detail.final),
        findings=findings,
        summary=summary,
        score=score_detail,
    )
