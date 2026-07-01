# MCP 集成规范

Model Context Protocol (MCP) 工具层——MAEA 框架中 Agent 获取外部数据的能力来源。

## 协议概述

MCP 是 Agent 与外部工具之间的标准化协议。MCP Server 提供 `tools/list` 和 `tools/call` 端点。

## 设计原则

### 薄层原则

> MCP Server 是薄层——封装已有 API，不持有数据，不实现业务逻辑。

- **依赖 > 实现**：MCP Server 转发请求到权威数据源，不做二次计算
- **不持有数据**：无状态，不缓存，每个请求独立
- **能力声明优先**：Server 的能力声明 (tool descriptions) 是 Agent 选型的主要依据

### MCP 不入注册表

MCP Server 和 Agent 是两类不同的实体：

| | Agent | MCP Server |
|---|---|---|
| 注册位置 | agent_registry.yaml | mcp_registry.yaml |
| 通信协议 | A2A | MCP stdio/HTTP |
| 主动发起 | 可以 | 不可以 |
| 有身份 | 有 (工号/档案) | 无 |

## 当前 MCP 生态

| MCP Server | 用途 | 协议 |
|------------|------|------|
| patent-mcp | 全球专利检索 | stdio |
| firecrawl | Web 搜索与爬取 | HTTP |
| maea-registry | Agent 注册表查询 | stdio |

## 添加 MCP Server

1. 实现 MCP 协议的 `tools/list` + `tools/call`
2. 在 `mcp_registry.yaml` 中注册
3. 在 Agent 的 `config.yaml` 的 `mcp_servers` 段中启用
