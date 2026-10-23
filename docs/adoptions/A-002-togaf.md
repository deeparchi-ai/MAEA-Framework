# A-002: TOGAF 10 / ADM

**状态**：已吸收·纯文档  
**日期**：2026-07-18（台账建档）  
**来源类型**：标准框架（The Open Group）  
**权威出处**：TOGAF 10 — Architecture Development Method (ADM)

---

## 吸收了什么

| 来源机制 | MAEA 对应 | 说明 |
|---------|-----------|------|
| ADM 八阶段 | Agent 职责划分 | 架构需求 → 能力映射 → 交付物，落在五域 Agent 的职责边界 |
| 架构治理（Architecture Governance） | sg-architect 治理域 | 入网审查、架构评审、冲突仲裁 |
| 交付物规范 | Agent 交付物验收标准 | 每类 Agent 的输出格式与验收项 |

## 落点

- `docs/zh/maea-whitepaper.md`（及 `docs/MAEA-whitepaper-zh.md`、`docs/zh/chapters/八理论基础.md`）"TOGAF 映射"节

## 主动舍弃 / 未吸收

| 来源机制 | 为什么不吸收 |
|---------|-------------|
| ADM 阶段门禁（Phase Gate 人工评审） | AI 原生组织用自动化治理审计替代阶段性人工评审 |
| 架构能力成熟度模型（ACMM，已废弃） | TOGAF 10 已移除，不引入 |
| 组织级架构能力分级 | 3–5 人 AI 原生组织不存在分层架构团队 |

## 实现评估

| 实现 | 状态 | 记录 |
|------|------|------|
| MACS | 无需采纳（方法论映射，无代码） | — |

## 备注

TOGAF 是**映射关系**而非架构来源：MAEA 的五域不是从 TOGAF 推出来的，是研究四家 AI 企业后得出，再与 TOGAF 做对照。此区分不可在对外材料中混淆。
