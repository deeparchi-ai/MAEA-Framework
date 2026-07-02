# MAEA Middleware Specification

> **Version:** 1.0 · **Status:** Draft · **Last Updated:** 2026-07-03
>
> MAEA middleware is the transaction processing layer for multi-agent systems.
> It sits between agents and the MACS Agent OS, providing routing, session
> management, multi-protocol communication, and lifecycle control — the
> functions that IBM CICS has provided for COBOL programs since 1969.
>
> This specification together with the [MACS Governance Spec](macs-governance-spec.md)
> forms the complete MAEA architecture:
>
> ```
> Agent (sg-architect, do-developer...)
>         │
>         ▼
> ┌───────────────────────────────┐
> │  MAEA Middleware (this spec)  │  ← ≈ CICS
> │  Routing · Session · Lifecycle│
> └───────────────┬───────────────┘
>                 │
>                 ▼
> ┌───────────────────────────────┐
> │  MACS Agent OS                │  ← ≈ z/OS
> │  WLM · Security · Audit · XVal│
> └───────────────────────────────┘
> ```

---

## 1. CICS Lineage

IBM CICS has run the world's highest-volume transaction systems for over 50
years. Its core insight: **isolation does not require per-unit OS processes.**
One Address Space hosts hundreds of concurrent transactions, each with its own
Task Control Block. MAEA middleware applies the same pattern to agent systems.

| CICS Concept | MAEA Equivalent | What it does |
|-------------|----------------|-------------|
| **Address Space** | Hermes Gateway (single process) | Hosts all agents sharing one platform connection |
| **Task Control Block (TCB)** | Agent Session Context | Per-agent: workspace, memory, skills, conversation state |
| **Program Control Table (PCT)** | Agent Registry + Routing Table | Maps `capability → agent_id`, hot-reloadable |
| **Resource Definition Online (RDO)** | Profile spawn/stop | Add/remove agents without gateway restart |
| **Pseudo-conversational** | Session persistence | State written to disk between turns, restored on next message |
| **EXEC CICS LINK** | A2A sync call | "I need your answer now" |
| **EXEC CICS START** | A2A async delegate | "Handle this when you can" |
| **PCT transaction ID** | `mention @agent-name` | Human-addressable agent invocation |
| **COMMAREA** | Session state blob | Data passed between turns of the same conversation |

---

## 2. Routing — Agent Registry

### 2.1 Capability-Based Routing

The registry answers one question: **"who can do X?"** It is not a static
peer list. It is a capability map that agents query at runtime to make
delegation decisions.

```
Task: "review this architecture decision"
       │
       ▼
Registry query: capability = "architecture_review"
       │
       ▼
Match: sg-architect (confidence=0.95, A2A enabled, L1)
       │
       ▼
Delegate via A2A sync call
```

### 2.2 Registry Schema

Each agent declares capabilities, not identity. The registry is the single
source of truth for routing decisions:

```yaml
agents:
  - id: sg-architect
    domain: strategy-governance
    security_level: L1
    a2a_enabled: true
    a2a_url: http://127.0.0.1:9900
    capabilities:
      - type: architecture_review
        confidence: 0.95
        how_to_ask: "Review this architecture decision..."
      - type: registry_maintenance
        confidence: 0.90
      - type: topology_validation
        confidence: 0.92
```

### 2.3 Routing Decision Flow

When an agent needs to delegate:

1. **Extract capability** from the task description
2. **Query registry** — match by `capability.type`
3. **Single match** → delegate directly
4. **Multiple matches** → select by: (a) A2A enabled, (b) higher confidence,
   (c) matching security level, (d) available concurrency
5. **No match** → degrade: self-handle → chain-ask → escalate to human

### 2.4 DAG Topology

Agent call relationships form a directed acyclic graph. The architecture agent
(sg-architect) validates the DAG on every topology change:

```
sg-architect (L1)
    ├──→ do-developer (L2)
    │       └──→ do-ops (L2)
    ├──→ cm-deepsight (L3)
    │       └──→ if-explorer (L3)
    └──→ es-reimbursement (L3)
```

Cycles are forbidden. Lateral communication (L3→L3) routes through
sg-architect. Upward communication (L2→L1) is blocked at the MACS security
layer.

### 2.5 Multi-Match Prioritization

When multiple agents declare the same capability:

| Priority | Criterion | Rationale |
|:--------:|-----------|-----------|
| 1 | `a2a_enabled = true` | No A2A = unreachable |
| 2 | Higher `confidence` | Self-reported capability strength |
| 3 | Matching `security_level` | Don't send L1 work to L3 agent |
| 4 | Available concurrency | Don't overload a busy agent |
| 5 | Model language match | Chinese tasks → agents with Chinese-native models |

---

## 3. Communication — Three Buses

### 3.1 Bus Architecture

MAEA middleware routes messages across three protocol buses:

```
┌──────────────────────────────────────────┐
│  MAEA Middleware                          │
│                                           │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  │
│  │   A2A   │  │   MCP   │  │  Feishu │  │
│  │ Agent↔  │  │ Agent→  │  │ Human→  │  │
│  │ Agent   │  │ Tools   │  │ Agent   │  │
│  └────┬────┘  └────┬────┘  └────┬────┘  │
│       │            │            │        │
│       ▼            ▼            ▼        │
│    A2A Client   MCP Client   Feishu GW   │
│    (HTTP/JSON)  (stdio/HTTP)  (Webhook)  │
└──────────────────────────────────────────┘
```

### 3.2 A2A: Agent-to-Agent

Agent-to-agent communication follows the [A2A Protocol](a2a-protocol.md).
Two patterns:

**Synchronous (LINK)** — the caller waits for a response:

```
POST /tasks
{
  "message": { "role": "user", "parts": [{"type": "text", "text": "..."}] },
  "context_id": "ctx-abc123"
}

Response: Task with status "completed" + output artifacts
```

**Asynchronous (START)** — fire and forget:

```
POST /tasks
Response: 202 Accepted (task queued)

Caller polls: GET /tasks/{task_id} → status
```

### 3.3 MCP: Agent-to-Tool

Model Context Protocol connects agents to external tools. MCP Servers are
thin layers — they wrap existing APIs, hold no data, and implement no
business logic.

| Principle | Rule |
|-----------|------|
| **Dependency over implementation** | MCP Server forwards to authoritative sources |
| **Stateless** | No caching; each request is independent |
| **Capability-first** | Tool descriptions are the primary selection signal |

Current MCP ecosystem:

| Server | Purpose | Protocol |
|--------|---------|----------|
| maea-registry | Agent registry queries | stdio |
| firecrawl | Web search + crawl | HTTP |

### 3.4 Feishu: Human-to-Agent

The human entry point follows a **DM Hub pattern**: the user talks to one
agent (sg-architect), which routes to the right backend agent and returns
a unified response.

```
User (Feishu DM)
    │
    ▼
sg-architect (DM Hub)
    │
    ├── A2A → cm-deepsight (research)
    ├── A2A → do-developer (code)
    └── A2A → do-ops (infra)
    │
    ▼
Aggregated response → User
```

Group chat adds a **mention-based interaction model** (§5).

---

## 4. Session — Pseudo-Conversational State

### 4.1 The CICS Pattern

CICS transactions are pseudo-conversational: they appear continuous to the
user, but the program terminates between interactions. State is written to
COMMAREA and restored on the next message. This avoids holding memory for
thousands of idle terminals.

MAEA middleware applies the same pattern to agent conversations:

```
Turn N:   Agent receives message → loads state from disk → processes → saves state → responds
Turn N+1: Agent receives message → loads state from disk → processes → ...
```

### 4.2 State Model

```json
{
  "session_id": "sess-20260703-a1b2c3",
  "agent_id": "sg-architect",
  "context_id": "ctx-abc123",
  "parent_session_id": null,
  "chat_id": "oc_xxx",
  "thread_id": "omt_xxx",
  "created": "2026-07-03T10:00:00Z",
  "last_active": "2026-07-03T10:05:00Z",
  "turn_count": 5,
  "conversation_state": {
    "current_task": "architecture_review",
    "pending_decisions": ["model_selection"],
    "delegated_to": ["cm-deepsight"]
  }
}
```

### 4.3 State Lifecycle

| Event | Action |
|-------|--------|
| First message in thread | Create new session |
| Subsequent message | Load session from disk → restore context |
| Session idle > 30 min | Mark dormant → eligible for compression |
| Session idle > 24 hr | Archive → write summary to audit log |
| Explicit `/new` or `/reset` | Terminate session → start fresh |

### 4.4 Cross-Session Continuity

For tasks spanning multiple sessions (e.g., multi-day consulting reports),
the middleware provides a progress log and task registry — the Anthropic
Harness pattern adopted by Hermes. See the
[session-bootstrap](https://github.com/deeparchi-ai/MAEA-Framework/blob/main/hermes/session-bootstrap.md)
skill documentation.

---

## 5. Agent Lifecycle

### 5.1 The RDO Pattern

IBM CICS RDO (Resource Definition Online) allows operators to define new
programs and transactions while CICS is running — no shutdown required.
MAEA middleware provides the same capability: agents can be spawned, stopped,
and reconfigured without gateway restart.

### 5.2 Spawn

```
hermes profile create do-analyzer
hermes profile edit do-analyzer   # model, skills, tools
hermes profile start do-analyzer  # launches A2A server on :9913
```

The new agent:
1. Generates an Agent Card at `/.well-known/agent.json`
2. Registers capabilities in the Agent Registry
3. Undergoes onboarding review (§5.4)
4. Appears in routing decisions immediately

### 5.3 Stop

```
hermes profile stop do-analyzer   # graceful: drain active tasks
hermes profile stop --force do-analyzer  # immediate: kill + notify delegates
```

Graceful stop: finish in-flight tasks, reject new ones, unregister from registry.
Forced stop: MACS brake signal (<1s), task state saved for recovery.

### 5.4 Onboarding Review

New agents pass through sg-architect's four-point review before joining the
network:

1. **Topology validation** — does not create cycles in the DAG
2. **Capability conflict detection** — no overlapping responsibilities
3. **Security boundary assignment** — L1/L2/L3, MCP access, A2A scope
4. **Four-name alignment** — Profile name = A2A peer name = routing key = registry ID

### 5.5 Naming Convention

```
{prefix}-{role}

Prefix (MAEA domain):
  sg = Strategy & Governance    (:9900-:9904)
  do = Delivery & Operations    (:9910-:9914)
  cm = Client & Market          (:9920-:9924)
  if = Innovation & Frontier    (:9930-:9934)
  es = Enterprise Services      (:9940-:9944)
  gw = Gateway / Default        (:9000)

Example: sg-architect, do-developer, cm-deepsight
```

---

## 6. Group Chat Governance

### 6.1 The Problem

Without governance, agents in shared chat groups exhibit three failure modes:

1. **Unsolicited speech** — agents respond to messages not addressed to them
2. **Cross-layer leakage** — internal agents expose architecture details in external groups
3. **Agent-to-agent chatter** — agents converse in groups instead of routing through A2A

### 6.2 Four-Layer Group Model

| Layer | Type | Examples | Agent behavior |
|:-----:|------|----------|---------------|
| **L0** | All-hands | Company-wide | All agents respond when @mentioned |
| **L1** | Team | Engineering, Research | Domain agents free to respond |
| **L2** | Project | Sprint, Deployment | Specified agents monitor actively |
| **L3** | Restricted / External | Client, Partner | Strict mention-only; no internal data |

### 6.3 Mention-Based Interaction

Agents in group chats follow a single rule: **respond only when @mentioned.**
No agent initiates conversation. No agent replies to un-addressed messages.
This is the CICS transaction ID pattern — the terminal operator specifies
which program to invoke.

```
User: "@sg-architect review this PR"
sg-architect: [responds]

User: "what do you all think?"   ← no @mention
[all agents remain silent]
```

### 6.4 Agent-to-Agent Communication in Groups

Agents do not communicate with each other in group chats. Agent-to-agent
communication routes through A2A (§3.2), outside the group channel. This
keeps group chats human-readable and prevents agent chatter from drowning
human conversation.

### 6.5 Stop Command Precedence

If a human in a group sends "stop" or "停止" without @mentioning a specific
agent, the default gateway agent (gw-default) interprets it as a brake
command and triggers MACS §3.5 Gene 3 across the cluster.

### 6.6 Specialized Agent Silence Rule

Some agents serve a single function (e.g., es-reimbursement processes expense
reports). They MUST remain completely silent in all groups that are not
related to their function — even when @mentioned. Silence is not a bug; it
is the designed behavior for single-function agents.

---

## 7. Middleware ↔ MACS Interface

The middleware layer does not enforce governance policy — it routes to the
OS that does. Every agent request, regardless of entry path, passes through
the same MACS kernel checks:

```
Online path:  Feishu → Middleware (route) → MACS (enforce) → Agent
Batch path:   Cron   → MACS (enforce) → Agent
A2A path:     Agent  → Middleware (route) → MACS (enforce) → Agent
```

| Middleware function | MACS subsystem that enforces it |
|--------------------|-------------------------------|
| Route to agent | §3 Security: L-level check before execution |
| Delegate task | §4 Audit: trace span attached |
| Spawn agent | §3 Security: onboarding review assigns L-level |
| Batch trigger | §2 WLM: token budget check. §4 Audit: job lifecycle trace |
| Group mention | §3 Security: L-level determines which agents are reachable in which groups |

---

## Appendix A: CICS Concept Mapping

| CICS | MAEA Middleware | Status |
|------|----------------|:------:|
| Address Space | Hermes Gateway | ✅ |
| TCB (Task Control Block) | Agent Session Context | ✅ |
| PCT (Program Control Table) | Agent Registry + routing | ✅ |
| RDO (Resource Definition Online) | Profile spawn/stop | ✅ |
| Pseudo-conversational | Session state persistence | ✅ |
| EXEC CICS LINK | A2A sync (message/send) | ✅ |
| EXEC CICS START | A2A async (task delegate) | ✅ |
| COMMAREA | Session state blob | ✅ |
| Transaction ID | @mention agent-name | ✅ |
| Terminal auto-install | Agent Card discovery | ✅ |
| CICS SPOOL | Cron output queue (→ JES §6) | 📋 |

---

## Appendix B: Deployment Reference

### Current Network (as of 2026-07-03)

| Agent | Prefix | Port | Security | Model |
|-------|:------:|:----:|:--------:|-------|
| gw-default | gw | :9000 | L2 | DeepSeek V4 Pro |
| sg-architect | sg | :9900 | L1 | DeepSeek V4 Pro |
| do-ops | do | :9910 | L2 | DeepSeek V4 Flash |
| do-developer | do | :9912 | L2 | Kimi k2.6 |
| cm-deepsight | cm | :9920 | L3 | DeepSeek V4 Pro |
| cm-success | cm | :9921 | L3 | DeepSeek V4 Pro |
| if-explorer | if | :9930 | L3 | DeepSeek V4 Pro |
| es-reimbursement | es | :9940 | L3 | Kimi k2.6 |

---

> *MAEA Framework · DeepArchi Team*
> *2026-07-03 · [deeparchi.ai](https://deeparchi.ai)*
