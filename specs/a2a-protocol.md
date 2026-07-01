# A2A 协议规范

Agent-to-Agent 通信协议——MAEA 框架中 Agent 之间的协作基础。

## 协议概述

A2A 协议定义了 Agent 之间如何发现、委托和交换结果。它建立在 HTTP/JSON 之上，端口隔离，支持本地回环和跨主机通信。

## Agent Card

每个 Agent 在启动时暴露一个发现端点：

```
GET /.well-known/agent.json
```

返回结构：

```json
{
  "name": "sg-architect",
  "description": "架构治理 Agent",
  "url": "http://127.0.0.1:9900",
  "protocolVersion": "0.3",
  "capabilities": {
    "streaming": false,
    "pushNotifications": false
  },
  "skills": [
    {"id": "architecture_review", "name": "架构评审"},
    {"id": "registry_maintenance", "name": "注册表维护"}
  ]
}
```

## 通信模式

### 同步调用

```
Agent A → POST /tasks → Agent B
Agent B → 处理 → 返回结果
Agent A ← 接收结果
```

### 委托链

Agent A 可以向 Agent B 发起任务委托，Agent B 可继续委托给 Agent C。每条委托附带：
- `context_id`：全局追踪 ID
- `confidence`：置信度评分
- `human_review_required`：是否需要人工审批

## 拓扑约束

- Agent 之间的调用关系形成有向无环图 (DAG)
- 不允许循环依赖
- 每次拓扑变更需通过 `sg-architect` 的 DAG 校验

## 信任模型

| 信任等级 | 说明 |
|---------|------|
| L1 | 本地回环，无需认证 |
| L2 | 同主机，bearer token |
| L3 | 跨主机，bearer token + IP 白名单 |

## 协议版本

当前版本：`0.3`

遵守 [Hermes A2A 协议](https://github.com/NousResearch/hermes-agent) 规范。
