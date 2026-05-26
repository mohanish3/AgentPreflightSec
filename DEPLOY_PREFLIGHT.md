# DeployPreflight: Infrastructure Redeploy Preflight

Status: **runner-up / future module**. Do not replace AgentPreflight as current winner. Ship only if MCP/skill scanner implementation stalls.

---

## Problem

Redeploys fail or create risk when repository configuration disagrees with the destination environment. The mismatch spans Dockerfile ports, app env vars, GitHub Actions secrets, Terraform provider regions, Kubernetes namespaces, Helm values, platform runtime versions, or Terraform plan deletes. Existing tools scan IaC, detect drift, or estimate cost — but developers still lack a simple preflight answer before redeploying.

What the tool would catch:
- Dockerfile exposes `8080`, platform expects `3000`
- app references `DATABASE_URL`, deploy workflow never sets it
- Terraform provider region differs from CI deploy region
- Helm values target one namespace, GitHub Action deploys another
- Terraform plan deletes database/storage without backup or snapshot policy
- Kubernetes resources exceed destination profile limits
- security group or ingress opens broader access than current config
- platform runtime version differs from app lockfile/runtime file

**Why current tools don't solve it:** Static IaC scanners find misconfigurations. Drift tools compare live vs desired state. Cost tools estimate spend. CI orchestrators run plans and applies. But developers still need: "If I redeploy this repo to this destination today, what will break, widen risk, or surprise me?" Most competitors own one layer, not the cross-file redeploy readiness workflow.

---

## Solution

DeployPreflight is a local-first destination-aware redeploy analyzer.

**Inputs:**
- repo path
- destination profile: `aws-ecs`, `eks`, `gke`, `vercel`, `render`, `fly`, `kubernetes`
- optional `terraform plan -json`, Kubernetes manifests, Helm values, GitHub Actions workflow, Dockerfile, `.env.example`
- optional read-only cloud/platform inventory

**Outputs:**
- readiness score
- blocker list with file/line evidence
- JSON/SARIF
- Codex patches for safe high-confidence fixes

---

## Four-day MVP

```bash
deploypreflight scan . --dest aws-ecs --env production
deploypreflight scan . --dest vercel --terraform-plan tfplan.json
deploypreflight fix blockers.json --apply
```

Collectors: Dockerfile, `.env.example`, package/runtime files, GitHub Actions, Terraform plan JSON, Kubernetes YAML, Helm values.

Rules: port mismatch, missing env var, missing GitHub secret reference, region mismatch, unsafe stateful delete, broad public ingress, runtime mismatch.

Fix command: port/env/secret/runtime mismatch (high-confidence only).

### 10x demo

1. Demo repo targets `aws-ecs/prod`.
2. Preflight finds container port mismatch, missing deploy secret, Terraform plan deleting stateful resource.
3. Readiness score below threshold.
4. Codex patch aligns port config, adds `.env.example` placeholder, adds policy gate for stateful deletes.
5. Rescan passes.

---

## Competitor landscape

This is a **mature, crowded market**. The 10x opportunity is not broad IaC scanning. It is destination-aware redeploy discrepancy analysis plus Codex patches.

Fresh 2026 pass found: Gomboc, Kestrel, DriftOps, DevPlus, ThreatMitigator, DriftHound — all use AI/remediation/drift language. DeployPreflight cannot claim remediation novelty.

### Top 10 competitors

| Rank | Competitor | Unique capability | Gap DeployPreflight targets |
|---:|---|---|---|
| 1 | Trivy | One scanner: IaC misconfig, secrets, vulns, SBOM, containers, Kubernetes. | No destination-specific redeploy readiness or repo patches for deploy mismatch. |
| 2 | HCP Terraform | Native plan/apply, health checks, drift detection. | Terraform-centric and platform-dependent; no cross-file analysis. |
| 3 | Checkov / Prisma Cloud | Rich IaC graph scanning across Terraform, CloudFormation, Kubernetes, Helm, Dockerfile. | Security/compliance first; not redeploy destination readiness. |
| 4 | Snyk IaC | IaC scanning + unmanaged resource/drift visibility and fix advice. | Enterprise focus; not lightweight destination profile patcher. |
| 5 | Spacelift | Drift detection/remediation inside IaC orchestration platform. | Requires platform adoption; not a drop-in repo analyzer. |
| 6 | env0 | Drift detection and AI drift-cause analysis. | Platform-centric; not local PR-first discrepancy patcher. |
| 7 | Firefly | Cloud asset inventory, drift, unmanaged resource discovery, IaC generation. | Needs cloud integration; heavier than hackathon MVP. |
| 8 | KICS | Multi-format IaC security scanner. | Finds policy violations, not destination-specific redeploy blockers. |
| 9 | Infracost | PR-native cloud cost estimates and guardrails. | Cost-only; not functional/security redeploy discrepancy. |
| 10 | Scalr | Terraform/OpenTofu drift detection with notifications. | Terraform platform scope; not cross-file app/IaC/CI/deploy readiness. |

New AI-adjacent infra competitors adding further pressure: Gomboc (deterministic Terraform scanning + remediation engine), Kestrel AI (reads live cloud and Terraform code → opens remediation PRs), DriftOps (AI-powered compliance/drift PR reports), DevPlus (AI agents for drift, cost, capacity), ThreatMitigator (AI-powered IaC threat modeling + drift + remediation), DriftHound (OSS Terraform/OpenTofu/Terragrunt drift detection).

Full URLs in `sources/source-register.md`.

---

## Evaluation

**Scorecard (1–10):**

| Criterion | DeployPreflight | AgentPreflight |
|---|---:|---:|
| Hackathon win potential | 6 | 8 |
| Feasibility | 7 | 8 |
| 10x workflow | 8 | 10 |
| Demo wow | 8 | 10 |
| Cost | 8 | 9 |
| Scale | 10 | 9 |
| Differentiation | 4 | 6 |
| **Total** | **51** | **60** |

**Why not winner for this hackathon:**
- Infra/IaC market is mature and crowded; fresh competitor pass found many AI-native rivals.
- Broad drift detection needs live cloud credentials and state access.
- Static repo-only checks risk feeling like another linter.
- Destination-aware discrepancy analysis is useful, but needs careful scoping.

**Best wedge if built:**

> "Will this repo redeploy cleanly to this destination?"

Ship only scoped to local repo + optional Terraform plan JSON + 4 destination profiles + Codex patch/rescan loop. Skip live cloud drift.
