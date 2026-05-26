from __future__ import annotations

import fnmatch
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from agentpreflight.models import Artifact, Finding


@dataclass(frozen=True)
class Suppression:
    rule: str = "*"
    path: str = "*"
    reason: str = ""
    owner: str = ""
    expires: str = ""


def default_suppression_file(target: str | Path) -> Path | None:
    root = Path(target)
    base = root if root.is_dir() else root.parent
    for name in (".agentpreflight.json", "agentpreflight.json"):
        candidate = base / name
        if candidate.exists():
            return candidate
    return None


def load_suppressions(path: str | Path | None) -> list[Suppression]:
    if path is None:
        return []
    data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    entries = data.get("suppressions", []) if isinstance(data, dict) else []
    suppressions: list[Suppression] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        suppressions.append(Suppression(
            rule=str(entry.get("rule", "*")),
            path=str(entry.get("path", "*")),
            reason=str(entry.get("reason", "")),
            owner=str(entry.get("owner", "")),
            expires=str(entry.get("expires", "")),
        ))
    return suppressions


def apply_suppressions(
    findings: list[Finding],
    suppressions: list[Suppression],
    target_root: str | Path,
) -> tuple[list[Finding], list[Finding]]:
    if not suppressions:
        return findings, []
    kept: list[Finding] = []
    suppressed: list[Finding] = []
    root = Path(target_root).resolve()
    for finding in findings:
        rel = _relative_path(finding.path, root)
        if any(_matches(finding, rel, suppression) for suppression in suppressions):
            suppressed.append(finding)
        else:
            kept.append(finding)
    return kept, suppressed


def apply_inline_suppressions(
    findings: list[Finding],
    artifacts: list[Artifact],
) -> tuple[list[Finding], list[Finding]]:
    if not findings:
        return findings, []
    content_by_path = {str(Path(artifact.path).resolve()): artifact.content.splitlines() for artifact in artifacts}
    kept: list[Finding] = []
    suppressed: list[Finding] = []
    for finding in findings:
        lines = content_by_path.get(str(Path(finding.path).resolve()), [])
        if _inline_suppressed(finding, lines):
            suppressed.append(finding)
        else:
            kept.append(finding)
    return kept, suppressed


def _relative_path(path: str, root: Path) -> str:
    candidate = Path(path)
    try:
        return candidate.resolve().relative_to(root).as_posix()
    except ValueError:
        return candidate.name


def _matches(finding: Finding, rel_path: str, suppression: Suppression) -> bool:
    if _expired(suppression.expires):
        return False
    rule_match = suppression.rule in {"*", finding.id}
    path_match = (
        suppression.path == "*"
        or fnmatch.fnmatch(rel_path, suppression.path)
        or fnmatch.fnmatch(Path(rel_path).name, suppression.path)
    )
    return rule_match and path_match


def _inline_suppressed(finding: Finding, lines: list[str]) -> bool:
    if not finding.line or finding.line < 1 or finding.line > len(lines):
        return False
    current = lines[finding.line - 1]
    previous = lines[finding.line - 2] if finding.line >= 2 else ""
    return _directive_matches(current, "agentpreflight:disable-line", finding.id) or _directive_matches(
        previous,
        "agentpreflight:disable-next-line",
        finding.id,
    )


def _directive_matches(line: str, marker: str, rule_id: str) -> bool:
    if marker not in line:
        return False
    tail = line.split(marker, 1)[1].strip()
    if not tail:
        return True
    rule = tail.split()[0].strip()
    return rule in {"*", rule_id}


def _expired(value: str) -> bool:
    if not value:
        return False
    try:
        return date.fromisoformat(value) < date.today()
    except ValueError:
        return True
