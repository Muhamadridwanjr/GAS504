"""
GAS Agent Engine — Agent Runner
Reads agent .md files, parses ROLE/TASKS/TOOLS/WORKFLOW sections,
and executes the agent workflow step-by-step via the ToolRegistry.
"""

from __future__ import annotations

import asyncio
import logging
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

import config
from tool_registry import ToolRegistry

logger = logging.getLogger(__name__)


# ─── Data classes ─────────────────────────────────────────────────────────────

@dataclass
class AgentDefinition:
    """Parsed representation of an agent .md file."""
    name: str
    role: str
    tasks: list[str]
    tools: dict[str, str]         # tool_name → description
    workflow: list[str]           # ordered workflow steps
    triggers: list[str]
    outputs: list[str]
    source_path: str


@dataclass
class StepResult:
    """Result of executing a single workflow step."""
    step_index: int
    step_text: str
    tool_called: Optional[str]
    tool_kwargs: dict[str, Any]
    result: Any
    success: bool
    error: Optional[str]
    duration_ms: float


@dataclass
class AgentExecutionResult:
    """Full result of one agent execution run."""
    agent_name: str
    success: bool
    steps: list[StepResult] = field(default_factory=list)
    total_duration_ms: float = 0.0
    error: Optional[str] = None
    payload_in: dict[str, Any] = field(default_factory=dict)
    payload_out: dict[str, Any] = field(default_factory=dict)


# ─── Agent Runner ─────────────────────────────────────────────────────────────

class AgentRunner:
    """
    Loads an agent definition from a .md file and executes its workflow
    by mapping step instructions to tool calls in the ToolRegistry.
    """

    # Regex patterns for markdown section headers
    _SECTION_RE = re.compile(r"^##\s+(.+)$", re.MULTILINE)
    _TOOL_LINE_RE = re.compile(r"^-\s+`?(\w+)`?:\s+(.+)$")
    _STEP_LINE_RE = re.compile(r"^\d+\.\s+(.+)$")
    _LIST_ITEM_RE = re.compile(r"^-\s+(.+)$")

    # Tool call pattern in step text: matches tool_name(...) or tool_name: ...
    _TOOL_CALL_RE = re.compile(
        r"\b(read_logs|check_websocket|metrics_reader|call_service|publish_event|"
        r"query_redis|write_redis|send_alert|query_db|fetch_ohlcv|run_backtest|"
        r"embed_text|search_vectors)\b"
    )

    def __init__(self, registry: ToolRegistry) -> None:
        self._registry = registry
        self._definitions: dict[str, AgentDefinition] = {}

    # ─── Loading ──────────────────────────────────────────────────────────────

    def load_agent(self, md_path: str) -> AgentDefinition:
        """
        Load and parse an agent .md file.
        Returns an AgentDefinition with all sections parsed.
        Caches the definition keyed by file path.
        """
        path = Path(md_path)
        if not path.exists():
            raise FileNotFoundError(f"Agent file not found: {md_path}")

        content = path.read_text(encoding="utf-8")
        definition = self.parse_md(content)
        definition.source_path = str(path.resolve())
        definition.name = definition.name or path.stem

        self._definitions[str(path.resolve())] = definition
        logger.debug("Loaded agent '%s' from %s", definition.name, md_path)
        return definition

    def parse_md(self, content: str) -> AgentDefinition:
        """
        Parse a markdown agent definition file into an AgentDefinition object.
        Extracts the H1 title as agent name, then parses all ## sections.
        """
        lines = content.splitlines()

        # Extract agent name from first H1
        name = ""
        for line in lines:
            if line.startswith("# "):
                name = line[2:].strip()
                break

        # Split content into sections
        sections = self._split_sections(content)

        role = self._extract_role(sections.get("ROLE", ""))
        tasks = self._extract_list(sections.get("TASKS", ""))
        tools = self._extract_tools(sections.get("TOOLS", ""))
        workflow = self._extract_workflow(sections.get("WORKFLOW", ""))
        triggers = self._extract_list(sections.get("TRIGGERS", ""))
        outputs = self._extract_list(sections.get("OUTPUTS", ""))

        return AgentDefinition(
            name=name,
            role=role,
            tasks=tasks,
            tools=tools,
            workflow=workflow,
            triggers=triggers,
            outputs=outputs,
            source_path="",
        )

    def _split_sections(self, content: str) -> dict[str, str]:
        """Split markdown content into named sections at ## headers."""
        sections: dict[str, str] = {}
        current_section = ""
        current_lines: list[str] = []

        for line in content.splitlines():
            match = re.match(r"^##\s+(.+)$", line)
            if match:
                if current_section:
                    sections[current_section] = "\n".join(current_lines).strip()
                current_section = match.group(1).strip().upper()
                current_lines = []
            else:
                if current_section:
                    current_lines.append(line)

        if current_section:
            sections[current_section] = "\n".join(current_lines).strip()

        return sections

    def _extract_role(self, text: str) -> str:
        """Extract role as cleaned paragraph text."""
        return " ".join(text.split())

    def _extract_list(self, text: str) -> list[str]:
        """Extract markdown bullet list items."""
        items = []
        for line in text.splitlines():
            match = self._LIST_ITEM_RE.match(line.strip())
            if match:
                items.append(match.group(1).strip())
        return items

    def _extract_tools(self, text: str) -> dict[str, str]:
        """Extract tool definitions: `tool_name: description` pairs."""
        tools = {}
        for line in text.splitlines():
            match = self._TOOL_LINE_RE.match(line.strip())
            if match:
                tools[match.group(1)] = match.group(2).strip()
        return tools

    def _extract_workflow(self, text: str) -> list[str]:
        """Extract numbered workflow steps as ordered list."""
        steps = []
        for line in text.splitlines():
            match = self._STEP_LINE_RE.match(line.strip())
            if match:
                steps.append(match.group(1).strip())
        return steps

    # ─── Execution ────────────────────────────────────────────────────────────

    async def execute(
        self,
        agent_name_or_path: str,
        payload: Optional[dict[str, Any]] = None,
    ) -> AgentExecutionResult:
        """
        Execute an agent by name (if already loaded) or .md file path.
        Runs each workflow step sequentially, collecting results.
        """
        # Resolve definition
        definition = self._resolve_definition(agent_name_or_path)
        if not definition:
            raise ValueError(f"Agent not found: '{agent_name_or_path}'. Load it first with load_agent().")

        payload = payload or {}
        result = AgentExecutionResult(
            agent_name=definition.name,
            success=False,
            payload_in=payload,
        )
        start_total = time.monotonic()

        logger.info("Executing agent '%s' with %d workflow steps", definition.name, len(definition.workflow))

        try:
            for i, step_text in enumerate(definition.workflow):
                step_result = await self.run_step(step_text, i, payload, definition)
                result.steps.append(step_result)

                if not step_result.success:
                    logger.warning(
                        "Agent '%s' step %d failed: %s — continuing",
                        definition.name, i + 1, step_result.error,
                    )
                    # Continue execution: agents should be resilient to individual step failures

            result.success = True
            result.payload_out = {"steps_completed": len(result.steps)}

        except Exception as exc:
            result.error = str(exc)
            result.success = False
            logger.error("Agent '%s' execution aborted: %s", definition.name, exc, exc_info=True)

        result.total_duration_ms = round((time.monotonic() - start_total) * 1000, 1)
        logger.info(
            "Agent '%s' finished — success=%s steps=%d duration=%.1fms",
            definition.name, result.success, len(result.steps), result.total_duration_ms,
        )
        return result

    async def run_step(
        self,
        step_text: str,
        step_index: int,
        payload: dict[str, Any],
        definition: AgentDefinition,
    ) -> StepResult:
        """
        Execute a single workflow step by detecting tool calls in the step text
        and invoking the appropriate tool with contextual kwargs.
        """
        start = time.monotonic()
        tool_name: Optional[str] = None
        tool_kwargs: dict[str, Any] = {}

        try:
            # Detect which tool this step uses
            tool_match = self._TOOL_CALL_RE.search(step_text)
            if tool_match:
                tool_name = tool_match.group(1)
                tool_kwargs = self._extract_tool_kwargs(step_text, tool_name, payload)

                result = await self._invoke_tool_with_retry(tool_name, **tool_kwargs)
            else:
                # Pure logic/computation step — no tool call, just log it
                logger.debug("Agent step %d (no tool): %s", step_index + 1, step_text[:80])
                result = {"step": step_index + 1, "status": "logic_step", "text": step_text}

            return StepResult(
                step_index=step_index,
                step_text=step_text,
                tool_called=tool_name,
                tool_kwargs=tool_kwargs,
                result=result,
                success=True,
                error=None,
                duration_ms=round((time.monotonic() - start) * 1000, 1),
            )

        except Exception as exc:
            return StepResult(
                step_index=step_index,
                step_text=step_text,
                tool_called=tool_name,
                tool_kwargs=tool_kwargs,
                result=None,
                success=False,
                error=str(exc),
                duration_ms=round((time.monotonic() - start) * 1000, 1),
            )

    @retry(
        stop=stop_after_attempt(config.AGENT_MAX_RETRIES),
        wait=wait_exponential(multiplier=config.AGENT_RETRY_BASE_DELAY, min=1, max=30),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        reraise=True,
    )
    async def _invoke_tool_with_retry(self, tool_name: str, **kwargs: Any) -> Any:
        """Invoke a tool with exponential-backoff retry on transient failures."""
        return await self._registry.call(tool_name, **kwargs)

    def _extract_tool_kwargs(
        self,
        step_text: str,
        tool_name: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Build keyword arguments for a tool call from step text and execution payload.
        Pulls symbol, timeframe, service names, and Redis keys mentioned in the step.
        """
        kwargs: dict[str, Any] = {}

        # Propagate common payload fields if available
        for field in ("symbol", "timeframe", "user_id", "signal_id", "job_id"):
            if field in payload:
                kwargs[field] = payload[field]

        # Extract service name from step text for call_service / check_websocket
        if tool_name in ("call_service", "check_websocket", "read_logs"):
            service_match = re.search(
                r"gas-[\w-]+|mt5-websocket|realtime-hub|binance-service", step_text
            )
            if service_match:
                kwargs["service"] = service_match.group(0)

        # Extract Redis key from step text for query_redis / write_redis
        if tool_name in ("query_redis", "write_redis"):
            key_match = re.search(r"`([^`]+:[^`]+)`", step_text)
            if key_match:
                kwargs["key"] = key_match.group(1)

        # For query_db, pass the step text as a hint (actual SQL is constructed by service)
        if tool_name == "query_db":
            kwargs["hint"] = step_text[:200]

        # For publish_event, extract event type from step text
        if tool_name == "publish_event":
            event_match = re.search(r"`(\w+_\w+(?:_\w+)*)`", step_text)
            if event_match:
                kwargs["event_type"] = event_match.group(1)
                kwargs["payload"] = payload

        # For send_alert, extract level from step text
        if tool_name == "send_alert":
            level_match = re.search(r"\b(INFO|WARNING|CRITICAL|EMERGENCY)\b", step_text.upper())
            kwargs["level"] = level_match.group(1) if level_match else "INFO"
            kwargs["message"] = step_text[:200]

        return kwargs

    def _resolve_definition(self, name_or_path: str) -> Optional[AgentDefinition]:
        """Resolve an agent definition by name or file path."""
        # Check by exact file path
        resolved = str(Path(name_or_path).resolve()) if Path(name_or_path).exists() else None
        if resolved and resolved in self._definitions:
            return self._definitions[resolved]

        # Check by agent name
        for defn in self._definitions.values():
            if defn.name == name_or_path or defn.name.lower() == name_or_path.lower():
                return defn

        # Try loading the file directly if it exists
        if Path(name_or_path).exists():
            return self.load_agent(name_or_path)

        return None

    @property
    def loaded_agents(self) -> list[str]:
        """Return list of all loaded agent names."""
        return [d.name for d in self._definitions.values()]
