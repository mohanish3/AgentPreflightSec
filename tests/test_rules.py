from __future__ import annotations

from agentpreflight.models import Artifact
from agentpreflight.rules.ap_skill_002 import HiddenUnicodeRule
from agentpreflight.scorer.trust_score import score, verdict


def test_hidden_unicode_rule_detects_zero_width() -> None:
    artifact = Artifact(path="SKILL.md", kind="skill_md", content="visible\u200bhidden")

    findings = HiddenUnicodeRule().check(artifact)

    assert len(findings) == 1
    assert findings[0].id == "AP-SKILL-002"


def test_scoring_caps_critical_to_50() -> None:
    artifact = Artifact(path="SKILL.md", kind="skill_md", content="visible\u200bhidden")
    finding = HiddenUnicodeRule().check(artifact)[0]
    finding.severity = "critical"

    detail = score([finding])

    assert detail.final == 50
    assert verdict(detail.final) == "fail"
