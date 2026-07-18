# MAEA 差异化定位

> 三句话说明 MAEA 是什么、不是什么、为什么选它。

---

## 一句话定位

**MAEA 是面向 AI 原生组织的多 Agent 企业架构治理框架——不是 Agent 工作台，不是算力底座，而是连接 Agent 能力与组织治理的中间层基础设施。**

---

## 对比表

| 维度 | MAEA Framework | StaffDeck（面壁） | PPIO Agentic Cloud | Google Managed Agents | CrewAI / AutoGen |
|------|:---:|:---:|:---:|:---:|:---:|
| 定位 | 治理框架 | Agent 工作台 | 商业算力底座 | 全托管 Agent 平台 | Agent 编排库 |
| 开源 | ✅ MIT | ✅ AGPL-3.0 | ❌ 商业云 | ❌ 闭源 SaaS | ✅ MIT |
| 可私有化 | ✅ | ✅ | ✅ | ❌ | ✅ |
| 安全等级 | L1-LS 四级 | — | — | Google 云 IAM | — |
| 双模型验证 | ✅ 内置 | ❌ | ❌ | ❌ | ❌ |
| Agent 生命周期 | ✅ 入职→绩效→退役 | ❌ | ❌ | ✅（托管内） | ❌ |
| 审计追溯 | ✅ DAG+回执 | ❌ | ❌ | ✅（托管内） | ❌ |
| 月成本 | ¥20,900 | 社区版免费 | 按量 | 按 token | 自托管 |
| 目标用户 | 企业架构师/CTO | 个人开发者 | AI 应用开发者 | 全球 SaaS 企业 | Python 开发者 |
| 适合场景 | 金融/政企/合规 | 快速原型 | 降本 | 海外市场 | 实验/教学 |

---

## 三句话

**1. MAEA 不是「又一个 Agent 框架」——市场上不缺编排库（CrewAI/AutoGen），MAEA 解决的是编排之上、应用之下的治理问题：谁可以调用谁？决策如何追溯？安全边界在哪里？**

**2. MAEA 不是「又一个 AI 平台」——Google/PPIO 提供托管 Agent 和算力，MAEA 提供在这些平台上运行的治理层。可以跑在 Google Cloud 上，也可以跑在国产云上——MAEA 不锁定任何底座。**

**3. MAEA 适合的是那些「Agent 不只是实验，已经成为生产系统」的组织——当你有 5+ 个 Agent、跨多个域、需要合规审计、需要预算控制的时候，MAEA 的价值才会显现。**

---

## 不做清单

- ❌ 不做 Agent 注册中心/Store/搜索引擎——这是大厂赛道
- ❌ 不做模型训练/微调——MAEA 是多模型消费者，不生产模型
- ❌ 不做低代码 Agent 搭建——不是可视化编排工具
- ❌ 不做通用 AI 咨询——MAEA 是框架，不是服务包

---

## 与竞争对手的关系

| 竞品 | 关系 | 说明 |
|------|------|------|
| StaffDeck | 潜在竞争 | 面壁有 118K 总星的开源社区基因，可能向上扩展到治理层 |
| PPIO | 互补 | 商业云底座，无 Agent 框架野心，是天然的合作方 |
| Google Managed Agents | 不同市场 | Google 面向全球 SaaS，MAEA 面向中国政企/合规市场 |
| CrewAI / AutoGen | 互补 | 编排层工具，MAEA 可以在其之上提供治理能力 |

---

*本文是 MAEA 框架的定位说明，会随竞品格局变化持续更新。*
*最新版本见 [MAEA-Framework/docs/zh/differentiation.md](https://github.com/deeparchi-ai/MAEA-Framework/blob/main/docs/zh/differentiation.md)*
