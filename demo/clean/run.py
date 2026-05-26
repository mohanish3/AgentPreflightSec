import subprocess
from pathlib import Path


def install_deps(requirements_file: Path) -> None:
    subprocess.run(
        ["pip", "install", "-r", str(requirements_file)],
        check=True,
    )


def setup_environment(config_path: Path) -> dict:
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    import json
    return json.loads(config_path.read_text())
