# MAEA Minimal A2A Demo

3 分钟上手 MAEA 多 Agent 企业架构框架的最小可运行示例。

## 特点

- **纯标准库** — 无需 `pip install`，只需 Python 3.9+
- **一键运行** — `python3 demo.py`
- **4 个 Phase** — 网络启动 → 入网审查 → 任务委托 → 关闭清理
- **3 个 Agent** — `sg-architect` 、`cm-deepsight` 、`do-developer`

## 目录

```
demo/
├── protocol.py      # A2A HTTP 服务器：Agent Card + /tasks
├── agents.py        # 3 个 Agent 类
├── registry.py      # 注册表 + 入网审查
├── demo.py          # 主脚本：4 Phase 串联
├── README.md        # 本文档
└── project.yaml     # Sprint 1 元数据
```

## 快速开始

```bash
cd demo
python3 demo.py
```

示例输出：

```
🏛️  MAEA Framework — Minimal A2A Demo
   python3 demo.py | 4 phases | 3 agents | stdlib only

========================================================
  Phase 1: 启动 A2A 网络
========================================================
  ✅ registry        listening on http://127.0.0.1:9903
  ✅ sg-architect     listening on http://127.0.0.1:9900
  ✅ cm-deepsight     listening on http://127.0.0.1:9901
  ✅ do-developer      listening on http://127.0.0.1:9902

...
```

## 协议端点

### Agent Card 发现

```bash
curl http://127.0.0.1:9996/.well-known/agent.json
```

### 任务委托

```bash
curl -X POST http://127.0.0.1:9996/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "id": "t1",
    "skill": "route_task",
    "prompt": "请进行研究并实现",
    "context_id": "demo-001",
    "metadata": {
      "target_url": "http://127.0.0.1:9997",
      "sub_skill": "deep_research"
    }
  }'
```

## 4 个 Phase 详解

| Phase | 动作 | 说明 |
|------|------|------|
| 1 | 启动 Registry + 3 Agents | 每个 Agent 在独立线程启动 HTTP 服务 |
| 2 | 入网审查 | 注册 Agent 并执行 DAG/能力/安全/身份校验 |
| 3 | 任务委托链 | sg-architect → cm-deepsight → do-developer |
| 4 | 关闭网络 | 顺序停止各 Agent 服务器 |

## Agent 角色

| Agent | 层级 | 主要技能 |
|-------|------|----------|
| `sg-architect` | 战略层 (L1) | 架构评审、任务路由、DAG 校验 |
| `cm-deepsight` | 研究层 (L3) | 深度研究、反方论证、风险评估 |
| `do-developer` | 交付层 (L2) | 快速实现、Bug 修复、API 对接 |

## 入网审查

`registry.py` 实现了 MAEA 安全模型中的 4 步审查：

1. **拓扑校验** — 检测 A2A 调用关系是否形成有向无环图 (DAG)
2. **能力冲突检测** — 识别与已有 Agent 的技能重叠
3. **安全边界验证** — 确保 L1 Agent 不声明高风险外部技能
4. **身份验证** — name / url / skill / profile 四名合一

## 扩展

- 在 `agents.py` 中添加新的 `Agent` 子类
- 在 `registry.py` 中增加更严格的审查规则
- 在 `demo.py` 中调整 Phase 和委托链

## 约束

- Python 3.9+
- 仅使用标准库 (`http.server`, `urllib`, `threading`, `dataclasses` 等)
