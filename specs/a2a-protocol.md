# MAEA A2A Protocol v1.0

**Agent-to-Agent 通信协议规范**
**MAEA Framework · 2026-07-18**
**协议版本：1.0**

---

## 一、协议定位

A2A（Agent-to-Agent）是 MAEA 框架中 Agent 之间的标准化通信协议。它定义了 Agent 如何**发现彼此、委托任务、交换结果**。

A2A 与 MCP 的关系：
- **MCP**：Agent → Tool 的单步调用（模型到工具的协议）
- **A2A**：Agent → Agent 的多步协作（Agent 到 Agent 的协议）

两者不是竞品，是不同层。一个完整的多 Agent 系统需要两者共存。

---

## 二、核心设计

### 2.1 协议基础

- **传输层**：HTTP/1.1 over TCP
- **序列化**：JSON（UTF-8）
- **端口隔离**：每个 Agent 运行在独立端口
- **安全模型**：信任等级分层（见 §6）

### 2.2 两条核心端点

| 端点 | 方法 | 用途 |
|------|------|------|
| `GET /.well-known/agent.json` | GET | Agent 发现（返回 Agent Card） |
| `POST /tasks` | POST | 任务委托（发送 Task，返回 TaskResult） |

### 2.3 设计原则

1. **最小依赖**：纯 HTTP + JSON，stdlib 可实现
2. **能力声明**：Agent Card 是交互前提——不知道对方能做什么就不该调它
3. **委托链追踪**：每条任务携带 `context_id`，跨 Agent 委托可追溯
4. **置信度量化**：每次委托附带 `confidence` 评分（0.0-1.0）
5. **可逆性标记**：不可逆决策标记 `human_review_required`

---

## 三、数据结构

### 3.1 Agent Card

每个 A2A Agent 启动时暴露发现端点，返回其身份和能力。

```
GET /.well-known/agent.json
```

```json
{
  "name": "sg-architect",
  "description": "架构治理与路由中枢",
  "url": "http://127.0.0.1:9900",
  "protocolVersion": "1.0",
  "capabilities": {
    "streaming": false,
    "pushNotifications": false
  },
  "skills": [
    {"id": "architecture_review", "name": "架构评审"},
    {"id": "registry_maintenance", "name": "注册表维护"},
    {"id": "dag_validate", "name": "DAG 拓扑校验"}
  ]
}
```

**字段规范**：

| 字段 | 类型 | 必须 | 说明 |
|------|------|:---:|------|
| `name` | string | ✅ | Agent 唯一标识，全局唯一 |
| `description` | string | ✅ | 一句话描述 |
| `url` | string | ✅ | Agent 的 HTTP 访问地址（含端口） |
| `protocolVersion` | string | ✅ | A2A 协议版本号 |
| `capabilities` | object | ✅ | 能力标志（streaming/pushNotifications） |
| `skills` | array | ✅ | 暴露的技能列表，每个含 `id` + `name` |

### 3.2 Task

A2A 的委托消息体。

```json
{
  "id": "sg-architect-a1b2c3",
  "skill": "deep_research",
  "prompt": "分析为什么 AI Agent 团队需要治理框架",
  "context_id": "demo-delegation-001",
  "confidence": 0.9,
  "human_review_required": false,
  "metadata": {
    "language": "zh-CN"
  }
}
```

**字段规范**：

| 字段 | 类型 | 必须 | 说明 |
|------|------|:---:|------|
| `id` | string | ✅ | 任务唯一 ID（建议格式：`{sender}-{uuid前6位}`） |
| `skill` | string | ✅ | 目标技能 ID（必须在目标 Agent Card 的 skills 中） |
| `prompt` | string | ✅ | 任务描述（自然语言） |
| `context_id` | string | ✅ | 全局追踪 ID，跨 Agent 委托链保持一致 |
| `confidence` | float | | 发起方对该委托的置信度评分（0.0-1.0），默认 1.0 |
| `human_review_required` | bool | | 该决策是否需要人类审批，默认 false |
| `metadata` | object | | 扩展字段（目标 URL、语言偏好、结构化参数等） |

### 3.3 TaskResult

A2A 的响应消息体。

```json
{
  "task_id": "sg-architect-a1b2c3",
  "status": "success",
  "output": {
    "researcher": "cm-deepsight",
    "findings": ["市场上存在 125k 星标的 AI Agent 集合", "用户痛点不是缺 Agent，而是缺少治理"],
    "confidence": 0.9
  },
  "artifacts": [
    {
      "filename": "generated_module.py",
      "content": "# Generated code\nprint('hello maea')\n",
      "language": "python"
    }
  ]
}
```

**字段规范**：

| 字段 | 类型 | 必须 | 说明 |
|------|------|:---:|------|
| `task_id` | string | ✅ | 对应请求的 `task.id` |
| `status` | string | ✅ | `success` / `pending` / `error` |
| `output` | object | ✅ | 任务执行结果（自由格式 JSON） |
| `artifacts` | array | | 产物列表（代码文件、报告等） |

**status 语义**：
- `success`：任务已完成，结果在 `output` 中
- `pending`：任务已接受但异步执行中（需配合推送通知，暂未在 1.0 中标准化）
- `error`：任务执行失败，错误信息在 `output.error` 或 `output.detail` 中

### 3.4 Skill

技能声明的最小单元。

```json
{
  "id": "deep_research",
  "name": "深度研究"
}
```

`id` 是唯一标识符（用于 Task 路由），`name` 是人类可读名称。

---

## 四、通信流程

### 4.1 发现 → 委托

```
Agent A                              Agent B
  │                                     │
  │  GET /.well-known/agent.json        │
  │ ──────────────────────────────────► │
  │                                     │
  │  ← AgentCard (name, skills, url)    │
  │                                     │
  │  POST /tasks  {Task}                │
  │ ──────────────────────────────────► │
  │                                     │
  │  ← TaskResult                       │
  │                                     │
```

### 4.2 委托链（多 Agent 协作）

```
sg-architect → cm-deepsight → do-developer
  context_id: "demo-001" （不变）

每个 Agent 在响应中附加审计日志，
委托链的 output 嵌套结构可追溯完整调用路径。
```

### 4.3 入网审查（四步审查）

新 Agent 加入 MAEA 网络时，Registry Agent 执行四步审查：

1. **拓扑校验**：检测 DAG 循环依赖
2. **能力冲突检测**：检查 skill id 重叠
3. **安全边界验证**：验证安全等级与声明的技能是否匹配
4. **身份验证**：验证四名合一（name/url/skill/profile 一致）

```json
// 注册
POST /tasks → Registry
{
  "skill": "register",
  "metadata": {
    "card": { /* AgentCard */ },
    "security_level": 2
  }
}

// 审查
POST /tasks → Registry
{
  "skill": "onboarding_review",
  "metadata": {
    "candidate_name": "do-developer",
    "edges": [["sg-architect", "do-developer"]]
  }
}
```

---

## 五、拓扑约束

### 5.1 DAG 原则

Agent 之间的调用关系必须形成**有向无环图（DAG）**。不允许循环依赖——A 调 B、B 调 C、C 调 A 构成循环，入网审查直接拒绝。

### 5.2 拓扑变更

每次拓扑变更（新 Agent 入网 / 能力声明变更 / 委托关系调整）必须通过 DAG 校验。校验由 `sg-architect`（架构治理 Agent）执行：

```json
POST /tasks → sg-architect
{
  "skill": "dag_validate",
  "metadata": {
    "edges": [
      ["sg-architect", "cm-deepsight"],
      ["cm-deepsight", "do-developer"]
    ]
  }
}
```

---

## 六、信任与安全模型

### 6.1 三层信任

| 信任等级 | 场景 | 安全措施 |
|:---:|------|------|
| L1 | 本地回环（127.0.0.1） | 无需认证 |
| L2 | 同主机，不同用户 | Bearer Token |
| L3 | 跨主机 / 跨网络 | Bearer Token + IP 白名单 + TLS |

MAEA 参考实现默认使用 L1（所有 Agent 在同一台机器上通过本地回环通信）。

### 6.2 审计日志

所有跨域 A2A 调用记录审计日志，包含：
- 调用方 Agent name
- 目标 Agent name + URL
- Task ID + context_id
- 时间戳
- 响应状态

审计日志可用于溯源任何跨 Agent 决策链。

### 6.3 安全 Gene（MAEA 扩展）

在 MAEA 完整实现中，Agent 的安全约束（不可修改章程、最小权限、刹车指令等）由 Gateway 层强制执行。A2A 协议层不感知安全 Gene——它是 MAEA 治理框架的增强，非协议本身的组成部分。

---

## 七、参考实现

MAEA 提供了一个最小可运行的 Python 参考实现，零外部依赖（仅 stdlib）：

```bash
git clone https://github.com/deeparchi-ai/MAEA-Framework.git
cd MAEA-Framework/demo
python3 demo.py
```

参考实现包含：
- `protocol.py`：A2A 协议核心（AgentCard / Task / TaskResult / A2AServer / fetch_agent_card / send_task）
- `agents.py`：三个参考 Agent（SGArchitect / CMDeepSight / DODeveloper）
- `registry.py`：Registry Agent + 入网审查四步流程

三文件合计约 800 行 Python，可在任何 Python 3.8+ 环境运行。

---

## 八、与行业协议的关系

### 8.1 与 Google A2A 的关系

Google 于 2025 年 4 月发布 A2A 协议（后移交 Linux Foundation AAIF），MAEA A2A 在概念层与其对齐（Agent Card、Task、JSON/HTTP），但在具体实现上保持独立：
- Google A2A 更偏托管 Agent 场景（与 Gemini Enterprise Agent Gallery 集成）
- MAEA A2A 更偏本地 Agent 治理场景（轻量级、零依赖、可自托管）

两者在概念层兼容——任何实现了 Agent Card + Task 模式的 Agent 可以在适配层对接。

### 8.2 与 MCP 的关系

MAEA 使用 MCP 作为 Agent → Tool 的协议，A2A 作为 Agent → Agent 的协议。两者共存，互不替代：
- MCP：`Agent → firecrawl_scrape(url=...)`（工具调用）
- A2A：`sg-architect → POST /tasks → cm-deepsight`（Agent 间委托）

---

## 九、版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 0.1 | 2026-06 | 初始草案（Hermes A2A 子集） |
| 0.3 | 2026-07 | Agent Card + Task/Result 数据结构定型 |
| **1.0** | **2026-07-18** | **从 MAEA 框架中抽出，独立版本。加入 DAG 约束、三层信任、入网审查流程、参考实现。** |

---

## 十、参考

- [MAEA 框架白皮书](../docs/MAEA-whitepaper-zh.md)
- [MAEA Demo 参考实现](../demo/)
- [Google A2A Protocol (Linux Foundation AAIF)](https://github.com/google/A2A)
- [Model Context Protocol (Anthropic)](https://modelcontextprotocol.io/)
