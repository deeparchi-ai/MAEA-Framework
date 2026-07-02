# 123,000 人收藏了一支 AI 梦之队。然后呢？

> 一个 GitHub 项目把 232 个 AI 员工装进了 Markdown 文件，拿到了 12.3 万颗星标。但没有人告诉你——这支梦之队的组织架构图，是空的。

---

## 你已经有了一支 AI 团队，但你不知道谁会干什么

[agency-agents](https://github.com/msitarzewski/agency-agents) 是 2026 年 GitHub 上最火的 AI 项目之一。12.3 万星标，2 万次 fork，232 个 AI 专家角色横跨 16 个部门——从前端工程师到小红书运营，从安全审计到游戏开发。

安装方式简单到令人窒息：

```bash
cp engineering/*.md ~/.claude/agents/
```

然后你就能在 Claude Code 里说「激活前端开发模式」，AI 就会自动切换身份。

这听起来像科幻小说的设定。Reddit 上炸了，视频号上百万播放，各路科技媒体争相报道。

**但 12.3 万个 Star 背后，藏着一个没人讨论的问题。**

---

## 打开 Issues 区，你会发现一个隐秘的事实

我把 agency-agents 的 Issues 和 Discussions 翻了一遍。票数最高的诉求，不是「加更多 Agent」，不是「支持新工具」，而是在问一些更根本的问题：

| 排名 | Issue | 👍 | 翻译成人话 |
|:---:|------|:---:|------|
| #1 | **Benchmarks?** | 17 | 「这些 Agent 到底哪个好用？」 |
| #2 | agency-orchestrator | 外部项目 | 「我不得不自己写了个编排引擎」 |
| #3 | agents-workspace | 外部项目 | 「我又写了一个工作流层」 |
| #4 | "Agent that recommends agents" | 新 Issue | 「232 个我选不过来」 |
| #5 | "I created a whole Harness" | Discussions | 「我写了一个自动选 Agent 的 Harness」 |
| #6 | "Is this repo dead?" | Q&A | 「这项目是不是没人管了？」 |

**看到了吗？**

没有人说「Agent 不够用」。所有人都在说同一件事——**Agent 太多了，但不知道怎么管。**

---

## 问题的本质：你有员工，没有组织

agency-agents 解决了「角色定义」问题。每个 Agent 都像一个写得很好的 JD（职位描述）——有身份、有工作流、有 KPI。

但它没有解决三个更根本的问题：

### 问题一：谁调谁？

232 个 Agent 之间没有任何通信机制。你只能一个一个手动激活。想让「前端工程师」和「UI 设计师」协作一个页面？你得自己来回当传话筒。

Reddit 上已经有人说：「我每次都得像 HR 一样给 AI 分配任务，累死了。」

### 问题二：怎么选？

打开 16 个部门，232 个 Agent。你要做一个 SaaS MVP，应该叫谁？

- 叫 Rapid Prototyper 还是 Frontend Developer？
- 叫 Backend Architect 还是 Software Architect？
- 要不要叫 DevOps Automator？

**选错了，浪费的是你的 API 费用和时间。**

于是有了 #634——「能不能加一个 Agent，专门推荐该用哪个 Agent？」

### 问题三：谁负责？

假设你同时激活了 5 个 Agent 做一个项目。前端改了组件库，后端改了数据库——没人发现这会导致 API 契约断裂。

这不是 Agent 不够聪明。**是没有人做架构治理。**

---

## 从 agency-agents 的热度里，能看到什么信号

12.3 万星标不是巧合。它背后是一个已经被验证的市场需求：

```
✅ 「AI 团队」概念：验证了。人们要的是分工，不是更聪明的单个 AI。
✅ 薄层设计：验证了。Markdown 文件 > 复杂框架。门槛即护城河。
✅ Prompt-as-product：验证了。好的角色定义本身就值钱。
✅ Claude Code 作为分发渠道：验证了。扔进 ~/.claude/agents/ 就能用。
```

但同时也暴露了薄层设计的上限：

```
❌ 没有编排：Agent 之间不通信
❌ 没有路由：不知道什么时候用哪个
❌ 没有治理：没有安全边界、没有冲突检测、没有版本管理
❌ 没有质量保障：没有 Benchmark、没有验证层
```

**agency-agents 画了一张完美的组织架构图，但没告诉你这张图怎么跑起来。**

---

## 从 prompt 模板到治理框架——中间缺了一层

我做了 [MAEA](https://deeparchi.ai)（多 Agent 企业架构框架），就是为了填这个坑。

它不是 agency-agents 的替代品——**它是 agency-agents 的升级路径。**

```
agency-agents → MAEA
──────────────────────────────
Agent 定义        → 保留（甚至可以直接用 agency-agents 的 prompt）
Agent 通信        → A2A 协议（Agent-to-Agent）
Agent 路由        → 意图路由 + 注册表
Agent 治理        → 入网审查 + 拓扑校验 + 安全边界
质量保障          → 双模型交叉验证 + 验证 Skill
```

具体来说，MAEA 解决了 agency-agents 用户正在自己造轮子的 5 件事：

### 1. Agent 编排（替代 #460 #494 的外部编排引擎）

不需要人来回当传话筒。Agent 之间通过 A2A 协议直接通信：

```
用户: "做竞品分析"
  └→ 架构Agent（sg-architect）路由
      ├→ 研究Agent（cm-deepsight）：市场数据、竞品技术栈
      ├→ 创新Agent（if-explorer）：技术可行性评估
      └→ 架构Agent（sg-architect）：整合 → 输出结构化报告
```

### 2. Agent 路由（替代 #634 的「Agent 推荐 Agent」）

不到 10 个 Agent 的时候不需要路由。但 232 个的时候，必须有。MAEA 的注册表（agent_registry.yaml）记录了每个 Agent 的**能力声明**和**信任等级**，架构 Agent 根据任务自动路由。

### 3. 能力冲突检测（替代「激活了 5 个 Agent 没人发现冲突」）

两个 Agent 的职责重叠了？一个 Agent 的能力声明和实际行为不一致？MAEA 在**入网审查**时就检测这些，而不是等问题爆了才发现。

### 4. 质量验证（替代 #11 的 Benchmark 诉求）

MAEA 的每个 Agent 都有**验证 Skill**——不是「我觉得这个 Agent 好用」，而是「它的输出 80% 被人类采纳」或「它的代码 PR 首次通过率 70%」。

### 5. 安全边界

哪些 Agent 能接触架构决策？哪些能接触用户数据？MAEA 的 L1-L3 安全等级定义了每条信任边界。

---

## 如果你已经有了一支 AI 梦之队

agency-agents 是一个了不起的项目。它证明了市场对一个前提的共识：**AI 协作的基本单位，正在从「问一个问题」进化成「分配一个项目」。**

但它停在了一步之遥。它给了你员工，没给你组织。

---

**接下来你可以做的事：**

**如果你只有 3-5 个 Agent** → agency-agents 就够了。手动管理完全可行。

**如果你有 5+ 个 Agent，开始感到混乱** → 你需要治理层。MAEA 的开源版提供了一个轻量的治理框架，可以接在 agency-agents 的 prompt 模板上面。

**MAEA 是开源的。如果你也有 5+ Agent 在跑，开始感到混乱——来 GitHub 一起共建 AI Agent 的治理层。**

👉 [deeparchi-ai/maea](https://github.com/deeparchi-ai/maea) · 欢迎 Issue / PR / 讨论

---

> 12.3 万人收藏了 AI 梦之队。下一个问题不是「还能加什么 Agent」，是「谁来当主管」。

---

*深度架构 · DeepArchi Team*
*2026 年 7 月*
*[deeparchi.ai](https://deeparchi.ai)*
