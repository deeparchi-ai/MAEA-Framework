"""MAEA Minimal Agents — three reference Agent implementations.

Each agent is an A2A peer that can receive tasks and optionally delegate
sub-tasks to other agents. All behavior is deterministic simulation, suitable
for a zero-dependency demo.
"""

from __future__ import annotations

import uuid
from abc import ABC
from typing import Any, Dict, List, Optional

from protocol import AgentCard, Skill, Task, TaskResult, A2AServer, send_task


class Agent(ABC):
    """Base class for an A2A-capable MAEA agent."""

    name: str = "base-agent"
    description: str = ""
    port: int = 0
    security_level: int = 3  # L1=1 (highest), L3=3 (standard)
    skills: List[Skill] = []
    default_port: int = 0

    def __init__(self) -> None:
        self.agent_id = str(uuid.uuid4())[:8]
        self.card = AgentCard(
            name=self.name,
            description=self.description,
            url="",  # populated by server start
            skills=self.skills,
        )
        self.server = A2AServer(
            agent_card=self.card,
            task_handler=self.handle_task,
            port=self.default_port,
        )
        self.audit_log: List[Dict[str, Any]] = []

    def start(self) -> int:
        port = self.server.start()
        return port

    def stop(self) -> None:
        self.server.stop()

    @property
    def url(self) -> str:
        return self.card.url

    def handle_task(self, task: Task) -> TaskResult:
        """Dispatch incoming tasks by skill id."""
        if task.skill == "ping":
            return TaskResult(
                task_id=task.id,
                status="success",
                output={"message": f"{self.name} is alive"},
            )

        handler = getattr(self, f"skill_{task.skill}", None)
        if handler is None:
            return TaskResult(
                task_id=task.id,
                status="error",
                output={"error": f"skill '{task.skill}' not supported by {self.name}"},
            )
        return handler(task)

    def delegate_to(
        self,
        target_url: str,
        skill: str,
        prompt: str,
        context_id: str,
        confidence: float = 1.0,
        human_review_required: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> TaskResult:
        """Send a sub-task to another A2A agent."""
        task = Task(
            id=f"{self.name}-{uuid.uuid4().hex[:6]}",
            skill=skill,
            prompt=prompt,
            context_id=context_id,
            confidence=confidence,
            human_review_required=human_review_required,
            metadata=metadata or {},
        )
        return send_task(target_url, task)

    def audit(self, event: str, detail: Dict[str, Any]) -> None:
        self.audit_log.append({"event": event, "detail": detail})


class SGArchitect(Agent):
    """Strategic layer: architecture governance + routing hub."""

    name = "sg-architect"
    description = "Architecture governance and routing hub"
    default_port = 9996
    security_level = 1  # L1
    skills = [
        Skill("architecture_review", "架构评审"),
        Skill("registry_maintenance", "注册表维护"),
        Skill("route_task", "任务路由"),
        Skill("dag_validate", "DAG 拓扑校验"),
    ]

    def skill_route_task(self, task: Task) -> TaskResult:
        # Demo routing: parse target agent from metadata.
        target = task.metadata.get("target_url")
        if not target:
            return TaskResult(
                task_id=task.id,
                status="error",
                output={"error": "missing target_url in metadata"},
            )
        sub_skill = task.metadata.get("sub_skill", "ping")
        sub_prompt = task.metadata.get("sub_prompt", task.prompt)
        result = self.delegate_to(
            target,
            sub_skill,
            sub_prompt,
            task.context_id,
            confidence=task.confidence,
            human_review_required=task.human_review_required,
        )
        return TaskResult(
            task_id=task.id,
            status=result.status,
            output={
                "routed_by": self.name,
                "target": target,
                "sub_result": result.to_dict(),
            },
        )

    def skill_architecture_review(self, task: Task) -> TaskResult:
        self.audit("architecture_review", {"context_id": task.context_id})
        return TaskResult(
            task_id=task.id,
            status="success",
            output={
                "reviewer": self.name,
                "verdict": "approved",
                "notes": [
                    "担保结构符合 MAEA 五层治理模型",
                    "A2A 拓扑无循环依赖",
                ],
            },
        )

    def skill_dag_validate(self, task: Task) -> TaskResult:
        edges = task.metadata.get("edges", [])
        visited = set()
        rec_stack = set()
        graph: Dict[str, List[str]] = {}
        for a, b in edges:
            graph.setdefault(a, []).append(b)

        def has_cycle(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            for neighbor in graph.get(node, []):
                if neighbor not in visited and has_cycle(neighbor):
                    return True
                if neighbor in rec_stack:
                    return True
            rec_stack.remove(node)
            return False

        cycle = any(has_cycle(n) for n in graph if n not in visited)
        return TaskResult(
            task_id=task.id,
            status="success",
            output={"cycle_detected": cycle, "edge_count": len(edges)},
        )

    def skill_registry_maintenance(self, task: Task) -> TaskResult:
        return TaskResult(
            task_id=task.id,
            status="success",
            output={"maintainer": self.name, "action": "registry_synced"},
        )


class CMDeepSight(Agent):
    """Research layer: deep reasoning + devil's advocate."""

    name = "cm-deepsight"
    description = "Deep research and cross-validation"
    default_port = 9997
    security_level = 3  # L3
    skills = [
        Skill("deep_research", "深度研究"),
        Skill("devils_advocate", "反方论证"),
        Skill("threat_assess", "风险评估"),
    ]

    def skill_deep_research(self, task: Task) -> TaskResult:
        return TaskResult(
            task_id=task.id,
            status="success",
            output={
                "researcher": self.name,
                "topic": task.prompt,
                "findings": [
                    "市场上存在 12.3 万星标的 AI Agent 集合",
                    "用户痛点不是缺 Agent，而是缺少治理",
                ],
                "confidence": task.confidence,
            },
        )

    def skill_devils_advocate(self, task: Task) -> TaskResult:
        return TaskResult(
            task_id=task.id,
            status="success",
            output={
                "reviewer": self.name,
                "role": "devils_advocate",
                "concerns": [
                    "多 Agent 协议之间的责任边界是否清晰？",
                    "入网审查是否能处理能力冲突？",
                ],
            },
        )

    def skill_threat_assess(self, task: Task) -> TaskResult:
        return TaskResult(
            task_id=task.id,
            status="success",
            output={
                "assessor": self.name,
                "risk_level": "medium",
                "mitigations": [
                    "启用最小权限模型",
                    "人工审查所有 L1/L2 决策",
                ],
            },
        )


class DODeveloper(Agent):
    """Delivery layer: coding implementation and quick fixes."""

    name = "do-developer"
    description = "Coding implementation and operations"
    default_port = 9998
    security_level = 2  # L2
    skills = [
        Skill("quick_impl", "快速实现"),
        Skill("bug_fix", "Bug 修复"),
        Skill("api_integration", "API 对接"),
    ]

    def skill_quick_impl(self, task: Task) -> TaskResult:
        # Simulate writing code based on prompt.
        artifact = {
            "filename": "generated_module.py",
            "content": f"# Generated by {self.name}\n# Task: {task.prompt}\nprint('hello maea')\n",
            "language": "python",
        }
        return TaskResult(
            task_id=task.id,
            status="success",
            output={
                "implementer": self.name,
                "summary": f"已根据需求完成快速实现: {task.prompt}",
                "lines_of_code": 3,
            },
            artifacts=[artifact],
        )

    def skill_bug_fix(self, task: Task) -> TaskResult:
        return TaskResult(
            task_id=task.id,
            status="success",
            output={
                "fixer": self.name,
                "issue": task.prompt,
                "patch": "- old\n+ fixed",
                "regression_tests": ["test_demo.py"],
            },
        )

    def skill_api_integration(self, task: Task) -> TaskResult:
        return TaskResult(
            task_id=task.id,
            status="success",
            output={
                "integrator": self.name,
                "endpoint": task.metadata.get("endpoint", "http://example.com/api"),
                "status": "connected",
            },
        )
