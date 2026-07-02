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

## 开发流程

### 环境设置

```bash
git clone https://github.com/deeparchi-ai/MAEA-Framework.git
cd MAEA-Framework
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt  # 如有
```

### 提交 PR

1. **Fork** 仓库并创建分支: `git checkout -b feat/your-feature`
2. **改动** + 测试: 确保 `demo/demo.py` 能跑通
3. **提交**: 使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式
   - `feat:` 新功能
   - `fix:` 修复
   - `docs:` 文档
   - `spec:` 协议规范变更
4. **PR**: 描述改动 + 为什么 + 如何验证
5. **Review**: 至少 1 位 maintainer 批准

### 目录约定

| 目录 | 内容 | 修改规则 |
|------|------|---------|
| `specs/` | 协议规范（A2A/MCP/安全） | 需 Issue 讨论后 PR |
| `demo/` | 参考实现 | 保持零外部依赖 |
| `docs/` | 方法论和博客 | 欢迎改进 |
| `hermes/` | Hermes Profile 模板 | 去敏感信息后提交 |
| `claude-code/` | Claude Code Skill | 参考现有格式 |

### 规范变更流程

`specs/` 下的 A2A/MCP/安全规范是 MAEA 的核心：

1. Open Issue → 讨论设计
2. PR 附带:
   - 规范变更（specs/ 文件）
   - 实现验证（demo/ 或 hermes/ 的参考实现）
   - 向后兼容说明

## 许可证

贡献即同意 MIT 许可证。详见 [LICENSE](LICENSE)。
