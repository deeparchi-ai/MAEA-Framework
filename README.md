# AEG 的组织面 · MAEA Framework

> AEG（Agent Execution Governance · Agent 执行治理）治理的是 **Agent 做了什么**，不是模型是什么。一个 Agent 成立，一百个更成立。
>
> **MAEA 是 AEG 的组织面**：管一群 Agent 怎么编制、谁能改什么、委派链有没有环、不可逆操作谁来复核。
> 单次执行上的策略、证据与复核由 [macs](https://github.com/deeparchi-ai/macs) 承担（执行面）。

## 组织面做什么

| 能力 | 回答的问题 | 在仓库里的位置 | 现状 |
|---|---|---|---|
| **编制** | 谁在岗、几个域、每层管什么 | [docs/MAEA-whitepaper-zh.md](docs/MAEA-whitepaper-zh.md)（框架总览）· [demo/](demo/) | 参考实现（编制表为参考示例） |
| **章程** | 谁能改什么、什么不可改 | [docs/MAEA-whitepaper-zh.md](docs/MAEA-whitepaper-zh.md)（安全治理：不可修改章程 / 安全边界 / 预算） | 规格 + 参考实现 |
| **拓扑校验** | 委派链有没有环、能力是否冲突、能不能越域 | [specs/A2A-spec-v1.md](specs/A2A-spec-v1.md) §8 · [demo/README.md](demo/README.md) 入网审查 | DAG 无环 + 四名合一 + 域隔离 + 能力冲突已实现；**孤点、委派深度、爆炸半径仅为口径，未实现** |
| **交叉验证** | 不可逆操作谁投反对票、多模型怎么裁决 | 编制表「交叉验证」列 · macs [XVal](https://github.com/deeparchi-ai/macs-xval-go) | 规格 + 执行面实现 |

四个部件的执行面视角（刹车 / 黑匣子 / 双人复核 / 适航审定）见 [macs README](https://github.com/deeparchi-ai/macs)。

## 术语

| 术语 | 含义 |
|---|---|
| **AEG**（Agent Execution Governance · Agent 执行治理） | 品类。治理的是 Agent 做了什么，不是模型是什么 |
| **执行面 · MACS** | 单次执行上的四件事：单调策略、跨 Agent 证据树、XVal 交叉验证、编制校验 → [macs](https://github.com/deeparchi-ai/macs) |
| **组织面 · MAEA** | 编制、章程、拓扑校验、交叉验证的组织侧规格 → [MAEA-Framework](https://github.com/deeparchi-ai/MAEA-Framework) |
| **单调策略** | 刹车：每次工具调用前判定，只能更严、不能放宽，默认只记录 |
| **跨 Agent 证据树** | 黑匣子：根 + 全部子 Agent，事实与判定按 callId 对齐，判决带当时策略哈希 |
| **XVal** | 双人复核：不可逆操作上一张反对票就升级，多数票不盖过 |
| **编制校验** | 适航审定：环、孤点、委派深度、爆炸半径、预算合计 |

## 编制与预算（参考示例，非承诺报价）

> 下表是**参考示例，非承诺报价**：用来演示「编制 × 预算」的写法，不构成对任何第三方的价格承诺。
> 示例的完整版本（含工号、首选模型、交叉验证分工）见 [docs/MAEA-whitepaper-zh.md](docs/MAEA-whitepaper-zh.md)。

| 域 | Gateway | Agent | 月预算（示例） |
|---|---|---|---|
| 战略与治理域 | :9900 | 架构治理、战略分析、风控合规 | ¥9,000 |
| 交付与运营域 | :9901 | 工程交付、数据智能、运营编排、基础设施运维 | ¥6,200 |
| 客户与市场域 | :9902 | 产品方案、市场拓展 | ¥3,000 |
| 创新与前沿域 | :9903 | 前沿探索 | ¥800 |
| 企业服务域 | :9904 | 财务行政 | ¥1,900 |

预算在这里不是财务字段，是**编制约束**：每个 Agent 在预算内运行，超额熔断；预算变更走章程里的人工审批口。

---

## 实现说明

### 三条通信总线

| Bus | Protocol | Purpose |
|---|---|---|
| Agent ↔ Agent | **A2A** | 委托、复核、冲突仲裁 |
| Agent → Tools | **MCP** | 数据检索、专利分析、搜索 |
| Human → Agent | **Feishu** | 单入口路由（DM Hub） |

### 参考实现拓扑

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

三条总线、五层治理模型，运行在 Hermes Agent 平台上（编制明细见 whitepaper，示例值）。

**五层治理模型：**

```
Strategy   — sg-architect    架构治理 + 路由中枢
Research   — cm-deepsight    深度研究 + 反方论证
Delivery   — do-developer    代码实现 / do-ops 运维
Management — WLM             工作负载管理（IBM z/OS WLM 风格，工程类比）
Gateway    — gw-default      飞书 / A2A 网关
```

## Why MAEA?

[agency-agents](https://github.com/msitarzewski/agency-agents) 的 star 数到 2026-11-15 为 168k（仓库自身 API 读数），Markdown 文件 330 个。
但打开它的 Issues，高票的都不是「多加几个 Agent」：

- 「有 benchmark 吗？」（#11，18 👍，2026-11-15 API 读数）
- 「我自己写了一套编排引擎」（#460）
- 「232 个 Agent 我选不出来」→ 现状是「帮我挑一个该用哪个 Agent」的请求（#634）

**需求已经被验证：缺的不是更多 Agent，是治理。**

→ 展开：[为什么是 MAEA](docs/why-maea.md)

## 生态

MAEA 是框架，不是产品。相关子项目：

| Project | 角色 |
|------|------|
| [macs](https://github.com/deeparchi-ai/macs) | AEG 的执行面（14 个子系统） |
| [wlm](https://github.com/deeparchi-ai/wlm) | 目标驱动资源调度（IBM WLM 风格） |
| [patent-mcp-server](https://github.com/deeparchi-ai/patent-mcp-server) | 通过 MCP 做全球专利检索 |
| [deepsight](https://github.com/deeparchi-ai/deepsight) | 深度推理研究方法论 |
| [deepblm-skill](https://github.com/deeparchi-ai/deepblm-skill) | AI 时代的 BLM 战略框架 |

## 上手

> 耗时为本机手测预估，不是承诺值。

| 入口 | 耗时（预估） | 能做什么 |
|------|:---:|------|
| [Claude Code](claude-code/) | ~30s | 在 Claude Code 里跑一个治理 Agent——挑 Agent、查冲突 |
| [Hermes](hermes/) | ~30min | 真实 A2A 网络、Agent 间通信 + 飞书集成（参考实现） |
| [只读](docs/) | 0min | 方法论 + 协议规格 |

## 1 分钟跑起来

```bash
git clone https://github.com/deeparchi-ai/MAEA-Framework.git
cd MAEA-Framework/demo
python3 demo.py
```

输出（2026-11-15 本机实跑，已截取关键行）：

```
🏛️  MAEA Framework — Minimal A2A Demo
   python3 demo.py | 4 phases | 3 agents | stdlib only

Phase 1: 启动 A2A 网络
  ✅ registry        listening on http://127.0.0.1:9999
  ✅ sg-architect    listening on http://127.0.0.1:9996
  ✅ cm-deepsight    listening on http://127.0.0.1:9997
  ✅ do-developer    listening on http://127.0.0.1:9998

Phase 2: 入网审查
  ✅ approved     sg-architect
  ✅ approved     cm-deepsight
  ✅ approved     do-developer

Phase 3: 任务委托链     研究 → 实现 → 风险三段委托
Phase 4: 关闭网络       全部 stopped
```

4 个阶段：启动 A2A 网络、入网审查（DAG 校验 + 能力冲突 + 安全边界 + 四名合一）、三段委托链、关闭网络。**零外部依赖**（仅标准库）。

## 谁需要 MAEA

| 你 | 从这里开始 |
|------|---------|
| 独立开发者，3–5 个 Agent | [Claude Code skill](claude-code/) → 先体验治理 |
| 团队，5+ 个 Agent | [Hermes 参考实现](hermes/) → A2A 协议 + 注册表 |
| Agent 平台/框架构建者 | [specs/](specs/) → A2A 协议 + 注册表规格 |
| 看方法论 | [docs/](docs/) → 治理 + Agent 设计 + 质量验证 |
| 关心我们的想法从哪来 | [docs/adoptions/](docs/adoptions/) → 采用登记表：每个外部来源、取什么、不取什么 |

## 参与

MAEA 是开源的。如果你也在被一群不受治理的 Agent 淹没——一起把治理层做出来。

→ [CONTRIBUTING.md](CONTRIBUTING.md)

---

> *DeepArchi · MIT License*
