# Scoring Formula: Risk Weighting & Trust Calculation

This document defines the mathematical model used by **AgentPreflight** to calculate a repository's **Trust Score (0–100)** based on static rule violations.

---

## 1. Core Trust Score Formula

Baseline score for a clean repository is **100**. Each violation deducts points by severity. Final score cannot fall below **0**:

```
Trust Score = max(0, 100 − Σ(Penalty per finding))
```

---

## 2. Severity Penalties

| Severity | Points deducted per finding |
|---|---|
| Critical | −30 |
| High | −15 |
| Medium | −7 |
| Low | −2 |

In `--profile strict` mode, medium findings are treated as high for scoring purposes.

---

## 3. Hard Caps

Caps apply after deductions. Multiple caps stack (lowest wins):

| Condition | Score cap |
|---|---|
| Any critical finding | ≤ 50 |
| ≥ 3 high findings | ≤ 60 |
| Any secrets finding | ≤ 55 |
| Unsafe shell + network egress combo | ≤ 45 |
| Unicode smuggling + prompt override combo | ≤ 50 |
| Privileged access + remote fetch combo | ≤ 45 |

A repository with a critical tool poisoning finding and clean everything else still cannot score above 50. No critical MCP flaw passes.

---

## 4. Verdict Thresholds

| Score | Verdict | CI outcome |
|---|---|---|
| 85–100 | pass | Exit 0 |
| 70–84 | warn | Exit 0 (warning logged) |
| 0–69 | fail | Exit 1 when `--fail-on` threshold met |

`--fail-on high` exits 1 if any high or critical findings exist, independent of score.

---

## 5. Example

Scan of `demo/poisoned` under `--profile strict`:

| Finding | Severity | Deduction |
|---|---|---|
| AP-MCP-001: prompt override in tool description | critical | −30 |
| AP-CODE-001: os.system with user input | critical | −30 |
| AP-CODE-003: curl \| bash remote pipe | high | −15 |
| AP-SEC-002: API token in .env | high | −15 |
| AP-SKILL-002: zero-width Unicode in SKILL.md | high | −15 |
| ... (10 more findings) | ... | ... |

Raw = 100 − (60 + 45 + ...) → 0 → cap at 50 (critical) → final = 0 (raw already ≤ 0)

Result: `trust_score=0 verdict=fail`
