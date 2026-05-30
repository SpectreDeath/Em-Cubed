"""Tests for the LLM surface: cloud, Ollama fallback, streaming, and function calling."""

import asyncio
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from em_cubed.surfaces.llm_surface import LLMSurface


@pytest.fixture
def llm_surface():
    return LLMSurface(timeout=10.0)


# ---------------------------------------------------------------------------
# Basic availability / metadata
# ---------------------------------------------------------------------------

def test_llm_surface_initialization(llm_surface):
    assert llm_surface.name == "llm"
    assert "Unified LLM execution" in llm_surface.description
    assert llm_surface.timeout == 10.0


def test_llm_surface_available():
    surface = LLMSurface()
    assert surface.available is True


def test_llm_surface_extract_tags():
    surface = LLMSurface()
    assert surface.extract_tags("any prompt") == []
    assert surface.extract_tags("") == []
    assert surface.extract_tags(None) == []


# ---------------------------------------------------------------------------
# No-cloud-keys paths (Ollama fallback)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_ollama_fallback_success(llm_surface):
    """When no cloud keys, route to Ollama and return its response."""
    import em_cubed.surfaces.llm_surface as mod

    ollama_ok = {"status": "ok", "value": "Hello from Ollama", "provider": "ollama", "model": "llama3"}

    with patch.object(mod.LLMSurface, "_has_cloud_keys", return_value=False):
        with patch.object(llm_surface._ollama, "is_available", new=AsyncMock(return_value=True)):
            with patch.object(llm_surface._ollama, "list_models", new=AsyncMock(return_value=["llama3"])):
                with patch.object(llm_surface._ollama, "chat", new=AsyncMock(return_value=ollama_ok)):
                    result = await llm_surface.execute("Say hello", context={"model": "llama3"})

    assert result["status"] == "ok"
    assert result["value"] == "Hello from Ollama"
    assert result["provider"] == "ollama"


@pytest.mark.asyncio
async def test_ollama_model_fallback_to_available(llm_surface):
    """If requested model isn't pulled, fall back to first available model."""
    import em_cubed.surfaces.llm_surface as mod

    ollama_ok = {"status": "ok", "value": "Fallback model response", "provider": "ollama", "model": "mistral"}

    with patch.object(mod.LLMSurface, "_has_cloud_keys", return_value=False):
        with patch.object(llm_surface._ollama, "is_available", new=AsyncMock(return_value=True)):
            with patch.object(llm_surface._ollama, "list_models", new=AsyncMock(return_value=["mistral"])):
                with patch.object(llm_surface._ollama, "chat", new=AsyncMock(return_value=ollama_ok)) as mock_chat:
                    result = await llm_surface.execute("Compute 2+2", context={"model": "llama3"})
                    # The surface should have used "mistral" (first available) not "llama3"
                    _, call_kwargs = mock_chat.call_args[0], mock_chat.call_args
                    assert call_kwargs[0][1] == "mistral"

    assert result["status"] == "ok"


@pytest.mark.asyncio
async def test_all_unavailable_returns_error(llm_surface):
    """Return an actionable error when neither cloud keys nor Ollama is available."""
    import em_cubed.surfaces.llm_surface as mod

    with patch.object(mod.LLMSurface, "_has_cloud_keys", return_value=False):
        with patch.object(llm_surface._ollama, "is_available", new=AsyncMock(return_value=False)):
            result = await llm_surface.execute("Hello")

    assert result["status"] == "error"
    assert "No LLM backend available" in result["message"]


# ---------------------------------------------------------------------------
# Cloud LiteLLM path
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_cloud_path_non_streaming(llm_surface):
    """Non-streaming cloud call returns the message content."""
    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
        with patch("litellm.acompletion") as mock_acompletion:
            mock_resp = MagicMock()
            mock_resp.choices = [MagicMock()]
            mock_resp.choices[0].message.content = "Paris"
            mock_acompletion.return_value = mock_resp

            result = await llm_surface.execute(
                "Capital of France?",
                context={"model": "gpt-4o", "temperature": 0.0},
            )

    assert result["status"] == "ok"
    assert result["value"] == "Paris"
    assert result["provider"] == "litellm"
    assert result["model"] == "gpt-4o"


@pytest.mark.asyncio
async def test_cloud_path_streaming(llm_surface):
    """Streaming cloud call concatenates delta content from all chunks."""
    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
        with patch("litellm.acompletion") as mock_acompletion:
            async def mock_stream(*args, **kwargs):
                for word in ["Hello", " ", "world"]:
                    chunk = MagicMock()
                    chunk.choices = [MagicMock()]
                    chunk.choices[0].delta.content = word
                    yield chunk

            mock_acompletion.return_value = mock_stream()

            result = await llm_surface.execute(
                "Say hello",
                context={"stream": True, "max_tokens": 10},
            )

    assert result["status"] == "ok"
    assert result["value"] == "Hello world"
    assert result["provider"] == "litellm"


@pytest.mark.asyncio
async def test_cloud_path_with_tools(llm_surface):
    """Function-calling (tools) parameters are passed through to LiteLLM."""
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get weather in a location",
                "parameters": {
                    "type": "object",
                    "properties": {"location": {"type": "string"}},
                    "required": ["location"],
                },
            },
        }
    ]

    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
        with patch("litellm.acompletion") as mock_acompletion:
            mock_resp = MagicMock()
            mock_resp.choices = [MagicMock()]
            mock_resp.choices[0].message.content = "It's sunny."
            mock_acompletion.return_value = mock_resp

            result = await llm_surface.execute(
                "What's the weather in SF?",
                context={"tools": tools},
            )

            # Verify tools were forwarded
            call_kwargs = mock_acompletion.call_args[1]
            assert call_kwargs.get("tools") == tools

    assert result["status"] == "ok"
    assert result["value"] == "It's sunny."


@pytest.mark.asyncio
async def test_litellm_error_surfaces_error_status(llm_surface):
    """If LiteLLM raises an exception the surface returns a status=error dict."""
    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
        with patch("litellm.acompletion", side_effect=RuntimeError("API down")):
            result = await llm_surface.execute("Hello")

    assert result["status"] == "error"
    assert "API down" in result["message"]


# ---------------------------------------------------------------------------
# Timeout
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_timeout_handling(llm_surface):
    """Execution exceeding the timeout returns a timeout error."""
    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
        with patch("litellm.acompletion") as mock_completion:
            async def slow(*args, **kwargs):
                await asyncio.sleep(0.3)
                return MagicMock()

            mock_completion.side_effect = slow
            llm_surface.timeout = 0.05

            result = await llm_surface.execute("This should timeout")

    assert result["status"] == "error"
    assert "timed out" in result["message"]


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_health_cloud_key_present(llm_surface):
    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
        assert await llm_surface.health() is True


@pytest.mark.asyncio
async def test_health_ollama_only(llm_surface):
    import em_cubed.surfaces.llm_surface as mod
    with patch.object(mod.LLMSurface, "_has_cloud_keys", return_value=False):
        with patch.object(llm_surface._ollama, "is_available", new=AsyncMock(return_value=True)):
            assert await llm_surface.health() is True


@pytest.mark.asyncio
async def test_health_nothing_available(llm_surface):
    import em_cubed.surfaces.llm_surface as mod
    with patch.object(mod.LLMSurface, "_has_cloud_keys", return_value=False):
        with patch.object(llm_surface._ollama, "is_available", new=AsyncMock(return_value=False)):
            assert await llm_surface.health() is False


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])