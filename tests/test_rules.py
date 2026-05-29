from __future__ import annotations

from agentpreflight.models import Artifact
from agentpreflight.rules.ap_code_001 import UnsafeShellRule
from agentpreflight.rules.ap_code_002 import DynamicCodeExecRule
from agentpreflight.rules.ap_sec_002 import ApiTokenRule
from agentpreflight.rules.ap_skill_002 import HiddenUnicodeRule
from agentpreflight.scorer.trust_score import score, verdict


def test_hidden_unicode_rule_detects_zero_width() -> None:
    artifact = Artifact(path="SKILL.md", kind="skill_md", content="visible\u200bhidden")

    findings = HiddenUnicodeRule().check(artifact)

    assert len(findings) == 1
    assert findings[0].id == "AP-SKILL-002"


def test_trojan_source_unicode_detected_in_python_code() -> None:
    # CVE-2021-42574: bidi override hides malicious logic in source code
    artifact = Artifact(
        path="tool.py",
        kind="code_py",
        content='access_level = "user\u202e \u2066# Check if admin\u2069 \u2066"\n',
    )

    findings = HiddenUnicodeRule().check(artifact)

    assert len(findings) == 1
    assert findings[0].id == "AP-SKILL-002"
    assert "CVE-2021-42574" in findings[0].references


def test_js_child_process_exec_detected() -> None:
    artifact = Artifact(
        path="server.js",
        kind="code_js",
        content='const child_process = require("child_process");\nchild_process.exec(userInput, callback);\n',
    )

    findings = UnsafeShellRule().check(artifact)

    assert len(findings) == 1
    assert findings[0].id == "AP-CODE-001"


def test_shell_eval_variable_detected() -> None:
    artifact = Artifact(
        path="run.sh",
        kind="code_sh",
        content='#!/bin/bash\neval "$USER_CMD"\n',
    )

    findings = DynamicCodeExecRule().check(artifact)

    assert len(findings) == 1
    assert findings[0].id == "AP-CODE-002"


def test_scoring_caps_critical_to_50() -> None:
    artifact = Artifact(path="SKILL.md", kind="skill_md", content="visible\u200bhidden")
    finding = HiddenUnicodeRule().check(artifact)[0]
    finding.severity = "critical"

    detail = score([finding])

    assert detail.final == 50
    assert verdict(detail.final) == "fail"


def test_aws_access_key_detected() -> None:
    artifact = Artifact(
        path="config.py",
        kind="code_py",
        content='AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"\n',
    )
    findings = ApiTokenRule().check(artifact)
    assert len(findings) == 1
    assert findings[0].id == "AP-SEC-002"


def test_anthropic_api_key_detected() -> None:
    artifact = Artifact(
        path="config.py",
        kind="code_py",
        content='api_key = "sk-ant-api03-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"\n',
    )
    findings = ApiTokenRule().check(artifact)
    assert len(findings) >= 1
    assert any(f.id == "AP-SEC-002" for f in findings)


def test_google_api_key_detected() -> None:
    artifact = Artifact(
        path="settings.json",
        kind="config",
        content='{"google_key": "AIzaSyBXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"}\n',
    )
    findings = ApiTokenRule().check(artifact)
    assert len(findings) == 1
    assert findings[0].id == "AP-SEC-002"


def test_strict_profile_escalates_medium_deduction_to_high_rate() -> None:
    from agentpreflight.models import Finding
    finding = Finding(
        id="AP-TEST",
        severity="medium",
        category="test",
        title="test",
        path="x.py",
        evidence="x",
        risk="x",
        fix="x",
    )
    balanced_detail = score([finding], profile="balanced")
    strict_detail = score([finding], profile="strict")

    assert balanced_detail.final == 100 - 7   # medium rate
    assert strict_detail.final == 100 - 15    # escalated to high rate
    # deductions list attributes points to 'high' bucket in strict mode
    high_bucket = next((d for d in strict_detail.deductions if d["severity"] == "high"), None)
    assert high_bucket is not None
    assert high_bucket["points"] == 15
    assert high_bucket["count"] == 1
