# 🏛️ MAEA — Multi-Agent Enterprise Architecture Framework

[![Stars](https://img.shields.io/github/stars/deeparchi-ai/MAEA-Framework?style=flat-square)](https://github.com/deeparchi-ai/MAEA-Framework/stargazers)
[![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-brightgreen?style=flat-square)](https://github.com/deeparchi-ai/MAEA-Framework)

> 💡 MAEA is a **governance framework and reference architecture** — protocol specs, governance models, and Agent design methodology. Open for discussion and iteration.
> Join the [Discussions](https://github.com/deeparchi-ai/MAEA-Framework/discussions).

> When you have more than 5 AI Agents, MAEA provides communication protocols, governance frameworks, and quality validation —
> turning your Agents from "a pile of prompt templates" into "a governable AI team."

---

## Why MAEA?

[agency-agents](https://github.com/msitarzewski/agency-agents) earned 125k stars with 232 Markdown files.
But open the Issues tab — the top-voted items aren't "add more Agents":

- "Which of these agents actually work?" (#11, 17 👍)
- "I had to build my own orchestration engine" (#460)
- "I can't choose among 232 agents" (#634)

**The demand is validated: it's not more Agents people need — it's governance.**

→ Deep dive: [Why agency-agents went viral but wasn't enough](docs/why-maea.md)

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Human (Feishu DM)                     │
└──────────────────────┬──────────────────────────────────┘
                       │
              ┌────────▼────────┐
              │   DM Hub         │
              │  sg-architect   │  Routing + Governance
              │   :9900          │
              └───┬──────┬──────┘
                  │      │
    ┌─────────────┤      ├─────────────┐
    │             │                   │
    ▼             ▼                   ▼
┌────────┐  ┌──────────┐      ┌──────────────┐
│Research│  │ Delivery │      │  Management  │
│:9920   │  │:9912:9910│      │  WLM         │
│deepsight│ │ dev  ops  │      │  Scheduler   │
└────────┘  └──────────┘      └──────────────┘
    │             │                   │
    └─────────────┼───────────────────┘
                  │
         ┌────────▼────────┐
         │  Tools (MCP)     │
         │  patent search   │
         └─────────────────┘
```

**Three buses, five layers, 8 Agents running on Feishu today.**

## What MAEA Does

```
  Human ──Feishu──► DM Hub (sg-architect) ──A2A──► Agent A
                     │                              Agent B
                     │                              Agent C
                     └────MCP────► Tools (patent/search/...)
```

**Three Communication Buses:**

| Bus | Protocol | Purpose |
|------|------|--------|
| 🤝 Agent ↔ Agent | **A2A** | Delegation, review, conflict arbitration |
| 🔌 Agent → Tools | **MCP** | Data retrieval, patent analysis, search |
| 👤 Human → Agent | **Feishu** | Single-interface routing via DM Hub |

**Five-Layer Governance Model:**

```
Strategy   — sg-architect    Architecture governance + routing hub
Research   — cm-deepsight    Deep research + red-team argumentation
Delivery   — do-developer    Code implementation / do-ops operations
Management — WLM             Workload management (IBM z/OS WLM style)
Gateway    — gw-default      Feishu / A2A Gateway
```

→ Further reading: [Why MAEA](docs/why-maea.md) · [Positioning vs StaffDeck/PPIO](docs/positioning.md) · [Whitepaper (中文)](docs/MAEA-whitepaper-zh.md) · [A2A Protocol v1.0](specs/a2a-protocol.md)

---

## Get Started

| Entry Point | Time | What You Can Do |
|------|:---:|------|
| **[Claude Code](claude-code/)** | 30s | A governance Agent inside Claude Code — picks Agents, detects conflicts |
| **[Hermes](hermes/)** | 30min | Real A2A network, inter-Agent comms + Feishu integration (reference impl) |
| **[Read only](docs/)** | 0min | Methodology + protocol specs |

## Run in 1 Minute

```bash
git clone https://github.com/deeparchi-ai/MAEA-Framework.git
cd MAEA-Framework/demo
python3 demo.py
```

Output:
```
Phase 1: Registry    ✅ 3 agents registered
Phase 2: A2A Ping    ✅ all 3 reachable
Phase 3: Delegate    ✅ task routed correctly
Phase 4: Conflict    ✅ overlap detected
```

4 phases validating A2A protocol + registry + routing + conflict detection. **Zero external dependencies.**

---

## Who Needs MAEA

| You | Start Here |
|------|---------|
| 🤖 Solo dev, 3–5 Agents | [Claude Code skill](claude-code/) → experience governance first |
| 👥 Team, 5+ Agents | [Hermes reference impl](hermes/) → A2A protocol + registry |
| 🏗️ Agent platform/framework builder | [specs/](specs/) → A2A protocol + registry spec |
| 📖 Here for the methodology | [docs/](docs/) → governance + Agent design + quality validation |

---

## Ecosystem

MAEA is a **framework**, not a product. Sub-projects:

| Project | Description |
|------|------|
| [macs](https://github.com/deeparchi-ai/macs) | Multi-Agent Coordination Runtime |
| [wlm](https://github.com/deeparchi-ai/wlm) | Goal-driven resource scheduler (IBM WLM style) |
| [patent-mcp](https://github.com/deeparchi-ai/patent-mcp-server) | Global patent search via MCP |
| [deepsight](https://github.com/deeparchi-ai/deepsight) | Deep reasoning research methodology |
| [deepblm](https://github.com/deeparchi-ai/deepblm-skill) | BLM strategy framework for the AI era |

---

## Contributing

MAEA is open source. If you're also drowning in ungoverned Agents — let's build the governance layer together.

→ [CONTRIBUTING.md](CONTRIBUTING.md)

---

**125,000 people bookmarked an AI dream team. The next question isn't "what other Agents can we add?" — it's "who's in charge?"**
