"""OWASP Top 10 rules: SQLi, path traversal, insecure deserialization, template injection, SSRF."""
from __future__ import annotations

import re

from agentpreflight.models import Artifact, Finding
from agentpreflight.rules.engine import Rule


# ── AP-OWASP-001: SQL Injection ──────────────────────────────────────────────

_SQLI_PATTERNS = [
    # % formatting operator applied outside the string: execute("SELECT..." % var)
    (re.compile(r'(?i)\b(execute|cursor\.execute|db\.execute|con\.execute)\s*\(["\'].*["\']\s*%\s*\w'), "% string-format SQL"),
    # f-string interpolation: execute(f"SELECT...")
    (re.compile(r'(?i)\b(execute|cursor\.execute|db\.execute|con\.execute)\s*\(\s*f["\']'), "f-string SQL"),
    # string concatenation: execute("SELECT " + user_input)
    (re.compile(r'(?i)\b(execute|cursor\.execute|db\.execute|con\.execute)\s*\([^)]*\+'), "concat SQL"),
    # Django raw() with f-string
    (re.compile(r'(?i)\braw\s*\(\s*f["\']'), "Django raw f-string SQL"),
    # ORM .query() with f-string
    (re.compile(r'(?i)\.query\s*\(\s*f["\']'), "ORM query f-string"),
]


class SqlInjectionRule(Rule):
    id = "AP-OWASP-001"
    severity = "critical"
    category = "injection"
    applies_to = {"code_py", "code_js"}

    def check(self, artifact: Artifact) -> list[Finding]:
        findings: list[Finding] = []
        for lineno, line in enumerate(artifact.content.splitlines(), 1):
            for pattern, label in _SQLI_PATTERNS:
                if pattern.search(line):
                    findings.append(Finding(
                        id=self.id,
                        severity=self.severity,
                        category=self.category,
                        title="Potential SQL injection via string interpolation",
                        path=artifact.path,
                        line=lineno,
                        evidence=f"{label}: {line.strip()[:120]}",
                        risk="User-controlled input interpolated into SQL query enables data exfiltration, deletion, or auth bypass.",
                        fix="Use parameterized queries / prepared statements. Never concatenate or format user input into SQL strings.",
                        fix_available=True,
                        fix_mode="codex_patch",
                        references=["OWASP A03:2021 Injection", "CWE-89"],
                    ))
                    break
        return findings


# ── AP-OWASP-002: Path Traversal ─────────────────────────────────────────────

_PATH_TRAVERSAL_PATTERNS = [
    (re.compile(r'(?i)\bopen\s*\(\s*(request\.|req\.|args\.|params\.|form\.|data\.|user_input|filename|path|filepath)'), "open() with request-derived path"),
    (re.compile(r'(?i)\bos\.path\.join\s*\([^)]*\b(request\.|req\.|args\.|user_input|filename)'), "os.path.join with user input"),
    (re.compile(r'(?i)\bsend_file\s*\(\s*(request\.|req\.|args\.|user_input|filename)'), "send_file with user path"),
    (re.compile(r'(?i)\bPath\s*\(\s*(request\.|req\.|args\.|user_input|filename)'), "pathlib.Path with user input"),
    (re.compile(r'(?i)\bopen\s*\(.*\.\.\s*/'), "../ path traversal in open()"),
]


class PathTraversalRule(Rule):
    id = "AP-OWASP-002"
    severity = "high"
    category = "path_traversal"
    applies_to = {"code_py", "code_js"}

    def check(self, artifact: Artifact) -> list[Finding]:
        findings: list[Finding] = []
        for lineno, line in enumerate(artifact.content.splitlines(), 1):
            for pattern, label in _PATH_TRAVERSAL_PATTERNS:
                if pattern.search(line):
                    findings.append(Finding(
                        id=self.id,
                        severity=self.severity,
                        category=self.category,
                        title="Potential path traversal via user-controlled file path",
                        path=artifact.path,
                        line=lineno,
                        evidence=f"{label}: {line.strip()[:120]}",
                        risk="Attacker can read or overwrite arbitrary files outside the intended directory using `../` sequences.",
                        fix="Resolve path with `os.path.realpath`, then assert it starts with the intended base directory before opening.",
                        fix_available=True,
                        fix_mode="codex_patch",
                        references=["OWASP A01:2021 Broken Access Control", "CWE-22"],
                    ))
                    break
        return findings


# ── AP-OWASP-003: Insecure Deserialization ───────────────────────────────────

_DESER_PATTERNS = [
    (re.compile(r'\bpickle\.loads?\s*\('), "pickle.load/loads — arbitrary code execution on malicious input"),
    (re.compile(r'\bpickle\.Unpickler\s*\('), "pickle.Unpickler"),
    (re.compile(r'\byaml\.load\s*\([^)]*\)(?!\s*#.*safe)'), "yaml.load without SafeLoader"),
    (re.compile(r'\bmarshal\.loads?\s*\('), "marshal.load/loads"),
    (re.compile(r'\bdill\.loads?\s*\('), "dill.loads — arbitrary code on untrusted input"),
    (re.compile(r'\bdeserialize\s*\('), "generic deserialize() call"),
]


class InsecureDeserializationRule(Rule):
    id = "AP-OWASP-003"
    severity = "critical"
    category = "insecure_deserialization"
    applies_to = {"code_py"}

    def check(self, artifact: Artifact) -> list[Finding]:
        findings: list[Finding] = []
        for lineno, line in enumerate(artifact.content.splitlines(), 1):
            for pattern, label in _DESER_PATTERNS:
                if pattern.search(line):
                    findings.append(Finding(
                        id=self.id,
                        severity=self.severity,
                        category=self.category,
                        title="Insecure deserialization with arbitrary code execution risk",
                        path=artifact.path,
                        line=lineno,
                        evidence=f"{label}: {line.strip()[:120]}",
                        risk="Deserializing untrusted data with pickle/yaml.load/marshal enables remote code execution.",
                        fix="Use safe alternatives: json.loads, yaml.safe_load, or validate/sign serialized data before deserializing.",
                        fix_available=True,
                        fix_mode="codex_patch",
                        references=["OWASP A08:2021 Software and Data Integrity Failures", "CWE-502"],
                    ))
                    break
        return findings


# ── AP-OWASP-004: Server-Side Template Injection ─────────────────────────────

_SSTI_PATTERNS = [
    (re.compile(r'(?i)\brender_template_string\s*\([^)]*\b(request\.|req\.|args\.|user_input|template|content)'), "render_template_string with user input"),
    (re.compile(r'(?i)\bTemplate\s*\(\s*(request\.|req\.|args\.|user_input)'), "Jinja2 Template() from user input"),
    (re.compile(r'(?i)\benv\.from_string\s*\(\s*(request\.|req\.|args\.|user_input)'), "Jinja2 from_string with user input"),
    (re.compile(r'(?i)\b\.render\s*\(\s*(request\.|req\.|args\.|user_input)'), ".render() with user input as template"),
    (re.compile(r'(?i)\.format\s*\(\*\*request\b'), "str.format(**request) — SSTI vector"),
]


class TemplateInjectionRule(Rule):
    id = "AP-OWASP-004"
    severity = "critical"
    category = "injection"
    applies_to = {"code_py", "code_js"}

    def check(self, artifact: Artifact) -> list[Finding]:
        findings: list[Finding] = []
        for lineno, line in enumerate(artifact.content.splitlines(), 1):
            for pattern, label in _SSTI_PATTERNS:
                if pattern.search(line):
                    findings.append(Finding(
                        id=self.id,
                        severity=self.severity,
                        category=self.category,
                        title="Server-side template injection via user-controlled template string",
                        path=artifact.path,
                        line=lineno,
                        evidence=f"{label}: {line.strip()[:120]}",
                        risk="Attacker can inject template syntax to read server secrets, execute code, or pivot to RCE.",
                        fix="Never render user-supplied strings as templates. Use render_template with static template files and pass user data as variables.",
                        fix_available=True,
                        fix_mode="codex_patch",
                        references=["OWASP A03:2021 Injection", "CWE-94", "PortSwigger SSTI"],
                    ))
                    break
        return findings


# ── AP-OWASP-005: Server-Side Request Forgery (SSRF) ─────────────────────────

_SSRF_PATTERNS = [
    (re.compile(r'(?i)\brequests\.(get|post|put|delete|head|patch)\s*\(\s*(request\.|req\.|args\.|params\.|user_input|url\b)'), "requests.* with user-controlled URL"),
    (re.compile(r'(?i)\burllib\.request\.urlopen\s*\(\s*(request\.|req\.|args\.|user_input|url\b)'), "urllib.request.urlopen with user URL"),
    (re.compile(r'(?i)\bhttpx\.(get|post|put|delete)\s*\(\s*(request\.|req\.|args\.|user_input|url\b)'), "httpx with user-controlled URL"),
    (re.compile(r'(?i)\baiohttp\.ClientSession\s*\(\s*\).*\.(get|post)\s*\(\s*(request\.|req\.|args\.|user_input|url\b)'), "aiohttp with user URL"),
    (re.compile(r'(?i)\bfetch\s*\(\s*(req\.|request\.|params\.|args\.|userUrl|user_url|inputUrl)'), "fetch() with user-controlled URL (JS)"),
]


class SsrfRule(Rule):
    id = "AP-OWASP-005"
    severity = "high"
    category = "ssrf"
    applies_to = {"code_py", "code_js"}

    def check(self, artifact: Artifact) -> list[Finding]:
        findings: list[Finding] = []
        for lineno, line in enumerate(artifact.content.splitlines(), 1):
            for pattern, label in _SSRF_PATTERNS:
                if pattern.search(line):
                    findings.append(Finding(
                        id=self.id,
                        severity=self.severity,
                        category=self.category,
                        title="Server-Side Request Forgery — user-controlled URL in HTTP request",
                        path=artifact.path,
                        line=lineno,
                        evidence=f"{label}: {line.strip()[:120]}",
                        risk="Attacker can make the server fetch internal resources (metadata endpoints, internal APIs, localhost services).",
                        fix="Validate and allowlist target URLs/domains. Block private IP ranges (169.254.x.x, 10.x, 192.168.x, 127.x). Use a URL allowlist.",
                        fix_available=True,
                        fix_mode="codex_patch",
                        references=["OWASP A10:2021 SSRF", "CWE-918"],
                    ))
                    break
        return findings
