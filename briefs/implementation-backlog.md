# Implementation Backlog: P0-P3 Priority Queue & Cuts

This document defines the Prioritized Implementation Backlog, product trade-offs, and stretch scopes for the 4-day **AgentPreflight** build.

---

## 1. Backlog Queue

### Priority P0: Core Parser & First 15 Rules (Day 1)
- [ ] **AP-B-001**: Build config Collectors (crawl target folders, read `mcp.json` and `SKILL.md`).
- [ ] **AP-B-002**: Implement Unicode Normalizer (canonical NFKC format, strip zero-width obfuscations).
- [ ] **AP-B-003**: Code first 15 deterministic rules (imperative overrides, homoglyph lookups, raw `os.system` strings).
- [ ] **AP-B-004**: Establish CLI base (argument parsing, color-coded stdout reports).

### Priority P1: Scorer, SARIF, & Test Harness (Day 2)
- [ ] **AP-B-005**: Scoring Engine (implement severity weighting, calculate Trust Score 0-100).
- [ ] **AP-B-006**: Structured Reporters (format output to standard JSON and GitHub-compliant SARIF).
- [ ] **AP-B-007**: Test Suite (create malicious and benign extension fixtures, run baseline assertions).
- [ ] **AP-B-008**: Local Suppressions (allow inline `# aisafe:disable-line` annotations).

### Priority P2: FastAPI Webhook & Codex Remediations (Day 3)
- [ ] **AP-B-009**: FastAPI Scanner API (`POST /v1/scans` endpoint).
- [ ] **AP-B-010**: Codex Patch Engine (prompt templates to generate diff patches for tool/script findings).
- [ ] **AP-B-011**: GitHub Action (wrap CLI in an action, comment on PRs with a scan scorecard).

### Priority P3: Stretch Goals & Post-MVP (Day 4+)
- [ ] **AP-B-012**: Tree-Sitter AST Scanner (parse complex multi-file Python/TS AST graphs).
- [ ] **AP-B-013**: Dynamic Docker Sandbox (**Pivoted to Stretch**; containerize extension executions, capture `iptables` egress).

---

## 2. Product Cuts & Trade-offs

To guarantee a robust, production-ready release in under 4 days, we made three critical cuts:
1. **Dynamic Sandbox Sandbox (Docker/eBPF)**: Deferred to a P3 stretch goal. Tracing kernel subprocesses and instrumenting `iptables` inside transient Docker containers raises severe platform-dependency and delivery risk for a 4-day build.
2. **Broad RAG Document Processing**: RAG document ingestion sanitizing is cut completely. Prisma AIRS operates in this crowded space, and constructing HTML/PDF extractors increases scope creep.
3. **Advanced Prompt Leakage dynamic red-teaming**: Excluded dynamic, multi-turn LLM exfiltration probes (like Garak), keeping prompt checks strictly static (regex/dictionary) to maintain sub-second CLI scan speeds.
