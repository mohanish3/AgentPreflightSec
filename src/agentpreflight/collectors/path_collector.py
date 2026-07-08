from __future__ import annotations
from pathlib import Path

from agentpreflight.models import Artifact

IGNORE_DIRS = {".git", "node_modules", ".venv", "venv", "dist", "build", "__pycache__", ".mypy_cache"}

MAX_FILE_BYTES = 2_000_000  # skip files larger than 2 MB


def _classify(path: Path) -> str | None:
    name = path.name.lower()
    suffix = path.suffix.lower()

    if name in ("mcp.json", ".mcp.json"):
        return "mcp_config"
    if name in ("skill.md", "skills.md"):
        return "skill_md"
    if suffix == ".py":
        return "code_py"
    if suffix in (".js", ".ts", ".mjs", ".cjs"):
        return "code_js"
    if suffix in (".sh", ".bash", ".zsh"):
        return "code_sh"
    if suffix in (".md", ".mdx"):
        return "markdown"
    if name in (".env", ".env.local", ".env.production", ".env.development"):
        return "env_file"
    if name.endswith(".env") and not name.startswith(".env.example"):
        return "env_file"
    if suffix == ".json" and "mcp" in name:
        return "mcp_config"
    if suffix in (".json", ".yaml", ".yml", ".toml"):
        return "config"
<<<<<<< HEAD
    if name in ("requirements.txt", "requirements-dev.txt", "requirements_dev.txt", "requirements_test.txt", "requirements-test.txt"):
        return "dep_requirements"
    if name in ("package-lock.json",):
        return "dep_lock"
    if name in ("pipfile.lock", "poetry.lock"):
        return "dep_lock"
=======
>>>>>>> origin/main
    return None


def collect(target: str | Path) -> list[Artifact]:
    root = Path(target).resolve()
    artifacts: list[Artifact] = []

    if root.is_file():
        kind = _classify(root) or "other"
        try:
            content = root.read_text(encoding="utf-8", errors="replace")
            artifacts.append(Artifact(path=str(root), kind=kind, content=content))
        except OSError:
            pass
        return artifacts

    for dirpath, dirnames, filenames in root.walk() if hasattr(root, "walk") else _compat_walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for filename in filenames:
            filepath = Path(dirpath) / filename
            kind = _classify(filepath)
            if kind is None:
                continue
            try:
                if filepath.stat().st_size > MAX_FILE_BYTES:
                    continue
                content = filepath.read_text(encoding="utf-8", errors="replace")
                artifacts.append(Artifact(path=str(filepath), kind=kind, content=content))
            except OSError:
                pass

    return artifacts


def _compat_walk(root: Path):
    import os
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        yield Path(dirpath), dirnames, filenames
