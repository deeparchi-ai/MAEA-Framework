"""MAEA Minimal Demo — four phases, three agents, zero dependencies.

Run:  python3 demo.py

Phase 1 — Network: start registry + three A2A agents.
Phase 2 — Onboarding: register every agent and run onboarding review.
Phase 3 — Delegation: sg-architect routes a research task to cm-deepsight,
           then delegates implementation to do-developer.
Phase 4 — Shutdown: stop all servers and print a summary.
"""

from __future__ import annotations

import json
import time
from typing import Any, Dict, List

from agents import CMDeepSight, DODeveloper, SGArchitect
from protocol import Task, fetch_agent_card, send_task
from registry import Registry, register_with_registry


def banner(title: str) -> None:
    print(f"\n{'=' * 56}")
    print(f"  {title}")
    print(f"{'=' * 56}")


def print_json(label: str, payload: Any) -> None:
    print(f"\n📋 {label}")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def phase_1_network() -> Dict[str, Any]:
    banner("Phase 1: 启动 A2A 网络")

    registry = Registry()
    architect = SGArchitect()
    researcher = CMDeepSight()
    developer = DODeveloper()

    registry.start()
    architect.start()
    researcher.start()
    developer.start()

    # Give the threads a moment to fully listen.
    time.sleep(0.2)

    agents = {
        "registry": registry,
        "sg-architect": architect,
        "cm-deepsight": researcher,
        "do-developer": developer,
    }

    for name, agent in agents.items():
        print(f"  ✅ {name:15} listening on {agent.url}")

    return agents


def phase_2_onboarding(agents: Dict[str, Any]) -> Dict[str, Any]:
    banner("Phase 2: 入网审查")

    registry_url = agents["registry"].url
    onboarding_results: Dict[str, Any] = {}

    # Define intended call topology (DAG): architect -> researcher -> developer.
    edges = [
        ("sg-architect", "cm-deepsight"),
        ("cm-deepsight", "do-developer"),
    ]

    for name in ["sg-architect", "cm-deepsight", "do-developer"]:
        agent = agents[name]
        approved, details = register_with_registry(
            registry_url,
            agent,
            declared_edges=[e for e in edges if e[0] == name],
        )
        onboarding_results[name] = {"approved": approved, "details": details}
        status = "✅ approved" if approved else "❌ rejected"
        print(f"  {status:14} {name}")

    # List registered agents via A2A.
    list_task = Task(
        id="list-agents",
        skill="list_agents",
        prompt="List all registered agents",
        context_id="demo",
    )
    list_result = send_task(registry_url, list_task)
    print_json("注册表快照", list_result.output)

    return onboarding_results


def phase_3_delegation(agents: Dict[str, Any]) -> Dict[str, Any]:
    banner("Phase 3: 任务委托链")

    architect = agents["sg-architect"]
    researcher = agents["cm-deepsight"]
    developer = agents["do-developer"]

    # Step A: architect asks researcher for deep research.
    research_result = architect.delegate_to(
        researcher.url,
        skill="deep_research",
        prompt="分析为什么 AI Agent 团队需要治理框架",
        context_id="demo-delegation-001",
        confidence=0.9,
    )
    print_json("cm-deepsight 研究结果", research_result.output)

    # Step B: architect asks developer for a quick implementation.
    impl_result = architect.delegate_to(
        developer.url,
        skill="quick_impl",
        prompt="实现一个最小 MAEA Agent 注册表 CLI",
        context_id="demo-delegation-001",
        confidence=0.85,
        metadata={"language": "python"},
    )
    print_json("do-developer 实现结果", impl_result.output)

    # Step C: direct security assessment from researcher.
    assess_result = send_task(
        researcher.url,
        Task(
            id="risk-assess",
            skill="threat_assess",
            prompt="评估上述任务链的安全风险",
            context_id="demo-delegation-001",
        ),
    )
    print_json("cm-deepsight 风险评估", assess_result.output)

    # Step D: verify we can fetch each Agent Card directly.
    cards = {}
    for name in ["sg-architect", "cm-deepsight", "do-developer"]:
        agent_url = agents[name].url
        cards[name] = fetch_agent_card(agent_url).to_dict()
    print_json("Agent Card 发现", cards)

    return {
        "research": research_result.to_dict(),
        "implementation": impl_result.to_dict(),
        "assessment": assess_result.to_dict(),
        "cards": cards,
    }


def phase_4_shutdown(agents: Dict[str, Any]) -> None:
    banner("Phase 4: 关闭网络")

    for name, agent in agents.items():
        agent.stop()
        print(f"  🔴 {name:15} stopped")


def main() -> None:
    print("🏛️  MAEA Framework — Minimal A2A Demo")
    print("   python3 demo.py | 4 phases | 3 agents | stdlib only")

    agents = phase_1_network()
    onboarding = phase_2_onboarding(agents)
    delegation = phase_3_delegation(agents)
    phase_4_shutdown(agents)

    banner("Demo 完成")
    summary = {
        "network": {name: agent.url for name, agent in agents.items()},
        "onboarding_approved": all(
            r["approved"] for r in onboarding.values()
        ),
        "delegation_steps": len(delegation),
    }
    print_json("总结", summary)


if __name__ == "__main__":
    main()
