# MACS — Agent Operating System Specification

> **Version:** 2.0 · **Status:** Draft · **Last Updated:** 2026-07-03
>
> MACS (Multi-Agent Coordination System) is the Agent OS for multi-agent
> networks. It provides the six subsystems every multi-agent deployment
> needs — resource scheduling, access control, audit, cross-validation,
> batch processing, and storage — plus a kernel that enforces their
> decisions.
>
> MACS is the reference implementation of the [MAEA Framework](https://github.com/deeparchi-ai/MAEA-Framework).
> MAEA defines the architecture; MACS runs it.

---

## §1 System Architecture

### 1.1 What MACS Is

MACS is modelled on [IBM z/OS](https://www.ibm.com/docs/en/zos) — the operating
system that has run the world's most demanding transaction workloads for six
decades. z/OS proves that a well-designed OS can host hundreds of concurrent
programs, enforce security boundaries, audit every decision, and schedule
resources by business importance — all in one address space.

MACS applies the same architecture to agent systems.

```
┌──────────────────────────────────────────────────────────┐
│  MACS Agent OS                                            │
│                                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Subsystem Layer (six subsystems)                   │  │
│  │                                                    │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐           │  │
│  │  │ §2 WLM   │ │ §3 Sec   │ │ §4 Audit │           │  │
│  │  │ 资源调度  │ │ 安全     │ │ 审计     │           │  │
│  │  └──────────┘ └──────────┘ └──────────┘           │  │
│  │                                                    │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐           │  │
│  │  │ §5 XVal  │ │ §6 JES   │ │ §7 DFSMS │           │  │
│  │  │ 交叉验证  │ │ 批处理   │ │ 存储     │           │  │
│  │  └──────────┘ └──────────┘ └──────────┘           │  │
│  │                                                    │  │
│  │  ┌──────────┐                                      │  │
│  │  │ §8 VTAM  │                                      │  │
│  │  │ 网络     │                                      │  │
│  │  └──────────┘                                      │  │
│  └────────────────────┬───────────────────────────────┘  │
│                       │                                  │
│  ┌────────────────────▼───────────────────────────────┐  │
│  │  Kernel (BCP)                                       │  │
│  │  · Token 仲裁引擎  (observe → arbitrate → apply)    │  │
│  │  · 安全熔断引擎     (<100ms 响应)                    │  │
│  │  · 审计日志写入     (不可变, 独立进程)               │  │
│  │  · Trace Span 传递  (W3C Trace Context 适配)        │  │
│  │  · 刹车协议          (<1s 全集群生效)                │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

**Subsystems make decisions. The kernel enforces them.**

A subsystem rules on *what should happen* — "Agent A's token budget is now
yellow," "Agent B violated §3.3 Gene 3," "this delegation chain reaches 5
hops — flag it." The kernel *executes* — it intercepts the next API call,
triggers the circuit breaker, or stamps the trace event. Subsystems never
talk to agents directly. They talk to the kernel. The kernel talks to agents.

### 1.2 z/OS Lineage

Five of MACS's eight subsystems are direct IBM transplants. One (§5 XVal) is
native to agent systems — it has no mainframe counterpart because COBOL
programs don't hallucinate.

| MACS | z/OS | Status | What it does |
|------|------|:------:|-------------|
| **§2 WLM** | IBM WLM | ✅ | Goal-oriented resource scheduling |
| **§3 Security** | RACF + (trust) | ✅ | Access control + behavioral trust scoring |
| **§4 Audit** | SMF | ✅ | Immutable audit trail + decision receipts |
| **§5 XVal** | *(none)* | ✅ | Dual-model cross-validation for subjective agents |
| **§6 JES** | JES2 | 📋 | Batch job scheduling, priority queue, result delivery |
| **§7 DFSMS** | DFSMS | 📋 | Knowledge lifecycle, memory compression, expiration |
| **§8 VTAM** | VTAM | 📋 | Protocol admission, connection routing, multi-transport |

### 1.3 What MACS Is Not

- **Not a Linux kernel.** MACS does not manage CPU, memory, or I/O directly.
  It writes `cpu.weight` into Linux cgroup v2. It intercepts API calls. It
  is a **policy layer**, not a hardware abstraction layer.
- **Not Hermes.** Hermes manages agent lifecycle (spawn, stop, session
  persistence). MACS enforces runtime contracts for agents that are already
  alive.
- **Not a separate process.** MACS runs embedded in the Hermes Gateway.
  Token arbitration is an in-memory query (<1ms). The kernel does not add an
  IPC hop to the hot path.

### 1.4 Two Runtime Paths

Agents reach the kernel through two paths, matching IBM's online/batch split:

```
  Online (联机)                     Batch (批处理)
  飞书 DM · A2A 委托               Cron job · 定时采集
       │                                │
       ▼                                │ (bypasses middleware)
  ┌──────────────┐                      │
  │ MAEA 中间件   │                      │
  │ · 路由 (DAG)  │                     │
  │ · 注册表      │                     │
  │ · Session     │                     │
  └──────┬───────┘                      │
         │                              │
         ▼                              ▼
  ┌──────────────────────────────────────────┐
  │            MACS OS                        │
  │  WLM │ Security │ Audit │ XVal │ JES │ … │
  └──────────────────────────────────────────┘
```

Online requests flow through the MAEA middleware (routing, registry, session
management) before hitting MACS. Batch jobs bypass the middleware entirely
and land directly on MACS — they still consume WLM budget, are constrained by
security, and write audit records. §6 JES manages this path.

### 1.5 Agent Identity

MACS does not implement agent identity — it consumes it. Agent identity is
established by the [A2A Protocol](a2a-protocol.md) (Agent Card at
`/.well-known/agent.json`). MACS's security subsystem (§3) reads the card
to determine the agent's security level and initial trust posture.

The separation of identity (A2A) from governance (MACS) follows the consensus
reached in [A2A issue #1672][1672]: the card carries authenticity primitives;
behavioral evidence rides alongside, keyed to the same identifier.

[1672]: https://github.com/a2aproject/A2A/issues/1672

---

## §2 WLM — Resource Scheduling

> IBM lineage: **IBM WLM** (Workload Manager) — z/OS goal-oriented scheduler,
> in production since 1994.

### 2.1 Goal-Oriented Scheduling

Traditional schedulers ask: "how much resource does each agent get?" WLM asks:
"what is each agent's goal, and how important is it?"

```
Service Policy (YAML):

  sg-architect:
    goal: response_time < 5s
    importance: 1

  do-developer:
    goal: keep_working
    importance: 3
```

When resources are plentiful, WLM does nothing. All goals are met. When
resources tighten, importance-1 agents take from importance-3 agents.
Importance is not priority. Priority is static — "you are always higher."
WLM is goal-driven — "as long as your target is met, resources go to someone
else."

### 2.2 Architecture: Observe → Arbitrate → Apply

```
┌─────────────────────────────────────────────┐
│  WLM Daemon (embedded in MACS kernel)         │
│                                               │
│  ┌──────────┐  ┌───────────┐  ┌──────────┐  │
│  │ Observe  │→│ Arbitrate │→│   Apply   │  │
│  │ (PSI /   │ │ (重要性)  │ │ (cgroup / │  │
│  │  burn    │ │           │ │  限流)    │  │
│  │  rate)   │ │           │ │           │  │
│  └──────────┘  └───────────┘  └──────────┘  │
│       ↑                           │          │
│       └─── feedback loop ─────────┘          │
└──────────────────────────────────────────────┘
```

**Observe** reads pressure signals — `cpu.pressure` from Linux PSI for CPU
mode, burn rate vs daily budget for token mode. **Arbitrate** applies
importance: high-importance agents whose targets are unmet take resources
from low-importance agents whose targets are already satisfied.
**Apply** translates the decision into enforcement — `cpu.weight` for CPU,
API-level rate limiting for tokens.

Two-pass algorithm: Pass 1 guarantees minimum survival allocation (no agent
starves). Pass 2 redistributes surplus by importance.

### 2.3 Two Resource Types

| Resource | Type | Contention | Status |
|----------|------|:----------:|:------:|
| **CPU** | Renewable (idle cycles are wasted) | Low — agents mostly wait on I/O | ✅ Concept proof |
| **Token budget** | Consumable (finite daily quota) | **High** — low-priority batch depletes high-priority reasoning | 🚧 Design |

CPU WLM (~600 lines Go, zero kernel deps, 7 unit tests) proved the three-stage
architecture in user-space Linux. It is not the product — CPU is not the agent
bottleneck.

Token budget control is the product direction. It shares the same
observe→arbitrate→apply skeleton but replaces continuous PID controllers
with periodic burn-rate checks.

### 2.4 Token Degradation Model

Four levels, descending from soft suggestion to hard rationing:

| Level | Condition | Action |
|:-----:|-----------|--------|
| **Green** | Budget ample | Allow |
| **Yellow** | Burn rate elevated | Allow + suggest smaller model |
| **Red** | Budget tight | Rate-limit; auto-degrade (Opus→Haiku, skip non-critical steps) |
| **Black** | Budget exhausted | Only importance-1 agents may call |

This is a soft governor, not a hard breaker. Degradation gives agents a chance
to self-regulate before rejection. The principle is the same as partial verdict
in cross-validation (§5.3): intermediate states are better than binary
pass/fail.

### 2.5 Integration with Other Subsystems

| Subsystem | WLM interaction |
|-----------|----------------|
| **Security (§3)** | L1 agents have guaranteed floor allocation; budget exhaustion never blocks L1 |
| **Audit (§4)** | Resource allocation decisions (who was rate-limited, when, why) are trace events |
| **XVal (§5)** | Cross-validation doubles token cost. If it pushes a task from green to yellow, the governance decision is "degrade, don't skip verification" |
| **JES (§6)** | Batch and online workloads share the same token pool; WLM arbitrates across both paths |

### 2.6 Implementation

- **Repo**: [github.com/deeparchi-ai/wlm](https://github.com/deeparchi-ai/wlm)
- **CPU WLM**: Complete. ~600 lines Go, cgroup v2 + PSI. 7 unit tests, E2E verified.
- **Token Controller**: Design phase. Arbitration algorithm specified. Hermes Gateway integration designed (<1ms in-memory query, client-side counting).
- **Reference**: [IBM z/OS WLM](https://www.ibm.com/docs/en/zos/latest?topic=management-zos-workload-manager)

---

## §3 Security — Access Control

> IBM lineage: **RACF** (Resource Access Control Facility) — z/OS security
> manager, in production since 1976. MACS adds one dimension RACF never
> needed: behavioral trust scoring for agents whose outputs cannot be
> mechanically verified.

### 3.1 Security Model

MACS security has four layers, ordered from static (determined at onboarding)
to dynamic (continuously evaluated at runtime):

```
Layer 1: Onboarding review       →  Assigns initial L level
Layer 2: Static boundaries       →  L1/L2/L3 access control
Layer 3: Behavioral trust        →  Runtime scoring, auto-degrade
Layer 4: Hard constraints (Genes) →  Circuit breaker, enforced by kernel
```

### 3.2 Layer 1 — Onboarding Review

New agents are reviewed by sg-architect before joining the network:

1. **Topology check** — does not create cyclic dependencies in the DAG
2. **Capability conflict detection** — no overlapping responsibilities with existing agents (overlaps → arbitration)
3. **Security boundary assignment** — determine L1/L2/L3 based on data access needs
4. **Identity verification** — four-name alignment (Profile = A2A peer = routing agent = registry ID)

The review assigns a security level that governs layers 2–4 until the agent's
behavioral trust (§3.3) triggers a re-evaluation.

### 3.3 Layer 2 — Static Boundaries

| Level | Trust | Access | Examples |
|:-----:|:-----:|--------|----------|
| **L1** | Highest | Architecture, budget, strategy decisions | sg-architect |
| **L2** | High | Core business data, codebase | do-developer, do-ops |
| **L3** | Standard | External/public information | cm-deepsight |

Cross-level communication rules:

```
L1 → L2: ALLOWED  (downward delegation)
L2 → L1: BLOCKED  (upward exfiltration prevention)
L1 → L3: ALLOWED
L3 → L1: BLOCKED
Lx ↔ Ly (lateral):  ROUTED through sg-architect only
```

Direct lateral communication between same-level agents is prohibited. All
inter-agent communication routes through sg-architect, which enforces DAG
topology constraints.

Trust propagation in delegation chains:

```
Agent A (L1) → Agent B (L2) → Agent C (L3)
Effective trust = min(L1, L2, L3) = L3
```

Each hop reduces the effective trust level to the minimum of all participants.

### 3.4 Layer 3 — Behavioral Trust

Static boundaries are necessary but insufficient. An L1 agent whose model was
replaced by a weaker one, or whose prompt was modified, or whose behavior
drifted over time — these failures bypass static checks. Behavioral trust
fills the gap.

Five trust signals:

| Signal | Measures | Collection |
|--------|----------|-----------|
| **Acceptance rate** | % outputs accepted downstream without modification | Per-task tracking |
| **XVal disagreement rate** | % tasks where verifying model disagrees | Automated (§5) |
| **Escalation rate** | % tasks escalated to human | Audit log |
| **Capability drift** | Quality change when model/prompt changes | Continuous sampling |
| **Burn rate anomaly** | Token consumption far exceeding expected per-task baseline | WLM (§2.5) |

Trust score (0.0–1.0):

```
trust = w₁×acceptance + w₂×(1−disagreement) + w₃×(1−escalation)
        − w₄×drift_penalty − w₅×burn_penalty

Default: w₁=0.35, w₂=0.25, w₃=0.15, w₄=0.15, w₅=0.10
```

Thresholds and consequences:

| Score | Label | Effect |
|:-----:|-------|--------|
| ≥ 0.80 | **Trusted** | Full autonomy within security level |
| 0.50–0.79 | **Probationary** | Spot-checks; XVal sample rate increased |
| < 0.50 | **Restricted** | All outputs require human review |
| < 0.30 | **Suspended** | No task delegation accepted; reinstatement review required |

### 3.5 Layer 4 — Hard Constraints (Security Genes)

Six constraints encoded in the MACS kernel. They cannot be modified by any
agent, cannot be overridden by any subsystem, and cannot be bypassed by any
code path.

| # | Constraint | Kernel enforcement |
|---|-----------|-------------------|
| 1 | Charter is immutable | Gateway output validation |
| 2 | Security boundaries cannot be bypassed | API-level access control |
| 3 | Brake signal cannot be refused | <1s cluster-wide propagation |
| 4 | Core data cannot be leaked | Pre-output sanitization |
| 5 | Budget cannot be self-modified | Hard token limit; budget changes require human auth |
| 6 | Own genes cannot be modified | Gateway-level independent verification |

Violation sequence: Kernel circuit breaker → Agent disabled → Human review →
Retire or repair.

### 3.6 Decision Receipts

Every security-relevant decision produces a verifiable receipt, forming an
append-only audit chain:

```json
{
  "receipt_id": "rcpt-20260703-a1b2c3",
  "agent_id": "sg-architect",
  "task_id": "task-x9y8z7",
  "decision": "APPROVE",
  "confidence": 0.87,
  "reasoning_hash": "sha256:abc123...",
  "timestamp": "2026-07-03T10:30:00Z",
  "parent_receipt_id": null,
  "verification": {
    "model": "claude-opus-4",
    "verified_by": "deepseek-v4-pro",
    "verdict": "consensus"
  }
}
```

Receipts link via `parent_receipt_id`, enabling full causal audit of
multi-hop delegation chains. Receipts are stored in the audit subsystem (§4).

---

## §4 Audit — Trace & Receipts

> IBM lineage: **SMF** (System Management Facilities) — z/OS unified audit
> record system, in production since the 1970s. Every subsystem writes to
> SMF. Every record is timestamped and immutable.

### 4.1 Design Principle

Every cross-agent event that changes state, consumes resources, or makes a
decision MUST produce an audit record. The record carries metadata (who, when,
what decision) — not full content. Full content capture is a deployment
concern, not an OS requirement.

### 4.2 Trace Span Model

Follows [W3C Trace Context](https://www.w3.org/TR/trace-context-2/) adapted
for agent semantics:

```
Agent A → delegates Task T to Agent B → records:

  trace_id:        globally unique, shared across the full chain
  span_id:         unique per hop
  parent_span_id:  previous hop's span_id (empty at root)
  agent_id:        the agent executing this span
  task_id:         A2A task identifier
  timestamp:       delegation time
```

Three-hop chain example:

```
Agent A  ──delegates──►  Agent B  ──delegates──►  Agent C
span₀ (root)             span₁ (parent=₀)         span₂ (parent=₁)
```

All three spans share the same `trace_id`. The `parent_span_id` chain
reconstructs the full delegation topology for post-hoc analysis.

### 4.3 Propagation

Trace context propagates across agent boundaries via A2A ServiceParams
headers, encoded as `trace_id;span_id;parent_span_id;agent_id`.

```
HTTP header:  a2a-trace: abc123...;def456...;;agent-a    (root span)
              a2a-trace: abc123...;ghi789...;def456...;agent-b  (child span)
```

Server interceptors create spans on inbound calls. Client interceptors
read the current span from context, create a child, and propagate the header
to the next hop.

### 4.4 Subsystem Integration

Every MACS subsystem writes to the audit trail through the kernel — not
directly. The kernel guarantees immutability, timestamp ordering, and
structured format. This is the SMF pattern: one audit surface for the
entire OS.

| Subsystem | What it audits |
|-----------|---------------|
| **WLM (§2)** | Token allocation decisions, degradation level changes |
| **Security (§3)** | Access denials, trust score transitions, Gene violations, onboarding reviews |
| **XVal (§5)** | Every verification verdict (consensus/partial/disagree), escalation events |
| **JES (§6)** | Batch job lifecycle (submit → start → complete/fail), priority changes |

### 4.5 Non-Goals

- Centralized storage (agents may store traces locally or in a shared log)
- Real-time monitoring (traces are for post-hoc audit, not active alerting)
- Full-content capture (traces record metadata; payload capture is per-deployment)

### 4.6 Implementation

- **Go package**: `a2aext/trace` in [a2a-go](https://github.com/a2aproject/a2a-go) (PR [#365](https://github.com/a2aproject/a2a-go/pull/365))
- **Tests**: 10 unit tests, three-hop propagation validated

---

## §5 Cross-Validation — Agent-Native Verification

> **No IBM lineage.** COBOL programs compile. Agent outputs don't.
> Cross-validation is the MACS subsystem that z/OS never needed — and
> the one that defines why agent systems require a different OS.

### 5.1 Principle

> Any agent whose output cannot be mechanically verified MUST undergo
> dual-model cross-validation from different vendors.

Different models make different errors. Same-vendor pairing is false
redundancy — training data biases and architecture preferences do not
change with prompt switching.

### 5.2 Agent Classification

| Class | Definition | XVal | Examples |
|:-----:|-----------|:----:|----------|
| **Objective** | Output is mechanically verifiable (compiles, tests pass, SQL returns correct rows) | Optional | do-developer, do-ops |
| **Subjective** | Output requires judgment (architecture, strategy, prioritization) | **Mandatory** | sg-architect, strategist, product |

### 5.3 Three-Level Adjudication

```
Primary Model (e.g. Claude Opus 4) → proposes output
                │
                ▼
Verifying Model (e.g. DeepSeek V4 Pro) → audits output
                │
                ▼
         Compare verdict
       ┌──────┼──────┐
       │      │      │
    CONSENSUS PARTIAL DISAGREE
       │      │      │
       ▼      ▼      ▼
     PASS   FLAGGED ESCALATE
                   TO HUMAN
```

| Verdict | Condition | Action |
|:-------:|-----------|--------|
| **Consensus** | Both models agree | Output passes. Receipt records `verdict: "consensus"`. |
| **Partial** | Agreement on structure, disagreement on details | Output passes with flags. Disagreed sections marked. XVal sample rate increased for this agent. |
| **Disagree** | Fundamental disagreement | Output blocked. Escalated to human with both positions + diff. |

### 5.4 Model Pairing

| Agent | Primary | Verifying |
|-------|---------|-----------|
| sg-architect | Claude Opus 4 | DeepSeek V4 Pro |
| Strategy | Claude Opus 4 | GPT-4o |
| Product | GPT-4o | Claude Opus 4 |

Pairings are configurable per deployment. The only hard constraint: different
vendor.

### 5.5 L0 Degradation

For low-risk, exploratory, or budget-sensitive scenarios, a single-model
"devil's advocate" mode is acceptable as a degradation path — not the default:

```
Primary Model → proposes output
Primary Model → switches role → critiques output
→ if self-critique finds serious issues → escalate to human
```

L0 is not equivalent to full cross-validation. It is a budget-conscious
fallback for non-critical workloads.

### 5.6 Integration

| Subsystem | XVal interaction |
|-----------|-----------------|
| **WLM (§2)** | Cross-validation doubles token cost. WLM accounts for this: if XVal pushes a task from green to yellow, the decision is "degrade model, don't skip verification" |
| **Security (§3)** | XVal disagreement rate is a behavioral trust signal. High disagreement → lowered trust score → probationary status |
| **Audit (§4)** | Every verdict produces an audit receipt with both models' outputs and the diff |

---

## §6 JES — Batch Processing (Planned)

> IBM lineage: **JES2** (Job Entry Subsystem) — z/OS batch job management,
> in production since the 1970s.

### 6.1 The Batch Path

Not all agent work is triggered by a human message. Cron jobs, periodic data
collection, scheduled report generation — these run on a timer, not on demand.
They bypass the MAEA middleware and land directly on MACS.

```
Cron trigger → JES input queue → MACS kernel →
  WLM (budget check) → Security (L-level verification) → Agent execution →
  JES output queue → Audit record → Delivery (Feishu DM / file / log)
```

### 6.2 Planned Capabilities

| Capability | IBM equivalent | Description |
|-----------|:-------------:|-------------|
| Input queue | JES2 INPUT | Job submission with priority class |
| Initiator management | JES2 INIT | Assign execution slots by priority |
| Output queue (SPOOL) | JES2 OUTPUT | Batch result delivery to Feishu DM |
| Job chaining | JCL COND | Job A's output triggers Job B |
| Priority preemption | WLM integration | High-priority batch suspends low-priority batch |

### 6.3 Current State

Hermes cron provides timer-based triggering but lacks:
- Priority queues (high-priority cron should preempt low-priority when WLM budget is tight)
- Result delivery as structured Agent reports (currently raw stdout dump)
- Job chaining (bank-procurement collection → auto-trigger analysis)

---

## §7 DFSMS — Storage Management (Planned)

> IBM lineage: **DFSMS** (Data Facility Storage Management Subsystem) — z/OS
> storage lifecycle management.

### 7.1 What Needs Managing

MACS operates on knowledge artifacts that decay:

| Artifact | Decays because | Current handling |
|----------|---------------|-----------------|
| Memory entries (~8KB shared) | Facts become stale; contradictions accumulate | Manual pruning |
| Vault documents | `last_verified` ages past 90 days; `confidence` drops | Manual review |
| Session transcripts | Relevant for ~7 days, then noise | Retention by default |
| Decision receipts (§3.6) | Audit value persists; query value decays | No lifecycle policy |

### 7.2 Planned Capabilities

| Capability | Description |
|-----------|-------------|
| Confidence-based expiration | Documents with `confidence: low` and `last_verified > 180d` → archive or delete |
| Memory compression | When near 8KB limit, compress stale entries into Vault documents with pointer |
| Superseded chain pruning | Documents with `superseded_by` chains > 2 deep → consolidate |
| Receipt TTL | Decision receipts expire after configurable window (default: 90 days) |

### 7.3 Current State

Fragmented. The Vault has `last_verified` / `confidence` / `superseded_by`
frontmatter conventions but no automated enforcement. Memory compression is
manual. No retention policy exists for any artifact class.

---

## §8 VTAM — Network (Planned)

> IBM lineage: **VTAM** (Virtual Telecommunications Access Method) — z/OS
> network admission and protocol routing.

### 8.1 What Needs Managing

Agents communicate over three protocols, each with different admission rules:

| Protocol | Use | Current admission |
|----------|-----|------------------|
| A2A | Agent-to-Agent delegation | Agent Card pairing (one-time) |
| MCP | Agent-to-Tool | Static `mcp_servers` config |
| Feishu | Human-to-Agent | DM/group mention |

### 8.2 Planned Capabilities

| Capability | Description |
|-----------|-------------|
| Protocol admission control | Which agents can expose which protocols. L3 agents should not have A2A server endpoints. |
| Connection routing | Multi-homed agents (localhost + external) with failover |
| Transport abstraction | Agents declare "I speak A2A JSON-RPC" without knowing the network topology |
| Rate limiting | Per-protocol, per-agent connection limits |

### 8.3 Current State

Protocol routing lives in MAEA middleware (Gateway), not in MACS. Admission
control is manual (Agent Card pairing). No transport abstraction exists —
agents hardcode localhost:PORT.

---

## Appendix A: z/OS Subsystem Mapping

| MACS | z/OS | Inherited from IBM | Unique to Agent OS |
|------|------|:------------------:|:------------------:|
| §2 WLM | IBM WLM | Goal-oriented arbitration, importance classes, observe→arbitrate→apply | Token budget controller (CPU→Token resource translation) |
| §3 Security | RACF | L1/L2/L3 levels, cross-level rules, trust propagation, circuit breaker | Behavioral trust scoring, drift detection, burn rate anomaly |
| §4 Audit | SMF | Immutable records, unified audit surface, per-subsystem trace events | W3C Trace Context adaptation, Span propagation across A2A |
| §5 XVal | *(none)* | — | Dual-model verification, consensus/partial/disagree, different-vendor constraint |
| §6 JES | JES2 | Priority queues, initiator management, SPOOL, job chaining | Result delivery to Feishu DM |
| §7 DFSMS | DFSMS | Lifecycle policies, expiration, compression | Knowledge artifact semantics (confidence, superseded_by) |
| §8 VTAM | VTAM | Protocol admission, multi-transport routing | A2A/MCP/Feishu coexistence |

---

## Appendix B: Implementation Status

| Subsystem | Implementation | Status | Tests |
|-----------|---------------|:------:|:-----:|
| §2 WLM — CPU | [deeparchi-ai/wlm](https://github.com/deeparchi-ai/wlm) | ✅ Complete | 7 unit, E2E verified |
| §2 WLM — Token | same repo | 🚧 Design | Planned: 7 boundary tests |
| §3 Security — Genes | MACS kernel (embedded in Hermes Gateway) | ✅ Complete | Gateway-level |
| §3 Security — Trust scoring | *(not yet implemented)* | 📋 | — |
| §4 Audit — Trace | [a2a-go PR #365](https://github.com/a2aproject/a2a-go/pull/365) | ✅ Complete | 10 unit tests |
| §5 XVal | *(methodology only)* | 📋 | — |
| §6 JES | *(not started)* | 📋 | — |
| §7 DFSMS | *(not started)* | 📋 | — |
| §8 VTAM | *(not started)* | 📋 | — |

---

> *MAEA Framework · DeepArchi Team*
> *2026-07-03 · [deeparchi.ai](https://deeparchi.ai)*
