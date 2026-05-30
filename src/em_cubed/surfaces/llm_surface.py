"""LLM surface integration for executing prompts via LiteLLM with a local-first Ollama fallback.

Execution chain (in priority order):
1. Cloud LLM via LiteLLM  — used when any cloud API key env-var is set.
2. Local Ollama            — used when no cloud keys are found; requires an Ollama
                             server running on OLLAMA_HOST (default localhost:11434).
3. Error                   — returned when both paths are unavailable so callers get
                             clear, actionable feedback instead of a silent mock.
"""

from __future__ import annotations

import asyncio
import os
from typing import Dict, Any, Optional
import structlog

from .base import SurfaceBase

logger = structlog.get_logger()

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_CLOUD_KEY_ENV_VARS = (
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "COHERE_API_KEY",
    "HUGGINGFACE_API_KEY",
    "LLM_API_KEY",
    "GEMINI_API_KEY",
    "GROQ_API_KEY",
    "MISTRAL_API_KEY",
    "AZURE_API_KEY",
)

_DEFAULT_OLLAMA_HOST = "http://localhost:11434"
_DEFAULT_OLLAMA_MODEL = "llama3"
_DEFAULT_CLOUD_MODEL  = "gpt-3.5-turbo"


# ---------------------------------------------------------------------------
# Ollama REST client (no extra package required — uses httpx which is already
# a transitive dependency of LiteLLM and listed in [dev] extras).
# ---------------------------------------------------------------------------

class _OllamaClient:
    """Thin async client for the Ollama local REST API."""

    def __init__(self, host: str, timeout: float):
        self._host    = host.rstrip("/")
        self._timeout = timeout

    async def is_available(self) -> bool:
        """Return True if the Ollama server is reachable."""
        try:
            import httpx
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(f"{self._host}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> list[str]:
        """Return names of locally-pulled models."""
        try:
            import httpx
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self._host}/api/tags")
                resp.raise_for_status()
                data = resp.json()
                return [m["name"] for m in data.get("models", [])]
        except Exception:
            return []

    async def chat(
        self,
        prompt: str,
        model: str,
        *,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        """
        Call ``POST /api/chat`` (non-streaming).

        Returns a dict with keys ``status`` and either ``value`` or ``message``.
        """
        try:
            import httpx

            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            payload = {
                "model":   model,
                "messages": messages,
                "stream":   False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            }

            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.post(
                    f"{self._host}/api/chat",
                    json=payload,
                )
                resp.raise_for_status()

            data = resp.json()
            content: str = data.get("message", {}).get("content", "")
            return {"status": "ok", "value": content, "provider": "ollama", "model": model}

        except Exception as exc:
            return {"status": "error", "message": f"Ollama request failed: {exc}"}


# ---------------------------------------------------------------------------
# LLMSurface
# ---------------------------------------------------------------------------

class LLMSurface(SurfaceBase):
    """Handle LLM prompt execution using LiteLLM for cloud and Ollama for local.

    Priority chain:
      1. LiteLLM  (when a supported cloud API key is present in the environment)
      2. Ollama   (when running locally with no cloud keys configured)
      3. Error    (clear message with actionable guidance)
    """

    def __init__(self, timeout: Optional[float] = None):
        super().__init__(timeout)
        ollama_host = os.getenv("OLLAMA_HOST", _DEFAULT_OLLAMA_HOST)
        self._ollama = _OllamaClient(ollama_host, timeout=self.timeout or 30.0)
        logger.info("LLMSurface initialized", timeout=self.timeout, ollama_host=ollama_host)

    # ------------------------------------------------------------------
    # SurfaceBase contract
    # ------------------------------------------------------------------

    def _check_availability(self) -> bool:
        """Return True if litellm is importable (cloud path) OR Ollama is available."""
        try:
            import litellm  # noqa: F401
            return True
        except ImportError:
            pass
        # Synchronous availability heuristic — just check if httpx is present
        try:
            import httpx  # noqa: F401
            return True
        except ImportError:
            return False

    @property
    def name(self) -> str:
        return "llm"

    @property
    def description(self) -> str:
        return (
            "Unified LLM execution via LiteLLM (cloud) with automatic local Ollama "
            "fallback. Supports multiple providers, streaming, and function calling."
        )

    @property
    def available(self) -> bool:
        return self._check_availability()

    @staticmethod
    def extract_tags(source: Optional[str]) -> list:  # type: ignore[override]
        """Extract tags — not applicable for raw LLM prompts; metadata defines tags."""
        return []

    # ------------------------------------------------------------------
    # Execution entry-point
    # ------------------------------------------------------------------

    async def execute(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute LLM prompt with timeout protection."""
        try:
            result = await asyncio.wait_for(
                self._execute_impl(code, context),
                timeout=self.timeout,
            )
            return result
        except asyncio.TimeoutError:
            logger.warning("LLM surface execution timed out", timeout=self.timeout)
            return {
                "status":  "error",
                "message": f"Execution timed out after {self.timeout}s",
            }

    async def _execute_impl(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return await self._run_prompt(code, context)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _has_cloud_keys() -> bool:
        """Return True if any recognised cloud API key is set in the environment."""
        return any(os.getenv(var) for var in _CLOUD_KEY_ENV_VARS)

    async def _run_prompt(
        self, prompt: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Route the prompt through the priority chain."""
        if not self.available:
            return {
                "status":  "error",
                "message": "LLM surface unavailable: install litellm or httpx.",
            }

        # ------------------------------------------------------------------
        # Path 1: Cloud LLM via LiteLLM
        # ------------------------------------------------------------------
        if self._has_cloud_keys():
            return await self._run_via_litellm(prompt, context)

        # ------------------------------------------------------------------
        # Path 2: Local Ollama fallback
        # ------------------------------------------------------------------
        logger.info(
            "No cloud API keys found — attempting local Ollama fallback",
            ollama_host=self._ollama._host,
        )
        ollama_result = await self._run_via_ollama(prompt, context)
        if ollama_result["status"] == "ok":
            return ollama_result

        # ------------------------------------------------------------------
        # Path 3: Both unavailable — return a clear, actionable error
        # ------------------------------------------------------------------
        logger.warning(
            "LLM surface: both cloud and local Ollama paths unavailable",
            ollama_error=ollama_result.get("message"),
        )
        return {
            "status":  "error",
            "message": (
                "No LLM backend available. "
                "Set a cloud API key (e.g. OPENAI_API_KEY) or start an Ollama server "
                f"on {self._ollama._host} (OLLAMA_HOST to override). "
                f"Ollama error: {ollama_result.get('message', 'unreachable')}"
            ),
        }

    # ------------------------------------------------------------------
    # Path 1: LiteLLM (cloud)
    # ------------------------------------------------------------------

    async def _run_via_litellm(
        self, prompt: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the prompt through LiteLLM using a configured cloud provider."""
        try:
            import litellm

            messages = [{"role": "user", "content": prompt}]
            if context and (system := context.get("system")):
                messages.insert(0, {"role": "system", "content": system})
            elif context:
                ctx_str = str({k: v for k, v in context.items() if k not in ("model", "temperature", "max_tokens", "stream", "tools", "tool_choice", "system")})
                if ctx_str != "{}":
                    messages.insert(0, {"role": "system", "content": f"Context: {ctx_str}"})

            model       = (context or {}).get("model", _DEFAULT_CLOUD_MODEL)
            temperature = (context or {}).get("temperature", 0.7)
            max_tokens  = (context or {}).get("max_tokens", 1000)
            stream      = (context or {}).get("stream", False)
            tools       = (context or {}).get("tools")
            tool_choice = (context or {}).get("tool_choice")

            logger.info(
                "Executing LLM prompt via LiteLLM (cloud)",
                model=model,
                prompt_length=len(prompt),
                stream=stream,
                has_tools=bool(tools),
            )

            response = await litellm.acompletion(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
                tools=tools,
                tool_choice=tool_choice,
                timeout=self.timeout,
            )

            if stream:
                chunks = []
                async for chunk in response:
                    chunks.append(chunk)
                if chunks:
                    # Accumulate delta content from every chunk
                    text_parts = []
                    for c in chunks:
                        if hasattr(c, "choices") and c.choices:
                            delta = c.choices[0].delta
                            if hasattr(delta, "content") and delta.content:
                                text_parts.append(delta.content)
                    generated_text = "".join(text_parts) or "[empty streaming response]"
                    logger.info("LiteLLM streaming complete", response_length=len(generated_text))
                    return {"status": "ok", "value": generated_text, "provider": "litellm", "model": model}
                return {"status": "error", "message": "No chunks received from streaming LLM"}
            else:
                if response and hasattr(response, "choices") and response.choices:
                    generated_text = response.choices[0].message.content or ""
                elif response and "choices" in response and response["choices"]:
                    generated_text = response["choices"][0]["message"]["content"]
                else:
                    return {"status": "error", "message": "Empty response from cloud LLM"}
                logger.info("LiteLLM execution successful", response_length=len(generated_text))
                return {"status": "ok", "value": generated_text, "provider": "litellm", "model": model}

        except Exception as exc:
            logger.exception("LiteLLM cloud execution failed", error=str(exc))
            return {"status": "error", "message": f"LiteLLM error: {exc}"}

    # ------------------------------------------------------------------
    # Path 2: Ollama (local)
    # ------------------------------------------------------------------

    async def _run_via_ollama(
        self, prompt: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the prompt through a locally-running Ollama server."""
        if not await self._ollama.is_available():
            return {"status": "error", "message": "Ollama server not reachable"}

        # Pick a model: prefer context override, then OLLAMA_MODEL env var, then default
        model = (
            (context or {}).get("model")
            or os.getenv("OLLAMA_MODEL")
            or _DEFAULT_OLLAMA_MODEL
        )

        # If the requested model is not pulled yet, pick first available
        available_models = await self._ollama.list_models()
        if available_models and model not in available_models:
            logger.warning(
                "Requested Ollama model not found locally — using first available",
                requested=model,
                available=available_models,
            )
            model = available_models[0]

        system      = (context or {}).get("system")
        temperature = (context or {}).get("temperature", 0.7)
        max_tokens  = (context or {}).get("max_tokens", 1024)

        logger.info(
            "Executing LLM prompt via local Ollama",
            model=model,
            prompt_length=len(prompt),
        )

        return await self._ollama.chat(
            prompt,
            model,
            system=system,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------

    async def health(self) -> bool:
        """Return True if at least one LLM path (cloud or local) is available."""
        if not self.available:
            return False
        if self._has_cloud_keys():
            return True
        return await self._ollama.is_available()