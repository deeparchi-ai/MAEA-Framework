# 飞书接入规范

飞书即时通讯平台——MAEA 框架中人类与 Agent 的交互界面。

## 设计原则

### DM Hub 模式

> 用户只跟一个 Agent 对话，该 Agent 负责路由到其他 Agent 并汇总回复。

```
用户 ──DM──► sg-architect ──A2A──► Agent A
                  │               │ Agent B
                  │               │ Agent C
                  └── 汇总 ←──────┘
```

优势：
- 用户不需要知道有几个 Agent、它们叫什么
- 单频道、单线程交互
- A2A 委托回执透明嵌入回复

### 群聊模式

Agent 参与飞书群聊，遵循规则：
- 只在被 `@mention` 时回复
- Agent 之间不在群内对话（走 A2A）
- 项目群用于 Sprint 管理（心跳报告、质量门、确认点）

## Bot 身份

每个 Agent 可选独立飞书 Bot 身份：

| 配置 | 说明 |
|------|------|
| App ID + Secret | 飞书开发者后台获取 |
| open_id | Bot 在群聊中的身份标识 |
| require_mention | 群内是否只在被 @ 时响应 |

## 跨 App 交互

飞书限制：不同 App 的 Bot 之间不能直接互动。跨 App 场景使用 `--as user` 以用户身份操作。

## 审批群

A2A 鉴权使用飞书群聊人工确认 (HITL)：
1. 新 Agent 发出配对请求
2. sg-architect 向审批群发送确认码
3. 人类回复确认码 → 通过
