# 架构吸收台账（Adoption Register）

> MAEA 是框架：外部成熟架构成果**来者不拒**，但每一条吸收都必须留痕——从哪来、吸收了什么、落在哪个文件、实现到什么程度。
> 实现侧（MACS）是否采纳，由 [MACS decisions/](https://github.com/deeparchi-ai/macs/tree/main/decisions) 的 ADR 独立评估，**不与框架吸收捆绑**。

---

## 台账

| 编号 | 来源 | 吸收内容 | 落点 | 实现状态 |
|:----:|------|---------|------|---------|
| [A-001](A-001-ibm-zos-subsystems.md) | IBM z/OS 子系统族 | 15 个治理机制映射（WLM/RACF/CICS/SMF/JES2/DFSMS/VTAM/RMF/ICSF/XCF/ARM/Health Checker/TSO-ISPF/隔离层/存储键） | `specs/macs-governance-spec.md` §2–§15 + Appendix A | 部分实现（WLM → [wlm](https://github.com/deeparchi-ai/wlm)，其余设计完成/待实现） |
| [A-002](A-002-togaf.md) | TOGAF 10 / ADM | ADM 八阶段→Agent 职责映射、架构治理、交付物规范 | `docs/zh/maea-whitepaper.md` 理论基础章 | 文档级（无代码实现需求） |
| [A-003](A-003-ai-native-org-research.md) | Accenture 2025 重组 / OpenAI / Anthropic / Sierra | 五域架构设计依据（无独立运维部、行业知识由数据承载等） | `docs/zh/maea-whitepaper.md` 五域章 | 已落地（本仓 Agent 拓扑即五域） |
| [A-004](A-004-a2a-mcp-protocols.md) | Google A2A（LF AAIF）/ Anthropic MCP | Agent Card、Task、JSON/HTTP 概念对齐；MCP 作为工具层 | `specs/a2a-protocol.md` §8.1、`specs/mcp-integration.md` | 已实现（Hermes 运行时 + 27 Agent 在跑） |

## 候选（尚未吸收，等评估）

| 来源 | 潜在吸收点 | 状态 |
|------|-----------|------|
| Palantir Foundry / AIP | 本体（Ontology）驱动的 Agent 权限与资源隔离模型 | 待评估（未写入任何 spec） |
| IT4IT 2.1 | 四价值流与 Agent 交付管线的映射 | 待评估 |
| BIAN | 银行业务能力映射（仅咨询交付场景，非框架本体） | 待评估 |

> 规则：候选表里的条目不等于已吸收。**未写入 docs/specs 的，一律不算吸收。**

---

## 状态定义

| 状态 | 含义 |
|------|------|
| 已吸收·已实现 | 有 spec + 有可运行代码/在产 Agent |
| 已吸收·部分实现 | 有 spec，部分组件落地 |
| 已吸收·纯文档 | 方法论映射，无需代码 |
| 候选待评估 | 知道有用，未写入框架 |
| 主动舍弃 | 评估后决定不吸收，**必须写清原因** |

## 联动

```
外部成果 → ① MAEA 吸收（本台账 + docs/specs 落地）
              ↓
           ② sg-architect 评估 MACS 是否采纳（MACS/decisions/ADR-NNN）
              ↓
           ③ 采纳 → 实现 ｜ 延后 → MACS DESIGN.md Roadmap ｜ 不采纳 → ADR 记原因
```

新增条目：复制 [ADOPTION-TEMPLATE.md](ADOPTION-TEMPLATE.md)，编号顺延。
