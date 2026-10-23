# A-004: Google A2A / Anthropic MCP

**状态**：已吸收·部分实现  
**日期**：2026-07-18（台账建档）  
**来源类型**：开源协议  
**权威出处**：Google A2A（2025-04 发布，后移交 Linux Foundation AAIF）；Anthropic Model Context Protocol

---

## 吸收了什么

| 来源机制 | MAEA 对应 | 说明 |
|---------|-----------|------|
| Agent Card | `/.well-known/agent.json` 发现端点 | 概念对齐 |
| Task 生命周期 | A2A `message/send`、`tasks/*` | 概念对齐，语义保留 |
| JSON/HTTP 传输 | 同 | 直接沿用 |
| MCP 工具调用 | 工具层（`specs/mcp-integration.md`） | Agent→工具的独立总线 |

**边界**：概念层对齐，实现层独立。Google A2A 偏向托管 Agent（Gemini Enterprise Agent Gallery）场景，MAEA A2A 面向自建 OPC 多 Agent 治理。

## 落点

- `specs/a2a-protocol.md`（v1.0，含 §8.1「与 Google A2A 的关系」）
- `specs/a2a-spec-v1.md`
- `specs/mcp-integration.md`
- `demo/`（纯 Python Minimal A2A 三 Agent 网络）

## 主动舍弃 / 未吸收

| 来源机制 | 为什么不吸收 |
|---------|-------------|
| Google 托管 Agent 的 Gallery 注册流程 | 依赖 Google Cloud 生态，OPC 场景不可用 |
| 推送通知（push notification） | v1 用轮询，避免 Agent 暴露公网回调端点 |
| gRPC 传输 | JSON/HTTP 足够，降低接入门槛 |

## 实现评估

| 实现 | 状态 | 记录 |
|------|------|------|
| Hermes 运行时（27+ Agent A2A :99xx） | ✅ 在产 | 走 MAEA A2A 语义 |
| `demo/` Minimal A2A | ✅ 公开可跑 | 三 Agent 网络 |
| MACS 自动发现 | 采纳 | `macs/decisions/ADR-002` |
| 标准兼容性（A2A TCK） | ⚠️ 未验证 | 待确认：未与 A2A 官方 TCK 对表 |

## 备注

- Chronicle（§4）已通过 [a2a-go PR #377](https://github.com/a2aproject/a2a-go/pull/377) 向上游回灌 trace context 能力——这是唯一一条"反向贡献"，其余为单向吸收。
- MCP 侧：工具级访问由 MCP 承担，不额外开 A2A 监听（薄层原则）。
