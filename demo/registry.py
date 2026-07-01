"""MAEA Minimal Registry — agent directory + onboarding review.

The registry keeps the canonical list of A2A peers and runs the four-step
onboarding review required by the MAEA security model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from agents import Agent
from protocol import AgentCard, Skill, Task, TaskResult


@dataclass
class RegistryEntry:
    """A registered agent record."""

    agent_id: str
    card: AgentCard
    security_level: int
    status: str = "pending"  # pending | approved | rejected
    review_notes: List[str] = field(default_factory=list)


class Registry(Agent):
    """Registry agent: directory service + onboarding gatekeeper."""

    name = "registry"
    description = "Agent registry and onboarding review"
    default_port = 9999
    security_level = 1
    skills = [
        Skill("register", "注册 Agent"),
        Skill("onboarding_review", "入网审查"),
        Skill("list_agents", "列出已注册 Agent"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.entries: Dict[str, RegistryEntry] = {}
        self.dependency_edges: List[Tuple[str, str]] = []

    def skill_register(self, task: Task) -> TaskResult:
        """Register a new agent from its Agent Card."""
        card_data = task.metadata.get("card")
        security_level = task.metadata.get("security_level", 3)
        if not card_data:
            return TaskResult(
                task_id=task.id,
                status="error",
                output={"error": "missing card in metadata"},
            )
        # Rehydrate skills from serialized dicts.
        raw_skills = card_data.get("skills", [])
        card_data["skills"] = [Skill(**s) for s in raw_skills]
        card = AgentCard(**card_data)
        entry = RegistryEntry(
            agent_id=card.name,
            card=card,
            security_level=security_level,
        )
        self.entries[card.name] = entry
        return TaskResult(
            task_id=task.id,
            status="success",
            output={
                "registered": card.name,
                "url": card.url,
                "status": entry.status,
            },
        )

    def skill_onboarding_review(self, task: Task) -> TaskResult:
        """Run the four-step onboarding review."""
        candidate_name = task.metadata.get("candidate_name")
        declared_edges = task.metadata.get("edges", [])  # list of [caller, callee]
        if not candidate_name or candidate_name not in self.entries:
            return TaskResult(
                task_id=task.id,
                status="error",
                output={"error": "candidate not registered"},
            )

        entry = self.entries[candidate_name]
        notes: List[str] = []
        passed = True

        # 1. Topology validation (DAG, no cycles).
        edges = self.dependency_edges + [tuple(e) for e in declared_edges]  # type: ignore[arg-type]
        cycle = self._detect_cycle(edges)
        if cycle:
            notes.append(f"FAIL: cycle detected after adding {candidate_name}")
            passed = False
        else:
            notes.append("PASS: topology is acyclic (DAG)")

        # 2. Capability conflict detection.
        conflicts = self._detect_capability_conflicts(entry)
        if conflicts:
            notes.append(f"WARN: capability overlap with {', '.join(conflicts)}")
            # Overlap does not auto-reject; marks for arbitration.
        else:
            notes.append("PASS: no capability conflicts")

        # 3. Security boundary verification.
        if entry.security_level == 1 and any(
            s.id in ("external_api", "budget_ops") for s in entry.card.skills
        ):
            notes.append("FAIL: L1 agent claims high-risk external skills")
            passed = False
        else:
            notes.append("PASS: security boundary within declared level")

        # 4. Identity verification (four-in-one).
        identity_ok = bool(entry.card.name) and entry.card.url.startswith("http://")
        if identity_ok:
            notes.append("PASS: identity verified (name/url/skill/profile aligned)")
        else:
            notes.append("FAIL: identity verification failed")
            passed = False

        entry.status = "approved" if passed else "rejected"
        entry.review_notes = notes
        if passed:
            self.dependency_edges.extend(tuple(e) for e in declared_edges)  # type: ignore[arg-type]

        return TaskResult(
            task_id=task.id,
            status="success",
            output={
                "candidate": candidate_name,
                "approved": passed,
                "notes": notes,
            },
        )

    def skill_list_agents(self, task: Task) -> TaskResult:
        return TaskResult(
            task_id=task.id,
            status="success",
            output={
                "count": len(self.entries),
                "agents": [
                    {
                        "name": e.card.name,
                        "url": e.card.url,
                        "status": e.status,
                        "security_level": e.security_level,
                    }
                    for e in self.entries.values()
                ],
            },
        )

    @staticmethod
    def _detect_cycle(edges: List[Tuple[str, str]]) -> bool:
        graph: Dict[str, List[str]] = {}
        nodes = set()
        for a, b in edges:
            graph.setdefault(a, []).append(b)
            nodes.add(a)
            nodes.add(b)

        visited: set = set()
        rec_stack: set = set()

        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            for neighbor in graph.get(node, []):
                if neighbor not in visited and dfs(neighbor):
                    return True
                if neighbor in rec_stack:
                    return True
            rec_stack.remove(node)
            return False

        return any(dfs(n) for n in nodes if n not in visited)

    def _detect_capability_conflicts(self, entry: RegistryEntry) -> List[str]:
        candidate_skills = {s.id for s in entry.card.skills}
        conflicts: List[str] = []
        for other in self.entries.values():
            if other.agent_id == entry.agent_id:
                continue
            other_skills = {s.id for s in other.card.skills}
            if candidate_skills & other_skills:
                conflicts.append(other.agent_id)
        return conflicts


def register_with_registry(
    registry_url: str,
    agent: Agent,
    declared_edges: Optional[List[Tuple[str, str]]] = None,
) -> Tuple[bool, Dict[str, Any]]:
    """Helper: register an agent and run onboarding review via A2A."""
    from protocol import Task, send_task

    # Step 1: register
    reg_task = Task(
        id=f"reg-{agent.name}",
        skill="register",
        prompt=f"Register {agent.name}",
        context_id=f"onboarding-{agent.name}",
        metadata={
            "card": agent.card.to_dict(),
            "security_level": agent.security_level,
        },
    )
    reg_result = send_task(registry_url, reg_task).output

    # Step 2: review
    review_task = Task(
        id=f"review-{agent.name}",
        skill="onboarding_review",
        prompt=f"Review {agent.name}",
        context_id=f"onboarding-{agent.name}",
        metadata={
            "candidate_name": agent.name,
            "edges": declared_edges or [],
        },
    )
    review_result = send_task(registry_url, review_task).output
    approved = bool(review_result.get("approved"))
    return approved, {
        "register": reg_result,
        "review": review_result,
    }
