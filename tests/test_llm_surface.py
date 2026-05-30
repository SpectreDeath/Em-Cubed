"""Tests for LLM surface implementation."""

import asyncio
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from em_cubed.surfaces.llm_surface import LLMSurface


@pytest.fixture
def llm_surface():
    """Create an LLMSurface instance."""
    return LLMSurface(timeout=10.0)


def test_llm_surface_initialization(llm_surface):
    """Test LLMSurface initialization."""
    assert llm_surface.name == "llm"
    assert "Unified LLM execution" in llm_surface.description
    assert llm_surface.timeout == 10.0


def test_llm_surface_available_without_api_keys():
    """Test that LLMSurface reports available when litellm (or httpx) is installed."""
    surface = LLMSurface()
    assert surface.available is True


def test_llm_surface_extract_tags():
    """Test tag extraction returns empty list for LLM surface."""
    surface = LLMSurface()
    assert surface.extract_tags("any prompt") == []
    assert surface.extract_tags("") == []
    assert surface.extract_tags(None) == []


@pytest.mark.asyncio
async def test_llm_surface_execute_ollama_fallback(llm_surface):
    """Test LLM execution falls back to Ollama when no cloud keys are set."""
    ollama_response = {"status": "ok", "value": "42", "provider": "ollama", "model": "llama3"}

    with patch.dict("os.environ", {}, clear=False):
        # Ensure no cloud keys leak in from the environment during this test
        import em_cubed.surfaces.llm_surface as mod
        with patch.object(mod.LLMSurface, "_has_cloud_keys", return_value=False):
            with patch.object(llm_surface._ollama, "is_available", new=AsyncMock(return_value=True)):
                with patch.object(llm_surface._ollama, "list_models", new=AsyncMock(return_value=["llama3"])):
                    with patch.object(llm_surface._ollama, "chat", new=AsyncMock(return_value=ollama_response)):
                        result = await llm_surface.execute("What is 6 * 7?")

    assert result["status"] == "ok"
    assert result["value"] == "42"
    assert result.get("provider") == "ollama"


@pytest.mark.asyncio
async def test_llm_surface_error_when_all_unavailable(llm_surface):
    """Test that a clear error is returned when neither cloud nor Ollama is available."""
    import em_cubed.surfaces.llm_surface as mod
    with patch.object(mod.LLMSurface, "_has_cloud_keys", return_value=False):
        with patch.object(llm_surface._ollama, "is_available", new=AsyncMock(return_value=False)):
            result = await llm_surface.execute("Hello")

    assert result["status"] == "error"
    assert "No LLM backend available" in result["message"]
    assert "OPENAI_API_KEY" in result["message"] or "Ollama" in result["message"]


@pytest.mark.asyncio
async def test_llm_surface_timeout(llm_surface):
    """Test LLM surface timeout handling."""
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        with patch("litellm.acompletion") as mock_completion:
            async def delayed_completion(*args, **kwargs):
                await asyncio.sleep(0.2)
                mock_response = MagicMock()
                mock_response.choices = [MagicMock()]
                mock_response.choices[0].message.content = "Delayed"
                return mock_response

            mock_completion.side_effect = delayed_completion
            llm_surface.timeout = 0.05

            result = await llm_surface.execute("This should timeout")

    assert result["status"] == "error"
    assert "timed out" in result["message"]


@pytest.mark.asyncio
async def test_llm_surface_with_context_cloud(llm_surface):
    """Test LLM cloud execution with context dict."""
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        with patch("litellm.acompletion") as mock_acompletion:
            mock_resp = MagicMock()
            mock_resp.choices = [MagicMock()]
            mock_resp.choices[0].message.content = "Paris"
            mock_acompletion.return_value = mock_resp

            result = await llm_surface.execute(
                "What is the capital of France?",
                context={"model": "gpt-3.5-turbo", "temperature": 0.0},
            )

    assert result["status"] == "ok"
    assert result["value"] == "Paris"
    assert result.get("provider") == "litellm"


@pytest.mark.asyncio
async def test_llm_surface_health_with_cloud_key(llm_surface):
    """Health returns True when a cloud key is present."""
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        result = await llm_surface.health()
    assert result is True


@pytest.mark.asyncio
async def test_llm_surface_health_with_ollama(llm_surface):
    """Health returns True when Ollama is reachable and no cloud keys are present."""
    import em_cubed.surfaces.llm_surface as mod
    with patch.object(mod.LLMSurface, "_has_cloud_keys", return_value=False):
        with patch.object(llm_surface._ollama, "is_available", new=AsyncMock(return_value=True)):
            result = await llm_surface.health()
    assert result is True


@pytest.mark.asyncio
async def test_llm_surface_health_when_nothing_available(llm_surface):
    """Health returns False when neither cloud keys nor Ollama are available."""
    import em_cubed.surfaces.llm_surface as mod
    with patch.object(mod.LLMSurface, "_has_cloud_keys", return_value=False):
        with patch.object(llm_surface._ollama, "is_available", new=AsyncMock(return_value=False)):
            result = await llm_surface.health()
    assert result is False