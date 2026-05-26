from __future__ import annotations

import unicodedata

from agentpreflight.models import Artifact


SUSPICIOUS_CONTROLS = {
    "\u200b",
    "\u200c",
    "\u200d",
    "\ufeff",
    "\u202a",
    "\u202b",
    "\u202c",
    "\u202d",
    "\u202e",
    "\u2066",
    "\u2067",
    "\u2068",
    "\u2069",
}


def normalize_artifact(artifact: Artifact) -> Artifact:
    artifact.normalized_content = unicodedata.normalize("NFKC", artifact.content)
    artifact.metadata["suspicious_unicode_count"] = sum(
        1 for char in artifact.content if char in SUSPICIOUS_CONTROLS
    )
    return artifact


def normalize_all(artifacts: list[Artifact]) -> list[Artifact]:
    return [normalize_artifact(artifact) for artifact in artifacts]
