"""AP-DEP-001: Known vulnerabilities in declared dependencies (pip-audit / npm audit)."""
from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

from agentpreflight.models import Artifact, Finding
from agentpreflight.rules.engine import Rule


def _run_pip_audit(requirements_text: str, source_path: str) -> list[Finding]:
    findings: list[Finding] = []
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as tmp:
        tmp.write(requirements_text)
        tmp_path = tmp.name
    try:
        result = subprocess.run(
            ["pip-audit", "--format", "json", "--requirement", tmp_path, "--skip-editable"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        raw = result.stdout.strip()
        if not raw:
            return []
        data = json.loads(raw)
        dependencies = data if isinstance(data, list) else data.get("dependencies", [])
        for dep in dependencies:
            name = dep.get("name", "unknown")
            version = dep.get("version", "?")
            for vuln in dep.get("vulns", []):
                vid = vuln.get("id", "UNKNOWN")
                description = vuln.get("description", "No description available.")
                fix_versions = vuln.get("fix_versions", [])
                fix_str = f"Upgrade to {', '.join(fix_versions)}" if fix_versions else "No fix available — review and consider alternative"
                severity = _map_severity(vid)
                findings.append(Finding(
                    id="AP-DEP-001",
                    severity=severity,
                    category="dependency_vulnerability",
                    title=f"Known vulnerability in {name}=={version}: {vid}",
                    path=source_path,
                    evidence=f"{name}=={version} has {vid}: {description[:200]}",
                    risk=f"Dependency {name}=={version} has a known CVE/vulnerability that could be exploited in production.",
                    fix=fix_str,
                    fix_available=bool(fix_versions),
                    references=[f"https://osv.dev/vulnerability/{vid}"],
                ))
    except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
        pass
    finally:
        Path(tmp_path).unlink(missing_ok=True)
    return findings


def _run_npm_audit(package_lock_text: str, source_path: str) -> list[Finding]:
    findings: list[Finding] = []
    with tempfile.TemporaryDirectory() as tmpdir:
        lock_path = Path(tmpdir) / "package-lock.json"
        lock_path.write_text(package_lock_text, encoding="utf-8")
        pkg_path = Path(tmpdir) / "package.json"
        pkg_path.write_text('{"name":"audit-target","version":"0.0.0"}', encoding="utf-8")
        try:
            result = subprocess.run(
                ["npm", "audit", "--json"],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=tmpdir,
            )
            raw = result.stdout.strip()
            if not raw:
                return []
            data = json.loads(raw)
            vulnerabilities = data.get("vulnerabilities", {})
            for pkg_name, vuln_info in vulnerabilities.items():
                severity = vuln_info.get("severity", "medium")
                via = vuln_info.get("via", [])
                for item in via:
                    if not isinstance(item, dict):
                        continue
                    vid = item.get("url", item.get("source", ""))
                    title = item.get("title", "Unknown vulnerability")
                    description = item.get("title", "No description.")
                    fix_available = bool(data.get("metadata", {}).get("vulnerabilities", {}).get("fixable", 0))
                    findings.append(Finding(
                        id="AP-DEP-001",
                        severity=_js_severity(severity),
                        category="dependency_vulnerability",
                        title=f"Known vulnerability in {pkg_name}: {title}",
                        path=source_path,
                        evidence=f"{pkg_name}: {description[:200]}",
                        risk=f"npm dependency {pkg_name} has a known vulnerability exploitable at runtime.",
                        fix=f"Run `npm audit fix` or upgrade {pkg_name}",
                        fix_available=fix_available,
                        references=[vid] if vid.startswith("http") else [],
                    ))
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
            pass
    return findings


def _map_severity(vuln_id: str) -> str:
    vid_upper = vuln_id.upper()
    if vid_upper.startswith("GHSA"):
        return "high"
    if vid_upper.startswith("CVE"):
        return "high"
    if vid_upper.startswith("PYSEC"):
        return "high"
    return "medium"


def _js_severity(npm_sev: str) -> str:
    return {"critical": "critical", "high": "high", "moderate": "medium", "low": "low"}.get(npm_sev, "medium")


class DependencyVulnRule(Rule):
    id = "AP-DEP-001"
    severity = "high"
    category = "dependency_vulnerability"
    applies_to = {"dep_requirements", "dep_lock"}

    def check(self, artifact: Artifact) -> list[Finding]:
        name = Path(artifact.path).name.lower()
        if name in ("requirements.txt", "requirements-dev.txt", "requirements_dev.txt", "requirements_test.txt"):
            return _run_pip_audit(artifact.content, artifact.path)
        if name == "package-lock.json":
            return _run_npm_audit(artifact.content, artifact.path)
        return []
