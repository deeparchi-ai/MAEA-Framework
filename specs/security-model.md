# 安全模型

MAEA 框架的安全边界定义——控制 Agent 能做什么、不能做什么。

## 安全等级

| 等级 | 定义 | 范围 | 示例 Agent |
|:----:|------|------|----------|
| **L1** | 接触架构/预算/战略决策 | 最高信任 | sg-architect |
| **L2** | 接触核心业务数据/代码 | 高信任 | do-developer, do-ops |
| **L3** | 接触外部/公开信息 | 标准信任 | cm-deepsight, if-explorer |

> ⚠️ **传输安全**：L2 和 L3 层的 bearer token 必须通过 TLS（HTTPS）传输，禁止在明文 HTTP 信道传递。

## 权限模型

### 最小权限原则

每个 Agent 只拥有完成任务所需的最小权限集。入网审查时校验：
- 能力声明是否超出角色范围
- 是否有不必要的 MCP Server 访问
- 是否有不必要的 A2A 通信权限

### 传输安全

L2 和 L3 层的 bearer token 必须通过 TLS（HTTPS）传输，禁止在明文 HTTP 信道传递。

### 信任传递

A2A 委托链中，下游 Agent 的信任等级取上游 Agent 和自身等级的较小值：

```
L1 → L2 → L3 委托链
信任等级 = min(L1, L2, L3) = L3
```

## 入网审查

新 Agent 入网需通过 sg-architect 的审查：

1. **拓扑校验**：不与已有 Agent 产生循环依赖
2. **能力冲突检测**：不与已有 Agent 职责重叠（重叠需仲裁）
3. **安全边界验证**：MCP Server 访问权限、A2A 通信范围
4. **身份验证**：四名合一 (Profile = A2A peer = routing agent = registry id)

## 决策审计

所有 `human_review_required` 的决策必须记录：
- 决策 ID + 时间戳
- 主推理 + 交叉验证结果
- 最终裁决 + 人工审批人
