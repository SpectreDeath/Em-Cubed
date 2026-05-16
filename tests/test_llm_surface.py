"""Tests for LLM surface implementation."""

import asyncio
import pytest
from unittest.mock import patch, MagicMock
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
    """Test that LLMSurface reports available when litellm is installed."""
    surface = LLMSurface()
    # Should be available since we installed litellm
    assert surface.available is True


def test_llm_surface_extract_tags():
    """Test tag extraction returns empty list for LLM surface."""
    surface = LLMSurface()
    assert surface.extract_tags("any prompt") == []
    assert surface.extract_tags("") == []
    assert surface.extract_tags(None) == []


@pytest.mark.asyncio
async def test_llm_surface_execute_mock_response(llm_surface):
    """Test LLM execution returns mock response when no API keys."""
    result = await llm_surface.execute("Explain AI")
    
    assert result["status"] == "ok"
    assert "[MOCK LLM RESPONSE]" in result["value"]
    assert "Explain AI" in result["value"]


@pytest.mark.asyncio
async def test_llm_surface_timeout(llm_surface):
    """Test LLM surface timeout handling."""
    # Patch to simulate having API keys available so we go to the real LLM path
    with patch.object(llm_surface, '_check_availability', return_value=True):
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            with patch('litellm.acompletion') as mock_completion:
                # Make the mock completion take longer than the timeout
                async def delayed_completion(*args, **kwargs):
                    await asyncio.sleep(0.1)  # 100ms delay
                    # Return a mock response
                    mock_response = MagicMock()
                    mock_response.choices = [MagicMock()]
                    mock_response.choices[0].message.content = "Delayed response"
                    return mock_response
                
                mock_completion.side_effect = delayed_completion
                
                # Set a very short timeout (50ms) to ensure timeout occurs
                llm_surface.timeout = 0.05
                
                result = await llm_surface.execute("This is a test prompt that should timeout")
                
                # Should timeout and return error status
                assert result["status"] == "error"
                assert "Execution timed out" in result["message"]


def test_llm_surface_health(llm_surface):
    """Test health check."""
    # Health is an async method, so we need to await it
    import asyncio
    health_result = asyncio.run(llm_surface.health())
    assert health_result is True  # Should be healthy when litellm available


@pytest.mark.asyncio
async def test_llm_surface_with_context(llm_surface):
    """Test LLM execution with context."""
    result = await llm_surface.execute(
        "What is the capital of France?",
        context={"task": "question_answering", "language": "english"}
    )
    
    assert result["status"] == "ok"
    assert "[MOCK LLM RESPONSE]" in result["value"]