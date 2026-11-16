# Scoring Formula: Risk Weighting & Trust Calculation

This document defines the mathematical model used by **AgentPreflight** to calculate a repository's **Trust Score (0–100)** based on static rule violations.

---

## 1. Core Trust Score Formula

The baseline score of a clean, unviolated repository is **100**. For each violation detected, the scoring engine applies a flat penalty based on severity. The final score cannot fall below **0**:

```
Trust Score = max(0, 100 − Σ Penalty(severity_i))
```

Under `--profile strict`, medium findings are escalated to high before deduction:

```
effective_severity = "high" if (profile == "strict" and severity == "medium") else severity
```

---

## 2. Severity Penalties

Each finding deducts a flat penalty regardless of how many times the same rule fires:

| Severity | Points deducted |
|---|---|
| Critical | 30 |
| High | 15 |
| Medium | 7 |
| Low | 2 |

---

## 3. Hard Caps

After deductions, combo caps apply if certain dangerous conditions are present:

| Condition | Score cap |
|---|---|
| Any critical finding | ≤ 50 |
| 3 or more high findings | ≤ 60 |
| Any secret finding (AP-SEC-001/002) | ≤ 55 |
| Unsafe shell + network egress (AP-CODE-001 + AP-CODE-005/AP-NET-001) | ≤ 45 |
| Hidden Unicode + prompt override (AP-SKILL-002 + AP-MCP-001/AP-SKILL-001) | ≤ 50 |
| Privileged tool + remote fetch (AP-MCP-005 + AP-SKILL-003/AP-CODE-003) | ≤ 45 |

Multiple caps trigger independently; the lowest applies.

---

## 4. Verdicts

| Score range | Verdict |
|---|---|
| 85–100 | pass |
| 70–84 | warn |
| 0–69 | fail |

---

## 5. Example

Repository with 2 critical + 3 high + 1 medium findings (balanced profile):

```
Deductions: 2×30 + 3×15 + 1×7 = 60 + 45 + 7 = 112
Raw: max(0, 100 − 112) = 0
Trust Score: 0   verdict: fail
```

Repository with 1 high + 2 medium findings (balanced profile):

```
Deductions: 1×15 + 2×7 = 15 + 14 = 29
Raw: 100 − 29 = 71
No caps triggered.
Trust Score: 71   verdict: warn
```
