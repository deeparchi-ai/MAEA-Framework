
## §2 Regulator — Resource Governance

> IBM lineage: **WLM** (Workload Manager)

Goal-oriented resource scheduling for agent workloads. Traditional schedulers
ask "how much resource does each agent get?" Regulator asks "what is each
agent's goal, and how important is it?"

### Architecture: Observe → Arbitrate → Apply

**Observe** reads pressure signals — `cpu.pressure` from Linux PSI for CPU
mode, burn rate vs daily budget for token mode. **Arbitrate** applies
importance: high-importance agents whose targets are unmet take resources
from low-importance agents whose targets are satisfied. **Apply** translates
the decision into enforcement — `cpu.weight` for CPU, API-level rate
limiting for tokens.

### Token Degradation Model

| Level | Condition | Action |
|:-----:|-----------|--------|
| **Green** | Budget ample | Allow |
| **Yellow** | Burn rate elevated | Allow + suggest smaller model |
| **Red** | Budget tight | Rate-limit; auto-degrade model tier |
| **Black** | Budget exhausted | Only importance-1 agents may call |

### Model Failover

When Gauge (§9) detects a vendor outage, Regulator decides the failover chain:
Primary → Audit → Tertiary. This follows the "两地三中心" (two-site-three-center)
model: production (Primary), hot standby (Audit), cold standby (Tertiary).

**Implementation:** [deeparchi-ai/wlm](https://github.com/deeparchi-ai/wlm) — 34 tests

---

## §3 Sanctum — Access Control & Trust

> IBM lineage: **RACF** (Resource Access Control Facility)

### Four Security Layers

| Layer | Type | Mechanism |
|:-----:|------|-----------|
| L1 | Onboarding review | Topology check, capability conflict detection, L-level assignment |
| L2 | Static boundaries | L1/L2/L3 access levels, cross-level rules, downward-only delegation |
| L3 | Behavioral trust | Five trust signals → trust score (0.0–1.0) → Trusted/Probationary/Restricted/Suspended |
| L4 | Hard constraints (Genes) | Six kernel-enforced constraints. Cannot be bypassed by any code path. Violation → circuit breaker → agent disabled. |

### §3b Loom — Causal-DAG Rollback

> IBM lineage: **CICS Syncpoint**

Transactional integrity for multi-agent workflows. When an orchestrator spawns
N subagents and one fails, Loom undoes only the failed branch — preserving
independent branches via fork-point snapshots. Two-phase commit protocol
with compensating actions for irreversible resources (payments, tweets).

**Implementation:** [deeparchi-ai/macs-state-go](https://github.com/deeparchi-ai/macs-state-go) — 12 tests

---

## §4 Chronicle — Audit & Trace

> IBM lineage: **SMF** (System Management Facilities)

Every cross-agent event that changes state, consumes resources, or makes a
decision MUST produce an audit record. Chronicle provides:

- **W3C traceparent** propagation across A2A ServiceParams
- **Cross-protocol bridge**: A2A↔MCP trace context via `params._meta.traceparent`
- **Decision receipts**: append-only hash chain (SEP #3004 compatible)
- **DUMP**: frozen decision-chain snapshot on trigger (SLIP traps)

**Implementation:**
- [a2a-go PR #377](https://github.com/a2aproject/a2a-go/pull/377) — 20 tests
- [deeparchi-ai/mcp-audit-go](https://github.com/deeparchi-ai/mcp-audit-go) — 10 tests (SEP #3004)
- [deeparchi-ai/trace-bridge-go](https://github.com/deeparchi-ai/trace-bridge-go) — 19 tests
- `macs/dump/` — Python, Hermes plugin (19 tests)

---

## §5 XVal — Tri-Model Cross-Validation

> **No IBM lineage.** COBOL programs compile. Agent outputs don't.

### 5.1 Three-Model Architecture

Follows the banking "两地三中心" (two-site-three-center) disaster recovery
model applied to LLM vendors:

```
Primary Model     Audit Model       Tertiary Model
(Production)      (Hot Standby)     (Cold Standby)
     │                 │                  │
     ▼                 ▼                  ▼
  ┌─────────────────────────────────────────┐
  │           Tri-Model Adjudication         │
  │                                         │
  │  3/3 Consensus  →  L1 Auto-Accept       │
  │  2/3 Majority   →  L2 Flagged + Execute │
  │  1/3 or 0/3    →  L3 Escalate to Human │
  └─────────────────────────────────────────┘
```

**Why three models?** Two models can only produce agree/disagree. Three models
produce consensus/majority/stalemate — richer signal. 2:1 majority means the
majority view is statistically stronger than a single dissenter, but the
minority opinion is preserved for human review.

### 5.2 Vendor Diversity

All three models MUST be from different vendors. Same-vendor pairing is false
redundancy — training data biases and architecture preferences do not change
with prompt switching.

```
Valid:   Anthropic + DeepSeek + Google   ✓
Invalid: Anthropic + Anthropic + Google  ✗ (same vendor)
Invalid: Claude Opus + Claude Sonnet     ✗ (same vendor, different model)
```

### 5.3 Three-Tier Failover

When Gauge (§9) detects a vendor outage:

| Failure | Failover | XVal Mode |
|---------|----------|-----------|
| Primary down | Audit promoted to Primary, Tertiary promoted to Audit | 2-model + L0 self-critique |
| Primary + Audit down | Tertiary promoted to Primary | L0 self-critique only |
| All three down | **Warden (§12) triggers global pause** | Human intervention |

### 5.4 Adjudication Matrix

| Primary | Audit | Tertiary | Verdict | Action |
|:-------:|:-----:|:--------:|:-------:|--------|
| ✓ | ✓ | ✓ | **Consensus** | L1: auto-accept |
| ✓ | ✓ | ✗ | **Majority (2:1)** | L2: flagged + execute |
| ✓ | ✗ | ✓ | **Majority (2:1)** | L2: flagged + execute |
| ✗ | ✓ | ✓ | **Majority (2:1)** | L2: flagged + execute |
| ✓ | ✗ | ✗ | **Minority (1:2)** | L3: escalate to human |
| ✗ | ✗ | ✗ | **Stalemate (0:3)** | L3: escalate to human |

### 5.5 L0 Degradation

When only one model is available (vendor outage cascade), single-model
"devil's advocate" self-critique is acceptable with increased spot-check
sampling rate. Not equivalent to full tri-model validation.

### 5.6 Integration

| Subsystem | XVal Interaction |
|-----------|-----------------|
| **Regulator (§2)** | Tri-model triples token cost. Regulator accounts for this in budget. |
| **Sanctum (§3)** | XVal disagreement rate is a behavioral trust signal. |
| **Chronicle (§4)** | Every verdict produces an audit receipt with all three model outputs. |
| **Gauge (§9)** | Monitors vendor health; triggers failover when degradation detected. |
| **Warden (§12)** | Handles total vendor outage escalation. |

**Implementation:** [deeparchi-ai/macs-xval-go](https://github.com/deeparchi-ai/macs-xval-go) — 31 tests (tri-model v0.2)

---

## §6 Cadence — Batch Processing

> IBM lineage: **JES2** (Job Entry Subsystem) + **SDSF** (output management)

### The Batch Path

Not all agent work is triggered by a human message. Cron jobs, periodic data
collection, scheduled report generation — these run on a timer, not on demand.
They bypass the MAEA middleware and land directly on MACS.

### Capabilities

| Capability | IBM Equivalent | Description |
|-----------|:-------------:|-------------|
| Input queue | JES2 INPUT | Job submission with priority class |
| Initiator management | JES2 INIT | Assign execution slots by priority |
| Output queue | SDSF SPOOL | Batch result delivery + status query |
| Job chaining | JCL COND | Job A's output triggers Job B |
| Priority preemption | Regulator integration | High-priority batch suspends low-priority |

**Implementation:** [macs/integrations/jes-gate](https://github.com/deeparchi-ai/macs/tree/main/integrations/jes-gate) — POC, 4 gate scenarios

---

## §7 Curator — Knowledge Lifecycle

> IBM lineage: **DFSMS** (Storage Management) + **DFSMSdss** (backup/restore)

### Tiered Context Model

```
Tier 0: Hot   — Full fidelity, ~50K tokens
Tier 1: Warm  — Summarized, key decisions preserved, ~10K tokens
Tier 2: Cold  — Bullet-point summary, ~1K tokens
Tier 3: Archive — Searchable index, unlimited (external storage)
```

### Capabilities

| Capability | Description |
|-----------|-------------|
| Confidence-based expiration | Documents with `confidence:low` and `last_verified > 180d` → archive |
| Memory compression | When near limit, compress stale entries into Vault documents |
| Backup/Restore | Full MACS state (registry, audit records, policies) export/import |
| PII-aware compression | Integrate with Sanctum to sanitize before compression; re-check on recall |

**Implementation:** [deeparchi-ai/macs-dfsms-go](https://github.com/deeparchi-ai/macs-dfsms-go) — 13 tests

---

## §8 Nexus — Protocol Routing

> IBM lineage: **VTAM** (Virtual Telecommunications Access Method)

### Logical Unit Names

Every MACS agent has a stable LU name independent of transport. Nexus
resolves LU names to available transports and selects the best one:

```
research-agent.prod → gRPC (priority 0) → HTTP (priority 1) → WebSocket (priority 2)
```

### Capabilities

| Capability | Description |
|-----------|-------------|
| Protocol admission | Which agents can expose which protocols |
| Transport negotiation | Auto-select best available transport (gRPC > HTTP > WebSocket) |
| Health tracking | Mark unhealthy endpoints; automatic failover |
| Rate limiting | Per-agent-pair connection limits |
| Circuit observability | Connection-level event log |

**Implementation:** [deeparchi-ai/macs-vtam-go](https://github.com/deeparchi-ai/macs-vtam-go) — 16 tests

---

## §9 Gauge — Performance Metrics

> IBM lineage: **RMF** (Resource Measurement Facility) + **NetView** (network monitoring)

### What Gauge Measures

| Metric | Source | Alert Threshold |
|--------|--------|:---:|
| Agent latency (p50/p95/p99) | Agent executor hooks | p95 > 3× baseline |
| Token consumption rate | Regulator burn rate feed | Trend > 1.5× projected |
| Model vendor health | API response codes + latency | > 10% errors in 5min window |
| Cross-vendor correlation | All three XVal models | Correlation score: are they all degrading together? |
| Agent success rate | Task completion tracking | < 80% over 1h window |
| Link quality (A2A/MCP) | Nexus circuit events | Packet loss > 1% or latency > 5s |

### Cross-Vendor Correlation Detection

Critical for the "两地三中心" model: if Anthropic + DeepSeek + Google all
degrade simultaneously, the cause is likely external (network, cloud
provider), not vendor-specific. Gauge detects correlated degradation
and escalates to Warden.

**Implementation:** v0.1 Go package — 20 tests. Repository: [deeparchi-ai/macs-gauge-go](https://github.com/deeparchi-ai/macs-gauge-go)

---

## §10 Seal — Identity & Cryptography

> IBM lineage: **ICSF** (Integrated Cryptographic Service Facility)

### Identity Lifecycle

| Phase | Mechanism |
|-------|-----------|
| **Registration** | Agent submits A2A Agent Card; Seal verifies four-name alignment |
| **Trust root binding** | Per-agent trust root pinned; rotation requires human re-auth |
| **Certificate rotation** | Automatic rotation with overlap window (no downtime) |
| **Revocation** | Immediate: all active sessions terminated; Chronicle records reason |
| **Output signature** | Agents sign critical outputs (decision receipts, file writes) |

### Separation from Sanctum

- **Seal** answers: "Who are you?" (identity, certificates, signatures)
- **Sanctum** answers: "What are you allowed to do?" (access, trust, constraints)

**Implementation:** v0.1 Go package — 19 tests. Repository: [deeparchi-ai/macs-seal-go](https://github.com/deeparchi-ai/macs-seal-go)

---

## §11 Relay — Cluster State

> IBM lineage: **XCF** (Cross-system Coupling Facility)

### Shared State & Broadcast

MACS agents run in separate processes. Relay provides the shared channel
they need for coordination:

| Capability | Description |
|-----------|-------------|
| **Cluster membership** | Who is online? Heartbeat-based member list |
| **Shared state** | Key-value store with TTL. Agent A writes; Agent B reads |
| **Broadcast events** | Publish/subscribe. "Model switch completed" → all agents notified |
| **Group communication** | Agent groups with atomic multicast |
| **State convergence** | Eventually consistent; conflict resolution by timestamp |

### Example: Agent Crash Recovery

```
Agent B crashes → Warden detects → Warden broadcasts "B restarting"
via Relay → Agent A pauses delegation to B → Warden restarts B →
Relay broadcasts "B restored" → Agent A resumes delegation
```

Without Relay: Agent A keeps delegating to a dead agent until timeout.

**Implementation:** v0.1 Go package — 15 tests. Repository: [deeparchi-ai/macs-relay-go](https://github.com/deeparchi-ai/macs-relay-go)

---

## §12 Warden — Recovery & Operations

> IBM lineage: **ARM** (Automatic Restart Manager) + **System Automation**

### Crash Recovery

| Condition | Action |
|-----------|--------|
| Agent crash detected | DUMP snapshot → restart agent → restore from Curator hot tier → replay from Loom fork point |
| 3 crashes in 5 min | Suspend agent → notify human → human decides: repair or retire |
| Kernel unresponsive > 5s | Pulse triggers → watchdog restarts kernel |
| Model vendor outage cascade | All three down → Warden broadcasts "global pause" → notify human |

### Policy Engine

Declarative policies for automated operations:

```yaml
policies:
  - name: agent-crash-loop
    condition: agent.failures(5m) >= 3
    action: [suspend_agent, notify_human, escalate_after(30m)]
  
  - name: vendor-total-outage
    condition: xval.active_models == 0
    action: [global_pause, notify_human, await_manual_restore]
  
  - name: token-budget-black
    condition: regulator.level == BLACK
    action: [allow_l1_only, notify_human]
```

### Escalation Levels

| Level | Trigger | Action |
|:-----:|---------|--------|
| L0 | Informational | Log to Chronicle |
| L1 | Warning | Notify agent owner (Feishu DM) |
| L2 | Action required | Notify + auto-mitigate (restart, degrade) |
| L3 | Critical | Notify + auto-mitigate + escalate to human after timeout |

**Implementation:** v0.1 Go package — 12 tests. Repository: [deeparchi-ai/macs-warden-go](https://github.com/deeparchi-ai/macs-warden-go)

---

## §13 Pulse — Self-Health

> IBM lineage: **z/OS Health Checker**

### What Pulse Checks

| Check | Frequency | Failure Action |
|-------|:--------:|----------------|
| **Subsystem heartbeat** | Every 10s | Log to Chronicle; if 3 consecutive misses → alert Warden |
| **Kernel liveness** | Every 1s | Watchdog restart |
| **Startup consistency** | On boot | Verify all subsystems at expected versions; refuse to start on mismatch |
| **Dependency health** | Every 30s | Recursive: if Regulator depends on Sanctum, and Sanctum is down, Pulse reports Regulator as degraded |

### Health Status

| Status | Meaning |
|:------:|---------|
| **Healthy** | All checks passing |
| **Degraded** | One or more non-critical subsystems down; agents continue |
| **Impaired** | Critical subsystem down; agents degraded |
| **Down** | Kernel unresponsive |

**Implementation:** v0.1 Go package — 10 tests. Repository: [deeparchi-ai/macs-pulse-go](https://github.com/deeparchi-ai/macs-pulse-go)

---

## §14 Console — Operator Console

> IBM lineage: **TSO** (Time Sharing Option) + **ISPF** (Interactive System Productivity Facility)

### Role

Console is the operator-facing control plane for MACS. It provides a unified
interface to all 13 kernel subsystems — status queries, agent lifecycle commands,
policy editing, job output browsing — across three modes.

### Three-Mode Architecture

| Mode | z/OS Equivalent | Interface | Use Case |
|------|:-------------:|-----------|----------|
| **Interactive** | ISPF panels | Feishu interactive cards + Web dashboard | Human operator at Feishu / browser |
| **Headless** | TSO CLIST / REXX | CLI (stdin/stdout REPL) | Scripting, cron, CI/CD pipeline |
| **Embedded** | TSO Batch (IKJEFT01) | MCP server tool set | AI agent integration via MCP |

### Command Menu

```
─── MACS Console ─────────────────────────
 0  Status      — 全系统状态一览 (Pulse)
 1  Agents      — Agent 列表 / 启停 / 重启 (Warden)
 2  Jobs        — 作业队列 / 输出查看 (Cadence)
 3  Audit       — 审计记录查询 (Chronicle)
 4  Metrics     — 实时指标面板 (Gauge)
 5  Identity    — Agent 身份管理 / 证书轮换 (Seal)
 6  Policies    — 策略查看 / 编辑 / 激活 (Warden)
 7  Log         — 系统日志浏览
 X  Exit
──────────────────────────────────────────
```

### Subsystem Read/Write Matrix

| Subsystem | Console Reads | Console Writes |
|-----------|:---:|:---:|
| §13 Pulse | Health status, dependency graph | — |
| §12 Warden | Policy list, agent status, escalation state | Start/stop/restart agent; edit/activate policies; manual escalate |
| §6 Cadence | Job queue, job output | Submit job; cancel job; re-prioritize |
| §4 Chronicle | Audit records (query by agent/time/trace) | — |
| §9 Gauge | Metric summaries, alerts, correlation reports | — |
| §10 Seal | Identity list, certificate status | Register agent; begin/complete rotation; revoke |
| §2 Regulator | Token budget, importance class | — |
| §3 Sanctum | Trust scores, access violations | — |
| §7 Curator | Context tier status, storage usage | Trigger compression; force backup |

### Headless CLI Contract

Every Console command must surface in three forms with identical semantics:

```
1. Interactive:  SELECTION → sub-panel → action
2. Headless CLI: macs-console <noun> <verb> [--flags]
3. Embedded MCP: tool name = "macs_<noun>_<verb>"
```

**Headless examples:**

```bash
macs-console status                    # system health overview
macs-console agent list                # all registered agents
macs-console agent start <lu-name>     # start agent with Loom fork-point
macs-console agent stop <lu-name>      # graceful stop
macs-console agent restart <lu-name>   # crash recovery path
macs-console job list [--status=<s>]   # cadence job queue
macs-console job output <job-id>       # job result
macs-console audit query [--agent=<a>] [--since=<t>] [--trace=<id>]
macs-console metric show [--subsystem=<s>] [--window=<d>]
macs-console identity list [--status=<s>]
macs-console identity register --lu=<name> --card=<url> --key=<hash>
macs-console identity rotate --lu=<name> --new-key=<hash>
macs-console identity revoke --lu=<name> --reason=<text>
macs-console policy list
macs-console policy edit --name=<n> --action=<a>
macs-console policy activate --name=<n>
```

### MCP Tool Contract (Embedded Mode)

```json
{
  "server": "macs-console",
  "tools": [
    {"name": "macs_status",           "description": "全系统 14 子系统健康状态"},
    {"name": "macs_agent_list",       "description": "列出所有注册 Agent 及状态"},
    {"name": "macs_agent_control",    "description": "Agent 启停/重启"},
    {"name": "macs_job_list",         "description": "查询 Cadence 作业队列"},
    {"name": "macs_job_output",       "description": "获取指定作业输出"},
    {"name": "macs_audit_query",      "description": "按条件查询审计记录"},
    {"name": "macs_metric_show",      "description": "查询 Gauge 指标"},
    {"name": "macs_identity_list",    "description": "列出 Seal 管理的 Agent 身份"},
    {"name": "macs_identity_manage",  "description": "注册/轮换/撤销 Agent 身份"},
    {"name": "macs_policy_list",      "description": "列出 Warden 策略"},
    {"name": "macs_policy_manage",    "description": "编辑/激活 Warden 策略"}
  ]
}
```

### Implementation

**Repository:** [deeparchi-ai/macs-console-go](https://github.com/deeparchi-ai/macs-console-go)

**v0.1 scope:**

| Component | Lines (est.) | Description |
|-----------|:--:|------|
| `pkg/console/cli.go` | ~150 | CLI router + REPL loop (headless mode) |
| `pkg/console/commands.go` | ~300 | All command handlers with subsystem integration |
| `pkg/console/mcp.go` | ~120 | MCP server tool definitions |
| `pkg/console/status.go` | ~80 | Unified status query across Pulse + Gauge + Regulator |
| `pkg/console/agentctl.go` | ~100 | Agent lifecycle: list / start / stop / restart |
| `pkg/console/job.go` | ~80 | Cadence job queue + output |
| `pkg/console/audit.go` | ~80 | Chronicle audit record queries |
| `pkg/console/identity.go` | ~80 | Seal identity management commands |
| `pkg/console/policy.go` | ~80 | Warden policy list / edit / activate |
| Tests | ~320 | 20+ tests covering all 8 command groups |



## Appendix A: z/OS Subsystem Mapping

| MACS | z/OS | Inherited from IBM | Unique to Agent OS |
|------|------|:---:|:---:|
| §2 Regulator | WLM | Goal arbitration, importance classes | Token budget + model failover |
| §3 Sanctum | RACF | L1/L2/L3 levels, cross-level rules | Behavioral trust scoring, drift detection |
| §3b Loom | CICS Syncpoint | Two-phase commit, UOW | Causal-DAG contamination detection, fork-point replay |
| §4 Chronicle | SMF | Immutable records, unified audit surface | W3C traceparent, cross-protocol bridge |
| §5 XVal | *(none)* | — | **Tri-model** verification, vendor outage failover |
| §6 Cadence | JES2 + SDSF | Priority queues, initiator management | Result delivery to Feishu, job output query |
| §7 Curator | DFSMS + dss | Lifecycle policies, tiered storage, backup/restore | Knowledge artifact semantics (confidence, superseded_by) |
| §8 Nexus | VTAM | Protocol admission, multi-transport routing | A2A/MCP/Feishu coexistence |
| §9 Gauge | RMF + NetView | Performance metrics, network monitoring | Cross-vendor health correlation, model degradation detection |
| §10 Seal | ICSF | Certificate management, cryptographic operations | Agent-specific identity lifecycle, output signature verification |
| §11 Relay | XCF | Cluster membership, shared state, broadcast | Inter-agent event pub/sub, state convergence |
| §12 Warden | ARM + System Automation | Crash recovery, policy-driven operations | Model outage escalation, human-in-the-loop policies |
| §13 Pulse | Health Checker | Subsystem health checks, startup verification | Dependency-aware health propagation, watchdog integration |
| §14 Console | TSO + ISPF | Interactive command environment, full-screen panels | Three-mode (Interactive/Headless/Embedded), Feishu + CLI + MCP, unified control plane |

---

## Appendix B: Implementation Status

| § | Subsystem | Repository | Status | Tests |
|:--:|-----------|-----------|:------:|:-----:|
| §2 | Regulator | [deeparchi-ai/macs-regulator-go](https://github.com/deeparchi-ai/macs-regulator-go) | ✅ CPU · 🚧 Token | 34 |
| §3 | Sanctum | [deeparchi-ai/macs-sanctum-go](https://github.com/deeparchi-ai/macs-sanctum-go) | ✅ v0.1 · 🚧 trust | 13 |
| §3b | Loom | [deeparchi-ai/macs-loom-go](https://github.com/deeparchi-ai/macs-loom-go) | ✅ v0.1 | 12 |
| §4 | Chronicle | [a2a-go PR #377](https://github.com/a2aproject/a2a-go/pull/377) + [mcp-audit-go](https://github.com/deeparchi-ai/mcp-audit-go) + [chronicle-bridge-go](https://github.com/deeparchi-ai/macs-chronicle-bridge-go) + DUMP | ✅ | 68 |
| §5 | XVal | [deeparchi-ai/macs-xval-go](https://github.com/deeparchi-ai/macs-xval-go) | ✅ tri-model v0.2 | 31 |
| §6 | Cadence | [macs/integrations/jes-gate](https://github.com/deeparchi-ai/macs/tree/main/integrations/jes-gate) | ✅ POC | 4 |
| §7 | Curator | [deeparchi-ai/macs-curator-go](https://github.com/deeparchi-ai/macs-curator-go) | ✅ v0.1 | 13 |
| §8 | Nexus | [deeparchi-ai/macs-nexus-go](https://github.com/deeparchi-ai/macs-nexus-go) | ✅ v0.1 | 16 |
| §9 | Gauge | [deeparchi-ai/macs-gauge-go](https://github.com/deeparchi-ai/macs-gauge-go) | ✅ v0.1 | 20 |
| §10 | Seal | [deeparchi-ai/macs-seal-go](https://github.com/deeparchi-ai/macs-seal-go) | ✅ v0.1 | 19 |
| §11 | Relay | [deeparchi-ai/macs-relay-go](https://github.com/deeparchi-ai/macs-relay-go) | ✅ v0.1 | 15 |
| §12 | Warden | [deeparchi-ai/macs-warden-go](https://github.com/deeparchi-ai/macs-warden-go) | ✅ v0.1 | 12 |
| §13 | Pulse | [deeparchi-ai/macs-pulse-go](https://github.com/deeparchi-ai/macs-pulse-go) | ✅ v0.1 | 10 |
| §14 | Console | *(design spec)* | 📋 | — |

---

## Appendix C: Glossary

| Term | Definition |
|------|-----------|
| **A2A** | Agent-to-Agent protocol. Standard for inter-agent communication. |
| **Cadence** | MACS §6: batch scheduling + job output management (JES2 + SDSF). |
| **Chronicle** | MACS §4: immutable audit trail + W3C trace + cross-protocol bridge (SMF). |
| **Curator** | MACS §7: tiered knowledge lifecycle + memory compression + backup/restore (DFSMS + dss). |
| **DUMP** | MACS recoverability artifact: a frozen snapshot of an agent's decision chain. |
| **Gauge** | MACS §9: performance metrics + cross-vendor health correlation (RMF + NetView). |
| **Gene** | Hard security constraint in Sanctum Layer 4. Cannot be bypassed by any code path. |
| **Kernel** | MACS core. Only path from subsystems to agents. Thin in-process layer. |
| **L1 / L2 / L3** | Security levels: L1=highest (architecture/strategy), L2=high (core data/code), L3=standard (public info). |
| **Loom** | MACS §3b: causal-DAG rollback + two-phase commit + fork-point snapshots (CICS Syncpoint). |
| **LU Name** | Logical Unit name. Stable agent identifier independent of transport (VTAM). |
| **MCP** | Model Context Protocol. Standard for agent-to-tool communication. |
| **Nexus** | MACS §8: protocol admission + multi-transport routing + LU name resolution (VTAM). |
| **Pulse** | MACS §13: MACS self-health checks (Health Checker). |
| **Regulator** | MACS §2: goal-oriented scheduler + token budget + model failover (WLM). |
| **Relay** | MACS §11: cluster membership + shared state + inter-agent broadcast (XCF). |
| **Sanctum** | MACS §3: access control + behavioral trust scoring + hard constraints (RACF). |
| **Seal** | MACS §10: agent identity registry + certificate rotation + output signatures (ICSF). |
| **Span** | Single step in a multi-hop agent delegation chain (W3C Trace Context). |
| **Traceparent** | W3C standard header: `version-trace_id-span_id-flags`. |
| **Warden** | MACS §12: crash recovery + policy-driven operations + human escalation (ARM + SA). |
| **XVal** | MACS §5: **tri-model** cross-validation with 2/3 majority adjudication. |
| **Console** | MACS §14: operator control plane. Three-mode (Interactive/Headless/Embedded). TSO + ISPF lineage. |
| **TSO** | Time Sharing Option. z/OS interactive command environment. Console Headless mode inherits its REPL paradigm. |
| **ISPF** | Interactive System Productivity Facility. z/OS full-screen panel manager. Console Interactive mode inherits its menu navigation. |
| **Headless** | Console mode: CLI via stdin/stdout REPL. Scriptable, cron-compatible. TSO CLIST equivalent. |
| **Embedded** | Console mode: MCP server tool set. AI agent calls Console as a tool. TSO Batch (IKJEFT01) equivalent. |

---

> *MAEA Framework · DeepArchi Team*
> *2026-07-18 · [deeparchi.ai](https://deeparchi.ai)*
