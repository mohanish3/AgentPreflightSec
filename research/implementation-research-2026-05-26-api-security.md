# Implementation research - API security - 2026-05-26

## Repository research used

- `briefs/privacy-security-model.md`: API must preserve offline guarantees and avoid accidental remote exposure.
- `briefs/launch-checklist.md`: go-live gates need basic API safety before exposing service mode.
- `workflow.md`: FastAPI is last priority, but once added needs proof and clear limitations.

## Research conclusion

API mode should be opt-in and guarded. CLI remains primary product path, but service mode needs enough controls to avoid becoming a new attack surface.

Implemented minimal production-facing controls:

1. Optional API key via environment variable.
2. Header support for `x-agentpreflight-key` and `Authorization: Bearer`.
3. In-memory per-client rate limiting.
4. Offline-only scan enforcement.

## Implementation

- `AGENTPREFLIGHT_API_KEY` enables API key enforcement.
- `AGENTPREFLIGHT_RATE_LIMIT_PER_MINUTE` controls rate limit, default 60.
- `GET /healthz` remains unauthenticated for liveness.
- `POST /v1/scans` enforces API security and offline mode.

## Validation result

- `pytest`: 25 passed.
- Auth proof:
  - missing key -> 401
  - wrong key -> 403
  - correct key -> 200
- Rate-limit proof:
  - first request -> 200
  - second request with limit 1/min -> 429
- Screenshot: `validation/screenshots/api-security-proof.png`.
