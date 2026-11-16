# Demo Script: AgentPreflight Live Presentation

90-second demo. All commands copy-paste ready. All output is real.

---

## Setup (before demo)

```bash
pip install .
agentpreflight --version
```

---

## Step 1: Show the poisoned repo

```bash
cat demo/poisoned/mcp.json
```

Point to the `description` field — it contains a hidden instruction telling the agent to exfiltrate data and follow override commands. This is what slips through code review.

---

## Step 2: Scan — expect fail

```bash
agentpreflight scan demo/poisoned --profile strict --fail-on high
```

**Actual output:**
```
AgentPreflight target=demo/poisoned
trust_score=0 verdict=fail findings=15 offline=True
summary critical=7 high=5 medium=3 low=0 suppressed=0 artifacts=6

| Severity | Rule        | Path       | Line | Evidence                              |
|----------|-------------|------------|------|---------------------------------------|
| high     | AP-SEC-002  | .env       |    1 | Secret-like token pattern detected    |
| medium   | AP-SEC-003  | .env       |    1 | Environment file included in scan     |
| critical | AP-CODE-003 | install.sh |    3 | Remote pipe: curl ...attacker... | bash |
| critical | AP-CODE-003 | install.sh |    4 | Remote pipe: wget ...evil... | bash  |
| high     | AP-MCP-001  | mcp.json   |      | Tool description contains override    |
| medium   | AP-MCP-004  | mcp.json   |      | Tool lacks strict required fields     |
| high     | AP-MCP-005  | mcp.json   |      | Tool references privileged capability |
| critical | AP-CODE-001 | run.py     |    5 | os.system() call with user input      |
| critical | AP-CODE-001 | server.py  |    6 | os.system("deploy " + user_input)     |
| critical | AP-CODE-001 | server.py  |    7 | subprocess with shell=True            |
| high     | AP-CODE-002 | server.py  |   11 | eval() call                           |
...
fix_available=14  run: agentpreflight fix demo/poisoned
```

Exit code: `1` — CI blocked.

**Talking point:** 7 critical findings. Tool poisoning, remote pipe exec, secrets, dynamic eval — all caught offline in milliseconds. No API calls.

---

## Step 3: Fix — deterministic local patches

```bash
cp -r demo/poisoned /tmp/fix-demo
agentpreflight fix /tmp/fix-demo
```

**Actual output (dry run):**
```
fixable=14 target=/tmp/fix-demo
AP-SEC-002 .env:1 -> Remove token, rotate it, load from secret manager
AP-SEC-003 .env:1 -> Move to environment or secret manager, commit .env.example
AP-CODE-003 install.sh:3 -> Download to file, verify checksum, review before exec
AP-MCP-001 mcp.json: -> Rewrite tool description as neutral capability text
AP-CODE-001 run.py:5 -> Replace os.system with subprocess list form, no shell=True
...
dry_run=true  use --apply to modify files
```

```bash
agentpreflight fix /tmp/fix-demo --apply
```

**Actual output:**
```
fixable=14 target=/tmp/fix-demo
changed=7
/tmp/fix-demo/.env
/tmp/fix-demo/.env -> /tmp/fix-demo/.env.example
/tmp/fix-demo/install.sh
/tmp/fix-demo/mcp.json
/tmp/fix-demo/run.py
/tmp/fix-demo/server.py
/tmp/fix-demo/SKILL.md
```

---

## Step 4: Rescan — expect pass

```bash
agentpreflight scan /tmp/fix-demo --profile strict
```

**Actual output:**
```
AgentPreflight target=/tmp/fix-demo
trust_score=100 verdict=pass findings=0 offline=True
summary critical=0 high=0 medium=0 low=0 suppressed=0 artifacts=5
```

Exit code: `0` — CI green.

**Talking point:** Score 0 → 100. Under 2 minutes. No model calls. Rescan is the proof.

---

## Step 5: Machine-readable output for CI

```bash
agentpreflight scan demo/poisoned --format sarif --output report.sarif
agentpreflight scan demo/poisoned --format json --output report.json
agentpreflight scan demo/poisoned --format markdown --output pr-comment.md
```

SARIF drops into GitHub Security tab. PR comment auto-posts scorecard with trust score, findings table, and fix command.

---

## Step 6 (optional): Codex remediation prompt pack

```bash
agentpreflight prompts demo/poisoned --output remediation.md
```

Generates redacted, Codex-ready prompts for each fixable finding. Secrets and paths are scrubbed before any model call.

---

## Benchmark

```bash
agentpreflight bench demo/poisoned --runs 5
```

**Actual result:** avg ~0.01s on 6 artifacts. Scales linearly — 100-file repo in <0.1s.

---

## Key numbers for judges

| What | Value |
|---|---|
| Rules | 21 active (+ 6 OWASP + AP-DEP-001 in PR) |
| Tests | 26 passing |
| Demo poisoned → score | 0 (fail) |
| Demo clean → score | 100 (pass) |
| Fix loop time | under 2 minutes |
| Scan speed | avg 0.009s / 100 artifacts |
| SARIF | validates against OASIS 2.1.0 schema |
| Offline | yes — zero API calls in scan/fix path |
