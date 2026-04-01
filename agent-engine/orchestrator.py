"""
GAS Agent Engine — Agent Orchestrator
Loads all domain agent configs, maintains the agent registry,
routes tasks to appropriate agents, and manages agent lifecycle.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import yaml

import config
from agent_runner import AgentRunner, AgentExecutionResult
from event_bus import EventBus
from model_router import ModelRouter
from tool_registry import ToolRegistry

logger = logging.getLogger(__name__)


# ─── Domain/Agent registry types ─────────────────────────────────────────────

class AgentStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    DISABLED = "disabled"


@dataclass
class AgentConfig:
    """Agent configuration loaded from a domain's config/agents.yaml."""
    name: str
    file: str                  # relative path to .md file within the domain directory
    md_path: str               # absolute path to .md file, resolved at load time
    domain: str
    enabled: bool
    schedule: str
    priority: int
    dependencies: list[str]
    triggers: list[dict[str, str]]


@dataclass
class AgentState:
    """Runtime state of a registered agent."""
    config: AgentConfig
    status: AgentStatus = AgentStatus.IDLE
    last_run_at: Optional[float] = None
    last_run_result: Optional[AgentExecutionResult] = None
    run_count: int = 0
    error_count: int = 0
    consecutive_errors: int = 0


@dataclass
class DomainConfig:
    """Parsed domain config from agents.yaml."""
    domain: str
    version: str
    description: str
    agents: list[AgentConfig] = field(default_factory=list)


# ─── Orchestrator ─────────────────────────────────────────────────────────────

class AgentOrchestrator:
    """
    Central orchestrator for all GAS Agent Engine agents.
    Loads domains from the filesystem, registers agents, dispatches tasks,
    and manages the full agent lifecycle.
    """

    def __init__(
        self,
        domains_base: str = config.DOMAINS_BASE_PATH,
    ) -> None:
        self._domains_base = Path(domains_base)
        self._registry: dict[str, AgentState] = {}      # agent_name → AgentState
        self._domains: dict[str, DomainConfig] = {}     # domain_name → DomainConfig

        # Shared components
        self._tool_registry = ToolRegistry()
        self._runner = AgentRunner(self._tool_registry)
        self._model_router = ModelRouter()
        self._event_bus = EventBus()

        self._running = False
        self._tasks: list[asyncio.Task] = []

    # ─── Lifecycle ────────────────────────────────────────────────────────────

    async def startup(self) -> None:
        """Initialize all components and load domain configurations."""
        logger.info("AgentOrchestrator starting up...")
        await self._tool_registry.startup()
        await self._model_router.startup()
        await self._event_bus.connect()

        self.load_domains()
        self._register_event_handlers()
        logger.info(
            "AgentOrchestrator ready — %d domains, %d agents registered",
            len(self._domains), len(self._registry),
        )

    async def shutdown(self) -> None:
        """Stop all running tasks and shut down components."""
        self._running = False
        for task in self._tasks:
            if not task.done():
                task.cancel()
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)

        await self._event_bus.disconnect()
        await self._tool_registry.shutdown()
        await self._model_router.shutdown()
        logger.info("AgentOrchestrator shut down cleanly")

    # ─── Domain Loading ───────────────────────────────────────────────────────

    def load_domains(self) -> dict[str, DomainConfig]:
        """
        Scan the domains/ directory for all config/agents.yaml files.
        Parses each and registers all enabled agents into the registry.
        Returns mapping of domain_name → DomainConfig.
        """
        self._domains.clear()
        self._registry.clear()

        if not self._domains_base.exists():
            raise FileNotFoundError(f"Domains base path not found: {self._domains_base}")

        yaml_files = sorted(self._domains_base.glob("*/config/agents.yaml"))
        if not yaml_files:
            logger.warning("No agents.yaml files found under %s", self._domains_base)

        for yaml_path in yaml_files:
            try:
                domain_config = self._parse_domain_yaml(yaml_path)
                self._domains[domain_config.domain] = domain_config
                for agent_cfg in domain_config.agents:
                    self._registry[agent_cfg.name] = AgentState(config=agent_cfg)
                logger.info(
                    "Loaded domain '%s' — %d agents",
                    domain_config.domain, len(domain_config.agents),
                )
            except Exception as exc:
                logger.error("Failed to load domain config %s: %s", yaml_path, exc, exc_info=True)

        return self._domains

    def _parse_domain_yaml(self, yaml_path: Path) -> DomainConfig:
        """Parse a domain agents.yaml file into a DomainConfig object."""
        with yaml_path.open("r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)

        domain_dir = yaml_path.parent.parent  # domains/{domain_name}/

        agents = []
        for agent_raw in raw.get("agents", []):
            # Resolve absolute path to the .md file
            relative_file = agent_raw["file"]  # e.g. "agents/market_monitor_agent.md"
            md_path = str((domain_dir / relative_file).resolve())

            agent_cfg = AgentConfig(
                name=agent_raw["name"],
                file=relative_file,
                md_path=md_path,
                domain=raw["domain"],
                enabled=agent_raw.get("enabled", True),
                schedule=agent_raw.get("schedule", "event-driven"),
                priority=agent_raw.get("priority", 5),
                dependencies=agent_raw.get("dependencies", []),
                triggers=agent_raw.get("triggers", []),
            )
            agents.append(agent_cfg)

            # Pre-load the agent .md if it exists
            if Path(md_path).exists():
                try:
                    self._runner.load_agent(md_path)
                except Exception as exc:
                    logger.warning("Could not pre-load agent .md '%s': %s", md_path, exc)

        return DomainConfig(
            domain=raw["domain"],
            version=raw.get("version", "1.0"),
            description=raw.get("description", ""),
            agents=agents,
        )

    # ─── Dispatching ──────────────────────────────────────────────────────────

    async def dispatch(
        self,
        agent_name: str,
        task: str = "",
        payload: Optional[dict[str, Any]] = None,
    ) -> AgentExecutionResult:
        """
        Dispatch a task to a specific agent by name.
        Checks agent state (enabled, not already running) before execution.
        Returns AgentExecutionResult regardless of success/failure.
        """
        if agent_name not in self._registry:
            raise KeyError(f"Agent '{agent_name}' not found in registry")

        state = self._registry[agent_name]

        if not state.config.enabled:
            raise RuntimeError(f"Agent '{agent_name}' is disabled")

        if state.status == AgentStatus.RUNNING:
            logger.warning("Agent '%s' is already running — skipping dispatch", agent_name)
            return AgentExecutionResult(
                agent_name=agent_name,
                success=False,
                error="Agent already running",
            )

        if state.status == AgentStatus.PAUSED:
            logger.info("Agent '%s' is paused — skipping dispatch", agent_name)
            return AgentExecutionResult(
                agent_name=agent_name,
                success=False,
                error="Agent is paused",
            )

        # Check dependencies
        for dep_name in state.config.dependencies:
            dep_state = self._registry.get(dep_name)
            if dep_state and dep_state.status == AgentStatus.ERROR and dep_state.consecutive_errors >= 3:
                logger.warning(
                    "Agent '%s' dependency '%s' is in error state — proceeding anyway",
                    agent_name, dep_name,
                )

        # Execute
        state.status = AgentStatus.RUNNING
        try:
            execution_payload = {**(payload or {}), "task": task}
            result = await self._runner.execute(state.config.md_path, execution_payload)

            import time
            state.last_run_at = time.time()
            state.last_run_result = result
            state.run_count += 1

            if result.success:
                state.consecutive_errors = 0
                state.status = AgentStatus.IDLE
            else:
                state.error_count += 1
                state.consecutive_errors += 1
                state.status = AgentStatus.ERROR if state.consecutive_errors >= 3 else AgentStatus.IDLE

            return result

        except Exception as exc:
            state.error_count += 1
            state.consecutive_errors += 1
            state.status = AgentStatus.ERROR
            logger.error("Dispatch error for agent '%s': %s", agent_name, exc, exc_info=True)
            return AgentExecutionResult(
                agent_name=agent_name,
                success=False,
                error=str(exc),
            )

    async def dispatch_domain(
        self,
        domain_name: str,
        payload: Optional[dict[str, Any]] = None,
    ) -> list[AgentExecutionResult]:
        """
        Dispatch all enabled agents in a domain, respecting priority ordering.
        Agents with the same priority run concurrently; lower number = higher priority.
        """
        if domain_name not in self._domains:
            raise KeyError(f"Domain '{domain_name}' not loaded")

        domain = self._domains[domain_name]
        enabled_agents = [a for a in domain.agents if a.enabled]

        # Group by priority
        by_priority: dict[int, list[str]] = {}
        for agent in enabled_agents:
            by_priority.setdefault(agent.priority, []).append(agent.name)

        all_results: list[AgentExecutionResult] = []
        for priority in sorted(by_priority.keys()):
            names = by_priority[priority]
            tasks = [self.dispatch(name, payload=payload) for name in names]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for r in results:
                if isinstance(r, Exception):
                    all_results.append(AgentExecutionResult(
                        agent_name="unknown", success=False, error=str(r)
                    ))
                else:
                    all_results.append(r)

        return all_results

    async def run_all(
        self,
        payload: Optional[dict[str, Any]] = None,
    ) -> dict[str, list[AgentExecutionResult]]:
        """
        Run all enabled agents across all domains.
        Returns mapping of domain_name → list of AgentExecutionResult.
        """
        all_results: dict[str, list[AgentExecutionResult]] = {}
        for domain_name in sorted(self._domains.keys()):
            logger.info("Running all agents in domain: %s", domain_name)
            try:
                results = await self.dispatch_domain(domain_name, payload)
                all_results[domain_name] = results
            except Exception as exc:
                logger.error("Error running domain '%s': %s", domain_name, exc)
                all_results[domain_name] = []
        return all_results

    # ─── Lifecycle Control ────────────────────────────────────────────────────

    def pause(self, agent_name: str) -> None:
        """Pause a specific agent — it will skip scheduled and event-driven runs."""
        if agent_name not in self._registry:
            raise KeyError(f"Agent '{agent_name}' not registered")
        state = self._registry[agent_name]
        if state.status == AgentStatus.RUNNING:
            raise RuntimeError(f"Cannot pause agent '{agent_name}' while it is running")
        state.status = AgentStatus.PAUSED
        logger.info("Agent '%s' paused", agent_name)

    def resume(self, agent_name: str) -> None:
        """Resume a paused agent."""
        if agent_name not in self._registry:
            raise KeyError(f"Agent '{agent_name}' not registered")
        state = self._registry[agent_name]
        if state.status == AgentStatus.PAUSED:
            state.status = AgentStatus.IDLE
            logger.info("Agent '%s' resumed", agent_name)

    def stop(self, agent_name: str) -> None:
        """Disable an agent entirely until explicitly re-enabled."""
        if agent_name not in self._registry:
            raise KeyError(f"Agent '{agent_name}' not registered")
        self._registry[agent_name].config.enabled = False
        self._registry[agent_name].status = AgentStatus.DISABLED
        logger.info("Agent '%s' disabled", agent_name)

    def enable(self, agent_name: str) -> None:
        """Re-enable a previously stopped/disabled agent."""
        if agent_name not in self._registry:
            raise KeyError(f"Agent '{agent_name}' not registered")
        state = self._registry[agent_name]
        state.config.enabled = True
        state.status = AgentStatus.IDLE
        state.consecutive_errors = 0
        logger.info("Agent '%s' enabled", agent_name)

    # ─── Status & Introspection ───────────────────────────────────────────────

    def get_status(self, agent_name: Optional[str] = None) -> dict[str, Any]:
        """
        Return status for a specific agent or all agents if name is None.
        Includes: status, run_count, error_count, last_run_at, domain, schedule.
        """
        import time

        if agent_name:
            if agent_name not in self._registry:
                raise KeyError(f"Agent '{agent_name}' not registered")
            state = self._registry[agent_name]
            return self._format_agent_status(state)

        # All agents grouped by domain
        status: dict[str, Any] = {
            "domains": {},
            "total_agents": len(self._registry),
            "running": sum(1 for s in self._registry.values() if s.status == AgentStatus.RUNNING),
            "errors": sum(1 for s in self._registry.values() if s.status == AgentStatus.ERROR),
        }
        for domain_name, domain_cfg in self._domains.items():
            domain_agents = [a.name for a in domain_cfg.agents]
            status["domains"][domain_name] = {
                "description": domain_cfg.description,
                "agents": {
                    name: self._format_agent_status(self._registry[name])
                    for name in domain_agents
                    if name in self._registry
                },
            }
        return status

    def _format_agent_status(self, state: AgentState) -> dict[str, Any]:
        """Format a single AgentState into a serializable status dict."""
        return {
            "name": state.config.name,
            "domain": state.config.domain,
            "status": state.status.value,
            "enabled": state.config.enabled,
            "schedule": state.config.schedule,
            "priority": state.config.priority,
            "run_count": state.run_count,
            "error_count": state.error_count,
            "consecutive_errors": state.consecutive_errors,
            "last_run_at": state.last_run_at,
            "dependencies": state.config.dependencies,
        }

    def list_agents(self, domain: Optional[str] = None) -> list[str]:
        """Return list of all agent names, optionally filtered by domain."""
        if domain:
            domain_cfg = self._domains.get(domain)
            if not domain_cfg:
                return []
            return [a.name for a in domain_cfg.agents]
        return list(self._registry.keys())

    def list_domains(self) -> list[str]:
        """Return list of all loaded domain names."""
        return list(self._domains.keys())

    # ─── Event Handling ───────────────────────────────────────────────────────

    def _register_event_handlers(self) -> None:
        """Subscribe orchestrator-level event handlers to the event bus."""

        async def handle_agent_dispatch(event_type: str, payload: dict[str, Any]) -> None:
            """Handle direct agent dispatch events from the event bus."""
            agent_name = payload.get("agent_name")
            if agent_name and agent_name in self._registry:
                await self.dispatch(agent_name, task=event_type, payload=payload)

        self._event_bus.subscribe("agent_dispatch_requested", handle_agent_dispatch)

    # ─── Components Access ────────────────────────────────────────────────────

    @property
    def tool_registry(self) -> ToolRegistry:
        return self._tool_registry

    @property
    def event_bus(self) -> EventBus:
        return self._event_bus

    @property
    def model_router(self) -> ModelRouter:
        return self._model_router

    @property
    def runner(self) -> AgentRunner:
        return self._runner
