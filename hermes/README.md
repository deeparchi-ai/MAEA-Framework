# MAEA on Hermes — 参考实现

MAEA 框架在 [Hermes Agent](https://github.com/NousResearch/hermes-agent) 上的完整参考实现。

## 架构概览

```
DM Hub (sg-architect :9900)
  ├──A2A── cm-deepsight (:9920)  深度研究
  ├──A2A── do-ops (:9910)        运维
  ├──A2A── if-explorer (:9930)   创新探索
  ├──A2A── do-developer (:9912)  编码
  ├──MCP── patent-mcp            专利检索
  └──MCP── firecrawl             Web 搜索
```

## Agent Profile 清单

| Agent | 端口 | 模型 | 职责 |
|-------|:----:|------|------|
| sg-architect | 9900 | DS v4-pro | 架构治理 + DM Hub |
| cm-deepsight | 9920 | DS v4-pro | 深度研究 |
| do-ops | 9910 | DS v4-pro | 运维/SRE |
| if-explorer | 9930 | DS v4-pro | 技术可行性 |
| do-developer | 9912 | kimi-k2.7 | 编码实现 |

## 部署

需要 [Hermes Agent](https://github.com/NousResearch/hermes-agent) + [lark-cli](https://github.com/nousresearch/lark-cli)。

详见各 Profile 目录下的 SOUL.md 和 config.yaml.template。
