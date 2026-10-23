# A-001: IBM z/OS 子系统族

**状态**：已吸收·已实现  
**日期**：2026-07-18（台账建档）/ 吸收工作 2026-07 至 2026-08  
**来源类型**：厂商架构（运行了 60 年的生产系统治理机制）  
**权威出处**：IBM z/OS 文档族（WLM / RACF / CICS / SMF / JES2 / SDSF / DFSMS / VTAM / RMF / NetView / ICSF / XCF / ARM / Health Checker / TSO / ISPF / PR-SM / z-VM）

---

## 吸收了什么

| 来源机制 | MAEA / MACS 对应 | 继承 | Agent 原生新增 |
|---------|-----------------|------|---------------|
| BCP（Dispatcher/SVC/SRB/Lock Manager） | Kernel | 工作单元派发、系统调用闸、异步调度、并发控制 | 统一准入、熔断、审计钩子注册、W3C traceparent、Agent 上下文锁 |
| WLM | §2 Regulator | 目标仲裁、重要性分级 | Token 预算 + 模型故障切换 |
| RACF | §3 Sanctum | L1/L2/L3 访问级、跨级规则 | 行为信任评分、漂移检测 |
| CICS Syncpoint | §3b Loom | 两阶段提交、工作单元 | 因果 DAG 污染检测、分叉点重放 |
| SMF | §4 Chronicle | 不可变记录、统一审计面 | W3C traceparent、跨协议桥 |
| JES2 + SDSF | §6 Cadence | 优先级队列、initiator 管理 | 结果投递飞书、作业输出查询 |
| DFSMS + dss | §7 Curator | 生命周期策略、分层存储、备份恢复 | 知识工件语义（置信度、superseded_by） |
| VTAM | §8 Nexus | 协议准入、多传输路由 | A2A/MCP/飞书共存、LU Name |
| RMF + NetView | §9 Gauge | 性能指标、网络监控 | 跨厂商健康关联、模型退化检测 |
| ICSF | §10 Seal | 证书管理、密码学操作 | Agent 身份生命周期、输出签名验证 |
| XCF | §11 Relay | 集群成员、共享状态、广播 | Agent 间事件 pub/sub、状态收敛 |
| ARM + System Automation | §12 Warden | 崩溃恢复、策略化运维 | 模型故障升级、人在环策略 |
| z/OS Health Checker | §13 Pulse | 子系统健康检查、启动校验 | 依赖感知健康传播、看门狗 |
| TSO + ISPF | §14 Console | 交互命令环境、全屏面板 | 三模式（Interactive/Headless/Embedded）、飞书+CLI+MCP 统一控制面 |
| LPAR / z/VM / 地址空间 + 存储键 | §15 隔离边界声明 | 部署层隔离语义（非内核职责） | Enclave 声明、跨 Enclave 默认拒绝 |

## 落点

- `specs/macs-governance-spec.md` §2–§15、Appendix A（映射表）、Appendix B（实现状态）、Appendix C（术语）、Appendix D（数据域矩阵）
- `specs/maea-middleware.md` §1 CICS Lineage（CICS ↔ 中间件层对应）

## 主动舍弃 / 未吸收

| 来源机制 | 为什么不吸收 |
|---------|-------------|
| 存储键的硬件级隔离 | Agent 运行时是 Linux 进程/容器，无法复刻 PSW 键；以 §15 界外化为部署层职责 |
| LPAR 固件分区 | 硬件层能力，MACS 不在内核实现（v2+ 多租户时以容器/VM 承接） |
| JCL 作业控制语言 | COBOL 时代批处理脚本语法，Agent 场景由结构化 API 替代 |

## 实现评估

| 实现 | 状态 | 记录 |
|------|------|------|
| Kernel + 14 子系统 | ✅ 全部公开落地（`deeparchi-ai/macs-kernel-go` 等 14 个 `macs-*-go` 仓库） | Appendix B：单测 387 项（kernel + 14 子系统）+ POC 集成 30 项 |
| MACS Dashboard | 部分 | ADR-001 只读观测；ADR-002 A2A 自动发现 |

## 备注

- ⚠️ **待确认**：`specs/macs-governance-spec.md` Appendix B/正文称 XVal 为 **tri-model** 三方校验，而 `macs-xval-go` 仓库描述写 **dual-model**。两者需对齐（属文档口径冲突，非实现缺陷）。
- §5 XVal 与 §15 隔离层在 Appendix A 标 `(none)`，即无 IBM 血统——这是有意保留的"Agent 原生"证据。
