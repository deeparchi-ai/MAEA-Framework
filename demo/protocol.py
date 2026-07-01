"""MAEA Minimal A2A Protocol — HTTP/JSON Agent-to-Agent communication.

Pure stdlib implementation of the A2A protocol used by MAEA.
- GET /.well-known/agent.json  -> Agent Card discovery
- POST /tasks                  -> synchronous task delegation

All payloads are JSON. No external dependencies.
"""

from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Callable, Dict, List, Optional


PROTOCOL_VERSION = "0.3"


@dataclass
class Skill:
    id: str
    name: str


@dataclass
class AgentCard:
    """Discovery metadata exposed by every A2A agent."""

    name: str
    description: str
    url: str
    protocolVersion: str = PROTOCOL_VERSION
    capabilities: Dict[str, bool] = field(default_factory=lambda: {
        "streaming": False,
        "pushNotifications": False,
    })
    skills: List[Skill] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        return data


@dataclass
class Task:
    """A2A task message."""

    id: str
    skill: str
    prompt: str
    context_id: str
    confidence: float = 1.0
    human_review_required: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        return cls(**data)


@dataclass
class TaskResult:
    """Result returned by an A2A task handler."""

    task_id: str
    status: str  # "success" | "pending" | "error"
    output: Dict[str, Any] = field(default_factory=dict)
    artifacts: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class A2ARequestHandler(BaseHTTPRequestHandler):
    """HTTP handler routing A2A endpoints."""

    server_ready: threading.Event

    def _agent_card(self) -> AgentCard:
        return self.server.agent_card  # type: ignore[attr-defined]

    def _task_handler(self) -> Callable[[Task], TaskResult]:
        return self.server.task_handler  # type: ignore[attr-defined]

    def _send_json(self, status: int, payload: Any) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> Optional[Dict[str, Any]]:
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return None
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/.well-known/agent.json":
            self._send_json(200, self._agent_card().to_dict())
            return
        self._send_json(404, {"error": "not_found", "path": self.path})

    def do_POST(self) -> None:  # noqa: N802
        if self.path == "/tasks":
            data = self._read_json()
            if data is None:
                self._send_json(400, {"error": "invalid_json"})
                return
            try:
                task = Task.from_dict(data)
                result = self._task_handler()(task)
                self._send_json(200, result.to_dict())
            except Exception as exc:  # noqa: BLE001
                self._send_json(500, {
                    "error": "handler_error",
                    "detail": str(exc),
                })
            return
        self._send_json(404, {"error": "not_found", "path": self.path})

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        # Suppress default access logs to keep demo output clean.
        pass


class A2AServer:
    """Lightweight A2A HTTP server running in a background thread."""

    def __init__(
        self,
        agent_card: AgentCard,
        task_handler: Callable[[Task], TaskResult],
        host: str = "127.0.0.1",
        port: int = 0,
    ) -> None:
        self.agent_card = agent_card
        self.task_handler = task_handler
        self.host = host
        self.port = port
        self._server: Optional[HTTPServer] = None
        self._thread: Optional[threading.Thread] = None
        self.ready = threading.Event()

    def start(self) -> int:
        A2ARequestHandler.server_ready = self.ready

        try:
            self._server = HTTPServer((self.host, self.port), A2ARequestHandler)
        except OSError:
            # Preferred port is in use; let the OS pick an available one.
            self._server = HTTPServer((self.host, 0), A2ARequestHandler)

        # Attach per-server state so each handler sees its own agent card/handler.
        self._server.agent_card = self.agent_card  # type: ignore[attr-defined]
        self._server.task_handler = self.task_handler  # type: ignore[attr-defined]

        actual_port = self._server.server_address[1]
        self.port = actual_port
        self.agent_card.url = f"http://{self.host}:{actual_port}"

        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        self.ready.wait(timeout=5.0)
        return actual_port

    def _run(self) -> None:
        self.ready.set()
        self._server.serve_forever()  # type: ignore[union-attr]

    def stop(self) -> None:
        if self._server:
            self._server.shutdown()
            self._server.server_close()
        if self._thread:
            self._thread.join(timeout=5.0)


def fetch_agent_card(url: str, timeout: float = 5.0) -> AgentCard:
    """Discover another agent's Agent Card."""
    request = urllib.request.Request(
        f"{url}/.well-known/agent.json",
        method="GET",
        headers={"Accept": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = json.loads(response.read().decode("utf-8"))
        skills = [Skill(**s) for s in data.get("skills", [])]
        return AgentCard(
            name=data["name"],
            description=data["description"],
            url=data["url"],
            protocolVersion=data.get("protocolVersion", PROTOCOL_VERSION),
            capabilities=data.get("capabilities", {}),
            skills=skills,
        )


def send_task(url: str, task: Task, timeout: float = 10.0) -> TaskResult:
    """POST a task to another A2A agent."""
    body = json.dumps(task.to_dict(), ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        f"{url}/tasks",
        method="POST",
        data=body,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
            return TaskResult(**data)
    except urllib.error.HTTPError as exc:
        return TaskResult(
            task_id=task.id,
            status="error",
            output={"detail": exc.read().decode("utf-8", errors="ignore")},
        )
