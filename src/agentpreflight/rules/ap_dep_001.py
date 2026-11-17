"""AP-DEP-001 dependency manifest inventory.

The scanner is offline by default and has no bundled advisory database. These
manifests are parsed locally; vulnerability findings are deferred until the
project can provide an offline advisory source or an explicit network opt-in.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from agentpreflight.models import Artifact
from agentpreflight.rules.engine import Rule

_REQUIREMENT = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)(?:\[[^\]]+\])?\s*(?:==\s*([^\s;]+))?")


def _parse_requirements(content: str) -> list[tuple[str, str | None]]:
    """Return pinned/unpinned package declarations without resolving or fetching."""
    dependencies: list[tuple[str, str | None]] = []
    for raw_line in content.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line or line.startswith(("-", ".", "/")):
            continue
        match = _REQUIREMENT.match(line)
        if match:
            dependencies.append((match.group(1).lower(), match.group(2)))
    return dependencies


def _parse_package_lock(content: str) -> list[tuple[str, str | None]]:
    """Read package names and versions from npm lockfile v1, v2, or v3 JSON."""
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return []

    dependencies: list[tuple[str, str | None]] = []
    if not isinstance(data, dict):
        return []
    packages = data.get("packages")
    if isinstance(packages, dict) and packages:
        for lock_path, package in packages.items():
            if not isinstance(package, dict) or not lock_path.startswith("node_modules/"):
                continue
            name = package.get("name")
            if not isinstance(name, str) or not name:
                name = lock_path.rsplit("node_modules/", 1)[-1]
            version = package.get("version")
            dependencies.append((name, version if isinstance(version, str) else None))
        return sorted(dependencies)

    def visit(entries: object) -> None:
        if not isinstance(entries, dict):
            return
        for name, package in entries.items():
            if not isinstance(package, dict):
                continue
            version = package.get("version")
            dependencies.append((name, version if isinstance(version, str) else None))
            visit(package.get("dependencies"))

    visit(data.get("dependencies"))
    return sorted(dependencies)


class DependencyVulnRule(Rule):
    id = "AP-DEP-001"
    severity = "high"
    category = "dependency_vulnerability"
    applies_to = {"dep_requirements", "dep_lock"}

    def check(self, artifact: Artifact) -> list:
        name = Path(artifact.path).name.lower()
        if name in (
            "requirements.txt",
            "requirements-dev.txt",
            "requirements_dev.txt",
            "requirements_test.txt",
            "requirements-test.txt",
        ):
            _parse_requirements(artifact.content)
        elif name == "package-lock.json":
            _parse_package_lock(artifact.content)
        # A CVE verdict cannot be made deterministically without advisory data.
        # Do not invoke pip-audit/npm audit here: they make network requests.
        return []
