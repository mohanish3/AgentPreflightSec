from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Artifact:
    path: str
    kind: str  # mcp_config | skill_md | code_py | code_js | markdown | env_file | other
    content: str
    normalized_content: str = ""
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.normalized_content:
            self.normalized_content = self.content


@dataclass
class Finding:
    id: str
    severity: str  # critical | high | medium | low
    category: str
    title: str
    path: str
    evidence: str
    risk: str
    fix: str
    fix_available: bool = False
    line: int | None = None
    column: int | None = None
    end_line: int | None = None
    references: list[str] = field(default_factory=list)
    snippet_hash: str | None = None
    fix_mode: str | None = None
    patch_preview: str | None = None

    def _get_snippet(self) -> str:
        """Get normalized snippet for fingerprinting."""
        if self.snippet_hash:
            return self.snippet_hash
        return self.evidence

    def _get_relative_path(self) -> str:
        """Get repo-relative POSIX path."""
        return self.path.replace("\\", "/")


@dataclass
class ScoreDetail:
    base: int
    deductions: list[dict]
    caps_applied: list[str]
    final: int


@dataclass
class ScanResult:
    target: str
    profile: str
    trust_score: int
    verdict: str  # pass | warn | fail
    findings: list[Finding]
    summary: dict
    schema_version: str = "1.0"
    tool: str = "AgentPreflight"
    offline: bool = True
    score: ScoreDetail | None = None
