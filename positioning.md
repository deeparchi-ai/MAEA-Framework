# MAEA 定位

> 一句话：**StaffDeck 管一个 Agent 怎么干活，PPIO 管 Agent 跑在哪，MAEA 管一群 Agent 怎么不乱。**

---

## 问题分层

企业用 Agent 不是问题——**用一群 Agent 协作才是问题**。

| 层 | 问题 | 现有方案 | 例子 |
|---|------|---------|------|
| 单 Agent 行为 | 这个 Agent 怎么干活？ | Agent 编排/工作流引擎 | **StaffDeck**（任务编排、工具调用、流程设计） |
| Agent 基础设施 | Agent 跑在哪？ | Agent 托管/部署平台 | **PPIO**（GPU 算力、模型部署、推理服务） |
| 多 Agent 治理 | 一群 Agent 怎么不乱？ | ❌ 空白 | **MAEA**（域隔离、拓扑校验、安全基因、经济模型） |

---

## 为什么需要 MAEA

单 Agent 的编排问题 StaffDeck 已经解决。Agent 的部署问题 PPIO 已经解决。但当你有 5 个、10 个、50 个 Agent 同时工作时：

1. **谁批准新 Agent 入网？** —— MAEA 有入网审查 + 四名合一校验
2. **跨域调用谁审计？** —— MAEA 有 bridge-bootstrap + 委托链追溯
3. **循环依赖怎么检测？** —— MAEA 有 DAG 拓扑校验（BFS，零漏检）
4. **安全事故爆炸半径多大？** —— MAEA 有域隔离 + 安全基因六条铁律
5. **预算超了谁来刹车？** —— MAEA 有 Token 预算 + 超额熔断
6. **Agent 间能力冲突谁裁决？** —— MAEA 有注册表 + 冲突检测

这些不是单 Agent 工作流的问题。是**组织治理**的问题。

---

## 关系

```
StaffDeck ──→ 管好一个 Agent 的行为
PPIO     ──→ 管好 Agent 的算力和部署
MAEA     ──→ 管好一群 Agent 的组织
             ↑
         MAEA Agent 可以跑在 PPIO 上
         MAEA Agent 可以调用 StaffDeck 编排好的工具
         三者互补，不竞争
```

---

## MAEA 不是

- ❌ 不是 Agent 编排/工作流引擎（那是 StaffDeck 的活）
- ❌ 不是 Agent 托管/算力平台（那是 PPIO 的活）
- ❌ 不是 Agent 框架（LangChain、CrewAI 那层）
- ✅ 是企业架构在 Agent 时代的应用——用管理人的方法管理 Agent

---

## 一句话

**StaffDeck 解决 Agent 怎么干活。PPIO 解决 Agent 跑在哪。MAEA 解决一群 Agent 怎么不乱。**
