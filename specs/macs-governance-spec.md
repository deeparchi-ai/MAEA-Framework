# MACS Governance Specification v1.0

> Multi-Agent Coordination System — Governance Framework for A2A Networks
>
> **Status:** Draft · **Version:** 1.0 · **Last Updated:** 2026-07-03
>
> This specification defines the governance layer for A2A (Agent-to-Agent) networks:
> how agents prove who they are, how they earn behavioral trust, how their outputs
> are verified, and how security boundaries are enforced.
>
> It is a companion to the [A2A Protocol](a2a-protocol.md) and builds on the
> [Security Model](security-model.md). It does not replace either — it adds the
> governance dimension that sits between identity and operation.

---

## 1. Why Governance ≠ Identity

The A2A protocol gives every agent an Agent Card — a machine-readable identity
document exposed at `/.well-known/agent.json`. This answers one question:
**"Is this really Agent B?"**

But running a multi-agent network in production reveals three harder questions:

| Question | Answered by | Defined in |
|----------|-------------|------------|
| "Is this really Agent B?" | Agent Card (identity) | A2A Protocol |
| "Should I trust Agent B's output?" | Behavioral trust | §2 of this spec |
| "What if A and B disagree?" | Cross-validation | §3 of this spec |
| "What can B access?" | Security boundaries | §4 of this spec |

The A2A community recognized this separation early. In [A2A issue #1672][1672],
**pshkv** framed it explicitly:

> The Agent Card should carry only *authenticity* primitives — stable identifier,
> verification material, issuer/controller, signature, key rotation. Behavioral
> evidence (receipts, trust signals) should ride alongside, keyed to the same
> identifier, without overloading the card.

**kenneives** endorsed this split: "Card carries identity + a resolvable pointer;
behavioral/safety trust lives in separately-signed, independently-verifiable
evidence keyed to that identifier."

**desiorac** drew three orthogonal layers: **identity** (who), **confidentiality**
(who can read), **reputation** (should I?).

MACS implements this three-layer separation as a governance framework.

### The Three-Layer Model

```
┌─────────────────────────────────────────────┐
│  LAYER 3: GOVERNANCE (§3-4)                 │
│  Cross-validation · Security boundaries     │
│  Escalation · Audit                         │
├─────────────────────────────────────────────┤
│  LAYER 2: BEHAVIORAL TRUST (§2)             │
│  Decision receipts · Trust scores            │
│  Capability attestation · Continuity checks  │
├─────────────────────────────────────────────┤
│  LAYER 1: IDENTITY (§1, A2A Protocol)        │
│  Agent Card · Signing · Key Rotation         │
│  DID/Certificate · Discovery                 │
└─────────────────────────────────────────────┘
```

[1672]: https://github.com/a2aproject/A2A/issues/1672

---

## 2. Behavioral Trust Layer

### 2.1 Trust Signals

Identity proves an agent *is who it claims to be*. Trust is whether it
*does what it claims to do*. MACS defines five behavioral trust signals:

| Signal | What it measures | Collection method |
|--------|-----------------|-------------------|
| **Decision acceptance rate** | % of agent outputs accepted by downstream consumers without modification | Per-task tracking |
| **Cross-validation disagreement rate** | % of tasks where the verifying model disagrees with the primary | Automated (§3) |
| **Escalation rate** | % of tasks escalated to human review | Human audit log |
| **Capability drift** | Change in output quality when model/prompt changes | Continuous sampling |
| **Continuity violations** | Cases where agent behavior changed mid-session without intent change | Session boundary checks |

### 2.2 Trust Score

Each agent carries a **trust score** (0.0–1.0) computed from its trust signals:

```
trust_score = w₁ × acceptance_rate
            + w₂ × (1 − disagreement_rate)
            + w₃ × (1 − escalation_rate)
            − w₄ × drift_penalty
            − w₅ × continuity_penalty
```

Default weights: `w₁=0.35, w₂=0.25, w₃=0.15, w₄=0.15, w₅=0.10`

Weights are configurable per deployment. A deployment handling financial
decisions may weight disagreement_rate higher; a creative content pipeline
may weight it lower.

### 2.3 Trust Thresholds

| Threshold | Label | Effect |
|:---------:|-------|--------|
| ≥ 0.80 | **Trusted** | Full autonomy within security level |
| 0.50–0.79 | **Probationary** | Outputs receive automated spot-checks; cross-validation sample rate increased |
| < 0.50 | **Restricted** | All outputs require human review before action |
| < 0.30 | **Suspended** | No task delegation accepted; review required for reinstatement |

### 2.4 Decision Receipts

Following **desiorac**'s proposal in [A2A #1672][1672], every agent decision that
affects another agent's execution SHOULD produce a verifiable receipt:

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

Receipts form an append-only chain (`parent_receipt_id` links backward),
enabling full causal audit of multi-hop delegation chains.

---

## 3. Cross-Validation Protocol

### 3.1 Principle

> Any agent whose output cannot be mechanically verified MUST undergo
> dual-model cross-validation.

This principle comes from von Neumann's redundancy logic applied to cognitive
agents: different models make different errors, so disagreement surfaces
hidden flaws that a single model would silently pass.

### 3.2 Agent Classification

| Class | Definition | Cross-validation | Examples |
|:-----:|-----------|:----------------:|----------|
| **Objective** | Output is mechanically verifiable (compiles, passes tests, SQL returns correct rows) | Optional | do-developer, do-ops |
| **Subjective** | Output requires judgment (architecture decisions, strategy, product prioritization) | **Mandatory** | sg-architect, strategist, product |

### 3.3 Three-Level Adjudication

```
     ┌─────────────────┐
     │  Primary Model   │ (e.g., Claude Opus 4)
     │  proposes output │
     └────────┬────────┘
              │
              ▼
     ┌─────────────────┐
     │ Verifying Model  │ (e.g., DeepSeek V4 Pro)
     │ audits output    │
     └────────┬────────┘
              │
     ┌────────▼────────┐
     │  Compare verdict │
     └────────┬────────┘
              │
    ┌─────────┼─────────┐
    │         │         │
    ▼         ▼         ▼
 CONSENSUS  PARTIAL   DISAGREE
    │         │         │
    ▼         ▼         ▼
  PASS     QUALIFIED  ESCALATE
           PASS       TO HUMAN
```

| Level | State | Action | Audit |
|:-----:|-------|--------|-------|
| **consensus** | Both models agree | Output passes. Receipt records `verdict: "consensus"`. | Normal |
| **partial** | Agreement on structure, disagreement on details | Output passes with flags. Disagreed sections marked. Receipt records `verdict: "partial"` + diff. | Flagged |
| **disagree** | Fundamental disagreement | Output blocked. Escalated to human with both positions + diff. Receipt records `verdict: "disagree"`. | Escalated |

### 3.4 Model Pairing

The verifying model MUST be from a different vendor than the primary model.
Same-vendor pairing is **false redundancy** — the underlying training data
biases and architecture preferences do not change with prompt switching.

| Deployment | Primary | Verifying |
|-----------|---------|-----------|
| sg-architect | Claude Opus 4 | DeepSeek V4 Pro |
| Strategy | Claude Opus 4 | GPT-4o |
| Product | GPT-4o | Claude Opus 4 |

### 3.5 L0 Degradation

For low-risk, exploratory, or budget-sensitive scenarios, a single-model
"devil's advocate" mode is acceptable as a **degradation path**, not the default:

```
Primary Model → proposes output
Primary Model → switches role → critiques output
if self-critique finds serious issues → escalate to human
```

This is borrowed from Anthropic's approach but treated as L0 (degraded),
not equivalent to full cross-validation.

---

## 4. Security Boundaries

### 4.1 Security Levels

MACS inherits the three security levels defined in the [Security Model](security-model.md):

| Level | Trust | Access | Examples |
|:-----:|:-----:|--------|----------|
| **L1** | Highest | Architecture, budget, strategy decisions | sg-architect |
| **L2** | High | Core business data, codebase | do-developer, do-ops |
| **L3** | Standard | External/public information | cm-deepsight, if-explorer |

### 4.2 Cross-Level Communication

```
L1 → L2: ALLOWED (downward delegation)
L2 → L1: BLOCKED (upward data exfiltration prevention)
L1 → L3: ALLOWED
L3 → L1: BLOCKED
Lx → Ly (lateral, same level): ALLOWED through SG-ARCHITECT ROUTING ONLY
```

Direct lateral communication between agents at the same security level is
**prohibited**. All inter-agent communication routes through the architecture
governance agent (sg-architect), which enforces DAG topology constraints.

### 4.3 Trust Propagation in Delegation Chains

When Agent A (L1) delegates to Agent B (L2) which delegates to Agent C (L3):

```
Effective trust level = min(A.level, B.level, C.level) = L3
```

Each hop in the chain reduces the effective trust level to the minimum of
all participants. This prevents a high-trust agent from laundering authority
through a lower-trust agent.

### 4.4 Hard Constraints (Security Genes)

Six constraints are encoded at the system level, not per-agent — they cannot
be modified by any agent:

| # | Constraint | Enforcement |
|---|-----------|-------------|
| 1 | Charter is immutable | Gateway output validation |
| 2 | Security boundaries cannot be bypassed | API-level access control |
| 3 | Brake signal cannot be refused | <1 second cluster-wide propagation |
| 4 | Core data cannot be leaked | Pre-output sanitization |
| 5 | Budget cannot be self-modified | Hard token limit |
| 6 | Own genes cannot be modified | Gateway-level independent verification |

Violation → Gateway circuit breaker → Agent disabled → Human review → Retire or repair.

---

## 5. Audit Trail

### 5.1 Requirements

Every cross-agent delegation MUST produce an auditable trace:

```
Agent A → delegates Task T to Agent B → records:
  - trace_id: globally unique
  - parent_trace_id: A's own parent (null if origin)
  - agent_id: A
  - target_agent_id: B
  - task_id: T
  - timestamp: delegation time
  - decision_receipt: if cross-validation was applied (§2.4)
```

### 5.2 Implementation

The trace context SHOULD follow the [W3C Trace Context](https://www.w3.org/TR/trace-context/)
model adapted for agent semantics:

| W3C field | Agent equivalent |
|-----------|-----------------|
| `traceparent` | `a2a-traceparent: {version}-{trace_id}-{span_id}-{flags}` |
| `tracestate` | `a2a-tracestate: agent_id={id},task_id={id},security_level=L{n}` |

For Go implementations, see the proposed `a2aext/trace` package in
[a2a-go](https://github.com/a2aproject/a2a-go).

### 5.3 Non-Goals

The audit trail does NOT require:
- Centralized storage (agents MAY store traces locally or in a shared log)
- Real-time monitoring (traces are for post-hoc audit, not active alerting)
- Full-content capture (traces record metadata: who, when, what decision;
  full payload capture is a deployment concern)

---

## 6. Implementation in A2A

### 6.1 Agent Card Extensions

MACS-aware agents SHOULD declare governance capabilities in their Agent Card:

```json
{
  "name": "sg-architect",
  "capabilities": {
    "extensions": [
      "https://deeparchi.ai/macs/v1/governance",
      "https://deeparchi.ai/macs/v1/cross-validation"
    ]
  },
  "macs": {
    "security_level": "L1",
    "cross_validation": "mandatory",
    "trust_score": 0.92,
    "supported_verdicts": ["consensus", "partial", "disagree"]
  }
}
```

### 6.2 Governance Interceptor

A2A client and server interceptors (following the `a2aext` pattern) implement
MACS governance checks at the protocol level:

- **Server interceptor**: validates agent identity, checks security level,
  initiates cross-validation for subjective decisions
- **Client interceptor**: propagates trace context, attaches trust signals,
  verifies receipts from upstream agents

### 6.3 Relationship to Other Specifications

| Spec | Relationship |
|------|-------------|
| [A2A Protocol](a2a-protocol.md) | MACS builds on A2A; every MACS-governed network is an A2A network |
| [Security Model](security-model.md) | MACS inherits L1/L2/L3 levels; adds behavioral trust on top |
| [Feishu Integration](feishu-integration.md) | Human escalation (L3 verdict: disagree) routes through Feishu |
| [WLM](https://github.com/deeparchi-ai/wlm) | MACS resource governance implementation; goal-oriented scheduling for CPU and token budgets (§7) |
| [a2a-go `a2aext`](https://github.com/a2aproject/a2a-go/tree/main/a2aext) | Reference Go implementation of governance interceptors |

---

## 7. Resource Governance (WLM)

### 7.1 MACS Governs Resources, Not Just Decisions

Sections 2–4 define how MACS governs agent *decisions*: who to trust, how to
verify, what to allow. But governance is incomplete without resource control.
A network of trusted agents that collectively exhausts the API budget by 2 PM
is a governed failure — orderly, but still a failure.

MACS's resource governance layer answers: **who gets how much of the shared
resource pool, and who gets cut when the pool runs dry?**

### 7.2 The WLM Architecture: Observe → Arbitrate → Apply

MACS resource governance is implemented by **WLM** ([github.com/deeparchi-ai/wlm](https://github.com/deeparchi-ai/wlm)),
a goal-oriented scheduler modeled on [IBM z/OS Workload Manager](https://www.ibm.com/docs/en/zos/latest?topic=management-zos-workload-manager).
Four decades of mainframe workload management distilled into a three-stage
control loop:

```
┌─────────────────────────────────────────────┐
│  Service Policy (YAML)                       │
│  "sg-architect:  response <5s,  imp=1"       │
│  "do-developer:  keep working, imp=3"        │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│  WLM Daemon                                   │
│                                               │
│  ┌─────────┐   ┌──────────┐   ┌───────────┐  │
│  │ Observe │ → │Arbitrate │ → │   Apply    │  │
│  │ (PSI /  │   │(重要性)  │   │(cpu.weight│  │
│  │  burn   │   │          │   │ /限流)    │  │
│  │  rate)  │   │          │   │           │  │
│  └─────────┘   └──────────┘   └───────────┘  │
│       ↑                            │          │
│       └──── feedback loop ─────────┘          │
└──────────────────────────────────────────────┘
```

**Observe** reads real-time resource pressure — `cpu.pressure` from Linux PSI
for CPU mode, burn rate vs daily budget for token mode. **Arbitrate** applies
MACS importance levels: an importance-1 agent whose target is unmet takes
resources from importance-3 agents whose targets are already satisfied.
**Apply** translates the arbitration decision into kernel-level or API-level
enforcement.

This is not priority. Priority is static — "you're always higher than me."
WLM is goal-driven — "as long as your target is met, resources go to someone
else."

### 7.3 Two Resource Types, One Architecture

| Resource | Type | Agent contention | WLM mode |
|----------|------|:---:|----------|
| **CPU** | Renewable | Low — agents mostly wait on I/O | CPU WLM: PSI → cpu.weight |
| **Token budget** | Consumable — finite daily quota | **High** — shared API key, low-priority batch depletes high-priority reasoning | Token controller: burn rate → rate limiting |

CPU WLM is the **concept proof** — ~600 lines of Go, zero kernel dependencies,
7 unit tests covering all arbitration edge cases. It proved the three-stage
architecture works in user-space Linux.

Token budget control is the **product direction** — because in LLM agent
systems, CPU is not the bottleneck. Token budgets are.

### 7.4 Token Budget Controller

The same observe→arbitrate→apply skeleton runs on a different resource:

```
CPU mode                     →  Token mode
observe: PSI cpu.pressure    →  observe: burn rate vs daily budget
arbitrate: weight rebalance  →  arbitrate: high-imp class gets floor allocation
apply: cpu.weight            →  apply: API-level rate limiting / degradation
```

Four degradation levels (less aggressive than hard rejection):

| Level | Condition | Action |
|:-----:|-----------|--------|
| **Green** | Budget ample | Allow |
| **Yellow** | Burn rate elevated | Allow + suggest smaller model |
| **Red** | Budget tight | Rate-limit; auto-degrade (Opus→Haiku, skip non-critical steps) |
| **Black** | Budget exhausted | Only high-importance agents can call |

This is a **soft governor**, not a hard circuit breaker. Degradation signals
give agents a chance to self-regulate before the hard rejection kicks in —
the same principle as MACS's partial verdict in cross-validation (§3.3).

### 7.5 Integration with MACS Governance

Resource governance interacts with the other five governance dimensions:

| Dimension | WLM interaction |
|-----------|----------------|
| **Security boundaries (§4)** | Token limits are per-security-level: L1 agents have guaranteed floor allocation; budget exhaustion never blocks L1 |
| **Behavioral trust (§2)** | Burn rate anomalies are a trust signal — an agent that consistently overshoots its expected token consumption per task may be in a reasoning loop |
| **Cross-validation (§3)** | Cross-validation doubles token cost (primary + verifying model). WLM must account for this: if cross-validation pushes a task from green to yellow, the governance decision is "degrade, don't skip verification" |
| **Audit trail (§5)** | Resource allocation decisions (who was rate-limited, when, why) are trace events in the audit chain |
| **Escalation (§3.3)** | Black-level budget exhaustion triggers human notification via Feishu |

### 7.6 Relationship to API Provider Limits

API provider limits (OpenAI spend caps, Anthropic usage limits) are **hard
ceilings** on aggregate consumption. They answer "how much total?" WLM answers
"who gets it within that total?" Provider limits and WLM are complementary —
not alternatives.

### 7.7 Implementation Status

| Component | Status | Tests |
|-----------|:------:|:-----:|
| CPU WLM (cgroup v2 + PSI) | ✅ Complete — concept proof | 7 unit tests, E2E verified |
| Token budget controller | 🚧 Design phase — arbitration algorithm specified, Hermes integration designed | Arbitration test suite planned (min 7 boundary tests, matching CPU WLM coverage) |
| WLM ↔ Feishu alerting | 📋 Not started | — |

---

## 8. References

- [A2A Issue #1672 — Agent Identity Verification for Agent Cards](https://github.com/a2aproject/A2A/issues/1672)
- [W3C Trace Context Level 2](https://www.w3.org/TR/trace-context-2/)
- [IETF RATS — Remote Attestation Procedures](https://datatracker.ietf.org/wg/rats/about/)
- [agentrust-io/trace — Behavioral evidence layer](https://github.com/agentrust-io/trace) (proposed by imran-siddique)
- [MACS Reference Architecture (DeepArchi Vault)](https://github.com/deeparchi-ai/MAEA-Framework)
- [Cross-Validation Protocol — DeepArchi whitepaper series](https://deeparchi.ai)
- [WLM — Goal-oriented resource scheduler for MACS](https://github.com/deeparchi-ai/wlm)
- [IBM z/OS Workload Manager](https://www.ibm.com/docs/en/zos/latest?topic=management-zos-workload-manager)

---

> *MAEA Framework · DeepArchi Team*
> *2026-07-03 · [deeparchi.ai](https://deeparchi.ai)*
