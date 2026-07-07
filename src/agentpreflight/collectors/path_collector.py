from __future__ import annotations
from pathlib import Path
import logging
import os

from agentpreflight.models import Artifact

IGNORE_DIRS = {".git", "node_modules", ".venv", "venv", "dist", "build", "__pycache__", ".mypy_cache"}

logger = logging.getLogger(__name__)

# Default max file size - can be overridden via environment variable
DEFAULT_MAX_FILE_BYTES = 2_000_000  # 2 MB


def _get_max_file_bytes() -> int:
    """Get max file size from environment or use default."""
    env_size = os.getenv("AGENTPREFLIGHT_MAX_FILE_SIZE")
    if env_size:
        try:
            return int(env_size)
        except ValueError:
            pass  # Fall back to default
    return DEFAULT_MAX_FILE_BYTES


def _is_binary_file(filepath: Path) -> bool:
    """Check if a file is binary by sniffing for null bytes in the first 8KB."""
    try:
        with open(filepath, "rb") as f:
            chunk = f.read(8192)
            return b"\x00" in chunk
    except (IOError, OSError):
        return False


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
    return None


def collect(target: str | Path) -> list[Artifact]:
    root = Path(target).resolve()
    artifacts: list[Artifact] = []
    max_file_size = _get_max_file_bytes()

    if root.is_file():
        kind = _classify(root) or "other"
        # Skip binary files
        if _is_binary_file(root):
            logger.debug("Skipping binary file: %s", root)
            return artifacts
        # Skip files larger than max size
        if root.stat().st_size > max_file_size:
            logger.debug("Skipping file too large (%d bytes > %d): %s", 
                       root.stat().st_size, max_file_size, root)
            return artifacts
        try:
            content = root.read_text(encoding="utf-8", errors="replace")
            artifacts.append(Artifact(path=str(root), kind=kind, content=content))
        except OSError as e:
            logger.debug("Failed to read file %s: %s", root, e)
        return artifacts

    for dirpath, dirnames, filenames in root.walk() if hasattr(root, "walk") else _compat_walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for filename in filenames:
            filepath = Path(dirpath) / filename
            kind = _classify(filepath)
            if kind is None:
                continue
            # Skip files larger than max size first (faster check)
            if filepath.stat().st_size > max_file_size:
                logger.debug("Skipping file too large (%d bytes > %d): %s", 
                           filepath.stat().st_size, max_file_size, filepath)
                continue
            # Skip binary files
            if _is_binary_file(filepath):
                logger.debug("Skipping binary file: %s", filepath)
                continue
            try:
                content = filepath.read_text(encoding="utf-8", errors="replace")
                artifacts.append(Artifact(path=str(filepath), kind=kind, content=content))
            except OSError as e:
                logger.debug("Failed to read file %s: %s", filepath, e)

    return artifacts


def _compat_walk(root: Path):
    import os
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        yield Path(dirpath), dirnames, filenames
