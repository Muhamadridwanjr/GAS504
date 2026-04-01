"""
Circuit Breaker for gas-strategy-core.

States:
  CLOSED   — normal, requests flow through
  OPEN     — failure threshold hit, requests blocked (returns cached/fallback)
  HALF_OPEN — recovery probe, allow limited requests through

Usage:
  result = await strategy_core_cb.call(
      coro_func, *args,
      fallback=some_fallback_func,
      **kwargs
  )
"""
import time
import asyncio
import logging
from enum import Enum
from typing import Callable, Any, Optional

log = logging.getLogger("gas.circuit_breaker")


class CircuitState(Enum):
    CLOSED    = "CLOSED"
    OPEN      = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreaker:
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        half_open_max: int = 2,
    ):
        self.name             = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout  = recovery_timeout
        self.half_open_max     = half_open_max

        self._state           = CircuitState.CLOSED
        self._failure_count   = 0
        self._half_open_count = 0
        self._last_failure_ts = 0.0
        self._lock            = asyncio.Lock()

    # ── State transitions ──────────────────────────────────────────────────────

    @property
    def state(self) -> CircuitState:
        if (
            self._state == CircuitState.OPEN
            and time.monotonic() - self._last_failure_ts >= self.recovery_timeout
        ):
            self._state           = CircuitState.HALF_OPEN
            self._half_open_count = 0
            log.warning(f"[{self.name}] → HALF_OPEN — probing recovery")
        return self._state

    def _on_success(self):
        if self._state in (CircuitState.HALF_OPEN, CircuitState.OPEN):
            log.info(f"[{self.name}] recovery confirmed → CLOSED")
        self._state         = CircuitState.CLOSED
        self._failure_count = 0

    def _on_failure(self, exc: Exception):
        self._failure_count  += 1
        self._last_failure_ts = time.monotonic()
        if self._failure_count >= self.failure_threshold:
            self._state = CircuitState.OPEN
            log.error(
                f"[{self.name}] → OPEN after {self._failure_count} failures. "
                f"Retry in {self.recovery_timeout}s. Last error: {exc}"
            )
        else:
            log.warning(
                f"[{self.name}] failure {self._failure_count}/{self.failure_threshold}: {exc}"
            )

    # ── Main call wrapper ──────────────────────────────────────────────────────

    async def call(
        self,
        func: Callable,
        *args: Any,
        fallback: Optional[Callable] = None,
        **kwargs: Any,
    ) -> Any:
        """
        Call `func(*args, **kwargs)` through the circuit breaker.
        If OPEN and `fallback` is provided, calls fallback instead.
        Raises CircuitOpenError if OPEN and no fallback is given.
        """
        async with self._lock:
            current = self.state

        if current == CircuitState.OPEN:
            log.warning(f"[{self.name}] is OPEN — request blocked")
            if fallback:
                return await _maybe_await(fallback, *args, **kwargs)
            raise CircuitOpenError(
                f"Circuit '{self.name}' is OPEN. Service unavailable. "
                f"Retry in {max(0, self.recovery_timeout - (time.monotonic() - self._last_failure_ts)):.0f}s."
            )

        if current == CircuitState.HALF_OPEN:
            async with self._lock:
                self._half_open_count += 1
                if self._half_open_count > self.half_open_max:
                    log.warning(f"[{self.name}] HALF_OPEN probe limit reached")
                    if fallback:
                        return await _maybe_await(fallback, *args, **kwargs)
                    raise CircuitOpenError(f"Circuit '{self.name}' probe limit reached.")

        try:
            result = await func(*args, **kwargs)
            async with self._lock:
                self._on_success()
            return result
        except Exception as exc:
            async with self._lock:
                self._on_failure(exc)
            raise

    # ── Diagnostics ───────────────────────────────────────────────────────────

    def status(self) -> dict:
        return {
            "name":          self.name,
            "state":         self.state.value,
            "failures":      self._failure_count,
            "threshold":     self.failure_threshold,
            "recovery_in_s": max(0, self.recovery_timeout - (time.monotonic() - self._last_failure_ts))
                             if self._state == CircuitState.OPEN else 0,
        }


async def _maybe_await(func: Callable, *args, **kwargs):
    result = func(*args, **kwargs)
    if asyncio.iscoroutine(result):
        return await result
    return result


class CircuitOpenError(Exception):
    pass


# ── Registry — one breaker per (service, endpoint) pair ───────────────────────
# Problem: a global breaker for gas-strategy-core means that 5 failures on
# /v1/analysis/briefing (slow) would block /v1/analysis/signal (fast). Per-endpoint
# isolation prevents healthy endpoints from being blocked by noisy neighbours.

class CircuitBreakerRegistry:
    """Lazy-init, thread-safe registry of per-key circuit breakers."""
    _breakers: dict[str, "CircuitBreaker"] = {}

    @classmethod
    def get(
        cls,
        key: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        half_open_max: int = 2,
    ) -> "CircuitBreaker":
        if key not in cls._breakers:
            cls._breakers[key] = CircuitBreaker(
                name=key,
                failure_threshold=failure_threshold,
                recovery_timeout=recovery_timeout,
                half_open_max=half_open_max,
            )
        return cls._breakers[key]

    @classmethod
    def all_statuses(cls) -> list[dict]:
        return [cb.status() for cb in cls._breakers.values()]


# ── Backward-compatible singleton (kept for external import compatibility) ─────

strategy_core_cb = CircuitBreakerRegistry.get("gas-strategy-core")
