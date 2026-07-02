# 🏛️ MAEA — Multi-Agent Enterprise Architecture Framework

[![Stars](https://img.shields.io/github/stars/deeparchi-ai/MAEA-Framework?style=flat-square)](https://github.com/deeparchi-ai/MAEA-Framework/stargazers)
[![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-brightgreen?style=flat-square)](https://github.com/deeparchi-ai/MAEA-Framework)

> 💡 MAEA 目前是一个**思考框架和参考架构**——协议规范、治理模型、Agent 设计方法论正在开放讨论和迭代中。
> 欢迎参与 [Discussions](https://github.com/deeparchi-ai/MAEA-Framework/discussions)。

> 当你的 AI Agent 超过 5 个时，MAEA 提供通信协议、治理框架和质量验证——
> 让 Agent 从「prompt 模板集合」升级为「可治理的 AI 团队」。

---

## 为什么需要 MAEA？

[agency-agents](https://github.com/msitarzewski/agency-agents) 用 232 个 Markdown 文件拿了 12.3 万星标。
但打开 Issues 区，票数最高的不是「加更多 Agent」，而是：

- 「这些 Agent 到底哪个好用？」（#11, 17 👍）
- 「我不得不自己写了个编排引擎」（#460）
- 「232 个我选不过来」（#634）

**需求已验证：不是缺 Agent，是缺治理。**

→ 深入阅读：[为什么 agency-agents 火了但不够用？](docs/why-maea.md)

---

---

## 架构全景

```
┌─────────────────────────────────────────────────────────┐
│                      人类 (飞书 DM)                       │
└──────────────────────┬──────────────────────────────────┘
                       │
              ┌────────▼────────┐
              │   DM Hub         │
              │  sg-architect   │  路由中枢 + 架构治理
              │   :9900          │
              └───┬──────┬──────┘
                  │      │
    ┌─────────────┤      ├─────────────┐
    │             │                   │
    ▼             ▼                   ▼
┌────────┐  ┌──────────┐      ┌──────────────┐
│ 研究层  │  │ 交付层    │      │  管理层       │
│:9920   │  │:9912:9910│      │  WLM          │
│deepsight│  │ dev  ops  │      │  资源调度     │
└────────┘  └──────────┘      └──────────────┘
    │             │                   │
    └─────────────┼───────────────────┘
                  │
         ┌────────▼────────┐
         │  工具层 (MCP)    │
         │  patent search   │
         └─────────────────┘
```

**三条总线，五层治理，8 个 Agent 已在飞书中运行。**

## MAEA 做什么

```
  人类 ──飞书──► DM Hub (sg-architect) ──A2A──► Agent A
                     │                            Agent B
                     │                            Agent C
                     └────MCP────► 工具层 (patent/search/...)
```

**三条通信总线：**

| 总线 | 协议 | 做什么 |
|------|------|--------|
| 🤝 Agent ↔ Agent | **A2A** | 委托、审查、冲突仲裁 |
| 🔌 Agent →工具 | **MCP** | 数据检索、专利分析、搜索 |
| 👤 人 → Agent | **飞书** | DM Hub 单界面路由 |

**五层治理模型：**

```
战略层   — sg-architect    架构治理 + 路由中枢
研究层   — cm-deepsight    深度研究 + 反方论证
交付层   — do-developer    编码实现 / do-ops 运维
管理层   — WLM             资源调度 (类 IBM z/OS WLM)
接入层   — gw-default      飞书 / A2A Gateway
```

→ 深入阅读：[框架全景](docs/overview.md) · [协议规范](specs/)

---

## 5 分钟开始

| 入口 | 门槛 | 你能做什么 |
|------|:---:|------|
| **[Claude Code](claude-code/)** | 30秒 | 一个治理 Agent inside Claude Code，帮你选 Agent +查冲突 |
| **[Hermes](hermes/)** | 30分钟 | 真实 A2A 网络，Agent 之间直接通信 + 飞书集成（MAEA 参考实现） |
| **[只读](docs/)** | 0分钟 | 纯方法论 + 协议规范 |

## 1 分钟跑起来

```bash
git clone https://github.com/deeparchi-ai/MAEA-Framework.git
cd MAEA-Framework/demo
python3 demo.py
```

输出：
```
Phase 1: Registry    ✅ 3 agents registered
Phase 2: A2A Ping    ✅ all 3 reachable
Phase 3: Delegate    ✅ task routed correctly
Phase 4: Conflict    ✅ overlap detected
```

4 个 Phase 验证 A2A 协议 + 注册表 + 路由 + 冲突检测，不依赖任何外部服务。

---

## 谁需要 MAEA

| 你 | 推荐入口 |
|----|---------|
| 🤖 个人开发者，3-5 个 Agent | [Claude Code skill](claude-code/) → 先体验治理 |
| 👥 团队，5+ Agent | [Hermes 参考实现](hermes/) → A2A 协议 + 注册表 |
| 🏗️ Agent 平台/框架开发者 | [specs/](specs/) → A2A 协议 + 注册表规范 |
| 📖 想了解方法论 | [docs/](docs/) → 治理框架 + Agent 设计 + 质量验证 |

---

## 生态

MAEA 是一个**框架**，不是一个产品。子项目：

| 项目 | 说明 |
|------|------|
| [macs](https://github.com/deeparchi-ai/macs) | 多 Agent 协调运行时 |
| [wlm](https://github.com/deeparchi-ai/wlm) | 目标驱动资源管理 (类 IBM WLM) |
| [patent-mcp](https://github.com/deeparchi-ai/patent-mcp-server) | 全球专利检索 MCP 工具 |
| [deepsight](https://github.com/deeparchi-ai/deepsight) | 深度推理研究法 |
| [deepblm](https://github.com/deeparchi-ai/deepblm-skill) | AI 时代 + BLM 战略框架 |

---

## 贡献

MAEA 是开源的。如果你也遇到了 Agent 治理的混乱——来一起建。

→ [CONTRIBUTING.md](CONTRIBUTING.md)

---

**12.3 万人收藏了 AI 梦之队。下一个问题不是「还能加什么 Agent」，是「谁来当主管」。**
