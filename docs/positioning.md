# MAEA 差异化定位

**一句话：StaffDeck 管一个 Agent 怎么干活，PPIO 管 Agent 跑在哪，MAEA 管一群 Agent 怎么不乱。**

---

## 竞争格局

| 维度 | StaffDeck（面壁智能） | PPIO | MAEA（DeepArchi） |
|------|----------------------|------|-------------------|
| **定位** | Agent 开发框架 | Agent 推理基础设施 | 多 Agent 治理框架 |
| **回答的问题** | 怎么做一个能干的 Agent？ | Agent 跑在什么云上？ | 5+ Agent 怎么不打架？ |
| **核心机制** | MCP 工具调用 + 模型编排 | GPU 调度 + 推理加速 | A2A 协议 + DAG 拓扑 + 治理层 |
| **适用阶段** | Agent 从 0 到 1 | Agent 从单机到集群 | Agent 从 1 到 N |
| **类比** | 员工培训手册 | 办公室租赁 | 组织架构图 + 公司制度 |

---

## 为什么 MAEA 是不同的品类

StaffDeck 和 PPIO 都在解决「单个 Agent」的问题。但当你有 5 个、10 个、20 个 Agent 时，新问题出现：

- **能力冲突**：两个 Agent 都声称能做「代码审查」，任务该发给谁？
- **循环依赖**：A 委托 B、B 委托 C、C 委托 A——谁来打断？
- **安全边界**：能访问预算的 Agent 被不该调它的 Agent 调了——谁负责拦截？
- **质量退化**：Agent 集群跑了一个月，模型幻觉越来越多——谁在监测？
- **爆炸半径**：一个 Agent 出错，错误结果在委托链里传播——爆炸范围多大？

这些问题不是单个 Agent 的问题，是**组织治理**问题。

MAEA 不是一个 Agent 开发框架。**MAEA 是 Agent 组织的管理框架。**

---

## 核心护城河

### 1. A2A 协议——Agent 间的标准化通信

StaffDeck 目前只有 MCP（Agent ↔ Tool），没有标准化 Agent 间通信协议。这意味着：
- 多 Agent 协作靠硬编码调用
- 没有统一的 Agent 发现机制
- 委托链不可追溯

MAEA 的 A2A 协议提供 Agent Card 发现、Task 委托、委托链追踪、置信度量化——这些是多 Agent 组织运作的通信基础设施。

### 2. DAG 拓扑治理——谁可以调谁

MAEA 强制执行 DAG（有向无环图）拓扑约束。每个 Agent 的调用关系在入网时审查，不允许循环依赖。这比「所有 Agent 可以互相调」的星型拓扑更安全，也比「靠文档约定」更可靠。

### 3. 五层治理模型——有层级结构

MAEA 将 Agent 组织为 5 个功能层，每层有明确的职责边界和安全等级。这不是技术分层，是**组织分层**——对标企业架构的域模型。

### 4. 入网审查——Agent 不是即插即用

新 Agent 加入 MAEA 网络时，Registry 执行四步审查：拓扑校验 → 能力冲突检测 → 安全边界验证 → 身份验证。通过的 Agent 才获得 A2A 通信权限。

### 5. 可验证的运行实例

MAEA 不是一个白皮书框架。它是一个正在运行的 9-Agent 组织：
- 月预算 ¥20,900
- 6 家模型供应商
- 双模型交叉验证
- 真实的 Slack/飞书交付通道
- 开源的参考实现（`demo/` 目录，800 行 Python，零依赖）

---

## 品类心智：多 Agent 治理框架

| 品类 | 代表 | 心智 |
|------|------|------|
| Agent 开发框架 | StaffDeck, LangChain, CrewAI | 「怎么做 Agent」 |
| Agent 推理平台 | PPIO, Together AI, Fireworks | 「Agent 跑在哪」 |
| **多 Agent 治理框架** | **MAEA** | **「Agent 团队怎么管」** |

三个品类是一条链上的三个环节：**开发 → 部署 → 治理**。

MAEA 的目标不是取代 StaffDeck 或 PPIO——而是定义第三个环节。当一个团队用 StaffDeck 做好 Agent、用 PPIO 部署好 Agent 后，他们需要第三个工具来管理这些 Agent 的协作关系。那个工具就是 MAEA。

---

## 市场时机

**为什么是现在？**

1. **StaffDeck 验证了「Agent 开发框架」品类**——但它停留在单 Agent 层面
2. **Google A2A 协议（2025.4）验证了 Agent 间通信标准化的需求**——但它是大厂协议，偏托管场景
3. **agency-agents（125k stars）验证了人们对「AI 团队」的渴望**——但它的 Issues 里全是治理诉求
4. **面壁智能的社区势能正在成型**——在它从「单 Agent 框架」扩展到「多 Agent 治理」之前，MAEA 需要先占据这个品类

**战略窗口：StaffDeck 的社区还在关心「怎么做更好的 Agent」，还没开始大规模问「Agent 多了怎么管」。当那个问题成为主流问题时，MAEA 应该是第一个被想到的答案。**

---

## 一句话（对外用）

> **StaffDeck tells your Agent how to do its job. PPIO finds it a desk. MAEA draws the org chart.**

---

*深度架构 · 邝谧*
*2026-07-18*
