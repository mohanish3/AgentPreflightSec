# Scoring Formula: Risk Weighting & Trust Calculation

This document defines the mathematical models used by **AgentPreflight** to calculate a repository's **Trust Score (0 - 100)** based on static rule violations.

---

## 1. Core Trust Score Formula

The baseline score of a clean, unviolated repository is **100**. For each violation detected, the scoring engine applies a penalty based on severity. The final score cannot fall below **0**:

$$\text{Trust Score} = \max\left(0, 100 - \sum (\text{Penalty}_{\text{Severity}})\right)$$

---

## 2. Severity Penalties

We assign standard, static weights to each severity classification:

- **Critical**: **30 Points** (High execution hazard, e.g. command injection, prompt-injected override)
- **High**: **15 Points** (System boundary exposure, e.g. hardcoded secrets, zero-width obfuscation)
- **Medium**: **5 Points** (Transport vulnerability, e.g. broad network binds, missing auth)
- **Low**: **1 Point** (Minor posture observations, e.g. missing metadata tags)

---

## 3. Decaying Compounding Violations

To prevent a repository from bottoming out at 0 due to repetitive occurrences of the same finding (for example, 5 separate warnings of the same localhost bind), we apply a **decay coefficient** ($\delta = 0.5$) for secondary instances of a specific Rule ID:

$$\text{Total Penalty}_{\text{Rule ID}} = \text{Penalty}_{\text{Base}} \times \left(1 + \sum_{i=2}^{N} \delta^{i-1}\right)$$

Where:
- $\text{Penalty}_{\text{Base}}$ is the standard penalty weight for the rule's severity.
- $N$ is the count of occurrences of that specific Rule ID.
- $\delta$ is the decay factor (fixed at `0.5`).

### Example Calculation:
If a scan finds **three High** violations of `AP-SR-001` (Secrets):
- 1st finding: $15$ points
- 2nd finding: $15 \times 0.5 = 7.5$ points
- 3rd finding: $15 \times 0.25 = 3.75$ points
- **Total deduction**: $15 + 7.5 + 3.75 = 26.25 \to 26$ points.
- **Trust Score**: $100 - 26 = 74$.

This compounding decay model ensures the score is highly reflective of overall project security without penalizing repeating instances excessively.
