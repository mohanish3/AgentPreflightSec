from __future__ import annotations

import subprocess
from pathlib import Path

from agentpreflight.collectors.path_collector import _classify
from agentpreflight.models import Artifact
from agentpreflight.rules.ap_dep_001 import (
    DependencyVulnRule,
    _parse_package_lock,
    _parse_requirements,
)


def test_requirements_manifest_is_parsed_locally() -> None:
    assert _parse_requirements(
        "# ignored\nrequests==2.32.3\nDjango>=5.0; python_version >= '3.10'\n-r base.txt\n"
    ) == [("requests", "2.32.3"), ("django", None)]


def test_npm_lockfile_is_parsed_locally() -> None:
    lock = '{"lockfileVersion":3,"packages":{"":{"name":"app"},"node_modules/lodash":{"version":"4.17.21"}}}'
    assert _parse_package_lock(lock) == [("lodash", "4.17.21")]
    legacy_lock = '{"lockfileVersion":1,"dependencies":{"left-pad":{"version":"1.3.0"}}}'
    assert _parse_package_lock(legacy_lock) == [("left-pad", "1.3.0")]


def test_supported_dependency_files_are_classified() -> None:
    assert _classify(Path("requirements-test.txt")) == "dep_requirements"
    assert _classify(Path("package-lock.json")) == "dep_lock"
    assert _classify(Path("poetry.lock")) is None


def test_default_dependency_scan_never_spawns_network_auditors(monkeypatch) -> None:
    def forbidden_process(*args, **kwargs):
        raise AssertionError("offline scans must not spawn audit subprocesses")

    monkeypatch.setattr(subprocess, "Popen", forbidden_process)
    rule = DependencyVulnRule()
    requirements = Artifact(path="requirements.txt", kind="dep_requirements", content="requests==2.32.3\n")
    npm_lock = Artifact(
        path="package-lock.json",
        kind="dep_lock",
        content='{"lockfileVersion":3,"packages":{"node_modules/lodash":{"version":"4.17.21"}}}',
    )

    assert rule.check(requirements) == []
    assert rule.check(npm_lock) == []
