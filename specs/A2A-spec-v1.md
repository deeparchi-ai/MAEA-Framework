# A2A 协议规范 v1

> 从 [MAEA 白皮书](../docs/zh/maea-whitepaper.md) 抽出，独立为完整协议规范。
> 版本: 1.0 · 2026-07-18

---

## 1. 协议定位

A2A（Agent-to-Agent）是 MAEA 框架中 Agent 间跨域协作的标准协议。它定义 Agent 如何彼此发现、委托任务、传递结果和追踪决策链。

A2A 不替代 MCP（Model Context Protocol）——MCP 是 Agent 到工具的通道，A2A 是 Agent 到 Agent 的通道。两者构成 MAEA 的双协议栈。

## 2. 核心设计原则

| 原则 | 说明 |
|------|------|
| **DAG 拓扑** | Agent 间调用关系必须形成有向无环图，禁止循环依赖 |
| **审计追溯** | 每次跨域调用产生完整审计记录（发起方/接收方/时间/结果） |
| **域隔离** | 同域走 Gateway 内部通道（零网络开销），跨域走 A2A HTTP |
| **最小权限** | Agent 只能调用授权范围内的对端 Agent，不可任意发现 |
| **可逆优先** | 任何不可逆的跨域委托必须标记 `human_review_required` |

## 3. 三种通信关系

MAEA 定义了三种 Agent 间关系，A2A 协议覆盖其中两种：

| 线型 | 关系 | 通道 | 延迟 | A2A? |
|------|------|------|------|:---:|
| 金实线 | 治理授权 | 人类→治理域 | — | — |
| 青实线 | 域内编排 | Gateway 内部 | μs | ❌ |
| 灰虚线 | 跨域协作 | HTTP A2A | ms | ✅ |

## 4. Agent Card — 发现端点

每个 Agent 在 Gateway 启动时暴露：

```
GET /.well-known/agent.json
```

### 响应结构

```json
{
  "name": "sg-architect",
  "description": "架构治理 Agent — 入网审查、注册表维护、模型选型、拓扑校验",
  "url": "http://127.0.0.1:9900",
  "protocolVersion": "1.0",
  "capabilities": {
    "streaming": false,
    "pushNotifications": false,
    "dual_model_verification": true
  },
  "skills": [
    {"id": "agent_onboarding", "name": "入网审查"},
    {"id": "registry_maintenance", "name": "注册表维护"},
    {"id": "model_selection", "name": "模型选型"},
    {"id": "architecture_review", "name": "架构评审"},
    {"id": "topology_validation", "name": "拓扑校验"}
  ],
  "trust_tier": "L1",
  "domain": "strategy_governance",
  "port": 9900
}
```

### 字段说明

| 字段 | 必填 | 说明 |
|------|:---:|------|
| `name` | ✅ | Agent 标识名，必须与 registry 一致 |
| `url` | ✅ | Gateway 地址 |
| `protocolVersion` | ✅ | A2A 协议版本 |
| `capabilities.streaming` | ✅ | 是否支持流式响应 |
| `capabilities.dual_model_verification` | — | 是否启用双模型交叉验证 |
| `skills` | ✅ | 可委托的能力列表 |
| `trust_tier` | ✅ | 安全等级 (L1/L2/L3/LS) |
| `domain` | ✅ | 所属业务域 |

## 5. 委托模型

### 5.1 同步委托

```
Agent A → POST /tasks → Agent B
Agent B → 处理 → 返回结果
Agent A ← 接收结果
```

请求体：

```json
{
  "context_id": "ctx_abc123",
  "task": {
    "type": "architecture_review",
    "params": {
      "target_agent": "cm-deepsight",
      "scope": "full"
    }
  },
  "caller": {
    "name": "sg-architect",
    "domain": "strategy_governance"
  },
  "confidence": 0.85,
  "human_review_required": false,
  "timestamp": "2026-07-18T10:00:00Z"
}
```

响应体：

```json
{
  "context_id": "ctx_abc123",
  "result": {
    "status": "completed",
    "confidence": 0.92
  },
  "processed_by": "cm-deepsight",
  "duration_ms": 2340
}
```

### 5.2 委托链

Agent A 委托 Agent B，Agent B 可继续委托 Agent C。规则：

- 每条委托独立携带 `context_id`，链路可追溯
- 链中任一节点失败，沿链回传错误
- 跨域委托必须经过 bridge-bootstrap 审计

### 5.3 委托回执

每次 A2A 委托完成后，发起方应在回复末尾附加回执摘要：

```
🔄 A2A 委托摘要
─────────────────
→ cm-deepsight :9920  "深度行业研究"
← cm-deepsight        用时 23s | "已完成BLM推演"
─────────────────
```

## 6. 信任模型

| 等级 | 范围 | 认证 | 适用 |
|:---:|------|------|------|
| L0 | 同域本地回环 | 无需 | Gateway 内部 |
| L1 | 同主机 | Bearer token | 核心域 Agent |
| L2 | 同网段 | Bearer token | 交付/客户域 |
| L3 | 跨主机 | Bearer token + IP 白名单 | 远程 Agent |

**注意**：无 Bearer token 时，Hermes 平台强制绑定 `127.0.0.1`。配置 token 后才会绑定 `0.0.0.0` 开放跨主机通信。

## 7. 安全 Gene — A2A 层约束

A2A 层强制执行六条安全 Gene：

| # | 约束 | A2A 层面实现 |
|---|------|------------|
| 1 | 不可修改章程 | Gateway 校验委托任务类型是否在授权范围内 |
| 2 | 不可绕过安全边界 | 仅可调用对端 Agent Card 中声明的 skills |
| 3 | 不可拒绝刹车 | 全局 brake 信号通过 A2A broadcast 在 <1s 内传播 |
| 4 | 不可泄露核心数据 | 委托参数中的敏感数据自动脱敏 |
| 5 | 不可自行修改预算 | A2A 层不计费，Token 消耗由各 Gateway 独立控制 |
| 6 | 不可修改自身 Gene | A2A 不提供基因修改接口 |

## 8. 拓扑校验

### 8.1 DAG 约束

Agent 间调用关系形成有向无环图（DAG）。每次拓扑变更（新 Agent 入网、能力声明更新、跨域委托规则修改）必须通过 `sg-architect` 的 DAG 校验。

### 8.2 校验规则

- **四名合一**：Profile name = A2A peer name = routing agent name = registry id，必须完全一致
- **无循环**：BFS 遍历检测闭环
- **域隔离检查**：跨域委托必须明确声明，默认不允许
- **能力冲突检测**：新 Agent 声明的 skills 不与现有 Agent 重叠

### 8.3 命名规范

- 前缀：`sg/`（战略治理）、`do/`（交付运营）、`cm/`（客户市场）、`if/`（创新前沿）、`es/`（企业服务）、`gw/`（网关）
- 端口段对齐：9900-9904（五域 Gateway），9910-9919（域内 Agent）

## 9. 协议演进

| 版本 | 日期 | 变更 |
|:---:|------|------|
| 0.3 | 2026-06 | 初始版：Agent Card + 同步委托 + DAG 拓扑 |
| 1.0 | 2026-07 | 新增：委托链审计、安全 Gene 映射、三种通信关系、回执规范 |

## 10. 与 Hermes A2A 的关系

MAEA A2A 协议基于 [Hermes A2A 协议](https://github.com/NousResearch/hermes-agent) 规范，在其基础上增加了：
- 企业级审计追溯（`context_id` + bridge-bootstrap）
- 安全 Gene 映射
- DAG 拓扑校验
- 三种通信关系（金实线/青实线/灰虚线）
- 委托回执规范

MAEA A2A 向后兼容 Hermes A2A 0.3。
