# Contributing to MAEA

MAEA 是开源的。欢迎 Issue / PR / Discussion。

## 贡献方式

### 报告问题
发现 A2A 协议的边界情况？Agent 治理框架的漏洞？
→ [Open an Issue](https://github.com/deeparchi-ai/MAEA-Framework/issues)

### 改进规范
`specs/` 下的协议规范是 MAEA 的核心。如果你实现了 A2A 协议的变体或改进：
1. Open Issue 讨论
2. PR 附带实现 + 测试

### 添加 Claude Code Skill
如果你写了一个基于 MAEA 方法的 Claude Code Agent：
1. 参考 `claude-code/maea-architect.md` 的格式
2. 包含：能力声明、路由规则、交付物定义
3. PR 到 `claude-code/`

### 添加 Hermes Profile
如果你在 Hermes 上跑了 MAEA 网络的变体：
1. 去敏感信息后提交 Profile 模板
2. PR 到 `hermes/profiles/`

## 行为准则

- 务实优先：讨论聚焦「能解决什么问题」
- 薄层原则：能依赖外部协议的不自己实现
- 可验证：任何改进需附带验证方式
