from __future__ import annotations

import json
import os
from pathlib import Path
import time
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

from agentpreflight.reporters import json_reporter
from agentpreflight.scanner import scan_path

app = FastAPI(title="AgentPreflight API", version="0.1.0")
_RATE_BUCKETS: dict[str, list[float]] = {}


class Target(BaseModel):
    type: Literal["path"] = "path"
    path: str


class ScanRequest(BaseModel):
    target: Target
    profile: Literal["dev", "balanced", "strict"] = "balanced"
    fail_on: Literal["low", "medium", "high", "critical"] | None = None
    formats: list[Literal["json", "sarif"]] = Field(default_factory=lambda: ["json"])
    offline: bool = True


def enforce_api_security(request: Request) -> None:
    expected_key = os.getenv("AGENTPREFLIGHT_API_KEY", "")
    supplied_key = _supplied_key(request)
    if expected_key:
        if not supplied_key:
            raise HTTPException(status_code=401, detail="missing API key")
        if supplied_key != expected_key:
            raise HTTPException(status_code=403, detail="invalid API key")
    _enforce_rate_limit(request, supplied_key or "anonymous")


def reset_rate_limits() -> None:
    _RATE_BUCKETS.clear()


def _supplied_key(request: Request) -> str:
    header_key = request.headers.get("x-agentpreflight-key", "")
    if header_key:
        return header_key
    auth = request.headers.get("authorization", "")
    if auth.lower().startswith("bearer "):
        return auth.split(" ", 1)[1].strip()
    return ""


def _enforce_rate_limit(request: Request, identity: str) -> None:
    limit_raw = os.getenv("AGENTPREFLIGHT_RATE_LIMIT_PER_MINUTE", "60")
    try:
        limit = int(limit_raw)
    except ValueError:
        limit = 60
    if limit <= 0:
        return
    now = time.monotonic()
    host = request.client.host if request.client else "unknown"
    bucket_key = f"{host}:{identity}"
    window_start = now - 60
    bucket = [item for item in _RATE_BUCKETS.get(bucket_key, []) if item >= window_start]
    if len(bucket) >= limit:
        _RATE_BUCKETS[bucket_key] = bucket
        raise HTTPException(status_code=429, detail="rate limit exceeded")
    bucket.append(now)
    _RATE_BUCKETS[bucket_key] = bucket


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/scans")
def create_scan(request: ScanRequest, _: None = Depends(enforce_api_security)) -> dict:
    if not request.offline:
        raise HTTPException(status_code=400, detail="remote triage is not implemented; offline must be true")
    target = Path(request.target.path)
    if not target.exists():
        raise HTTPException(status_code=404, detail="target path not found")
    result = scan_path(target, profile=request.profile)
    return json.loads(json_reporter.render(result))
