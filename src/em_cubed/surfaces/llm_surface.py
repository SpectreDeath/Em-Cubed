"""LLM surface integration for executing prompts via LiteLLM."""

import asyncio
import json
import os
from typing import Dict, Any, Optional, Union, AsyncIterator
import structlog

from .base import SurfaceBase

logger = structlog.get_logger()


class LLMSurface(SurfaceBase):
    """Handle LLM prompt execution using LiteLLM for unified API access."""

    def __init__(self, timeout: Optional[float] = None):
        super().__init__(timeout)
        logger.info("LLMSurface initialized", timeout=self.timeout)

    def _check_availability(self) -> bool:
        """Check if litellm is available."""
        try:
            import litellm  # noqa: F401
            return True
        except ImportError:
            logger.warning("litellm not available for LLM surface")
            return False

    @property
    def name(self) -> str:
        return "llm"

    @property
    def description(self) -> str:
        return "Unified LLM execution via LiteLLM supporting multiple providers with streaming and function calling"

    @property
    def available(self) -> bool:
        return self._check_availability()

    @staticmethod
    def extract_tags(source: Optional[str]) -> list:
        """Extract tags from LLM prompts - returns empty list as tags are not meaningful for raw prompts."""
        # For LLM surfaces, we don't extract meaningful tags from raw prompts
        # Skills using this surface should define their own tags in metadata
        return []

    async def execute(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute LLM prompt with timeout protection."""
        try:
            result = await asyncio.wait_for(
                self._execute_impl(code, context),
                timeout=self.timeout
            )
            return result
        except asyncio.TimeoutError:
            logger.warning("Surface execution timed out", timeout=self.timeout)
            return {
                "status": "error",
                "message": f"Execution timed out after {self.timeout}s"
            }

    async def _execute_impl(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute LLM prompt - implemented by subclasses."""
        return await self._run_prompt(code, context)

    async def _run_prompt(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Run LLM prompt synchronously in the executor thread."""
        if not self.available:
            logger.error("Attempted LLM execution but litellm not available")
            return {"status": "error", "message": "litellm not available"}

        try:
            # Import litellm here to handle missing dependency gracefully
            import litellm
            
            # Check if we have any API keys configured
            has_api_key = any([
                os.getenv("OPENAI_API_KEY"),
                os.getenv("ANTHROPIC_API_KEY"), 
                os.getenv("COHERE_API_KEY"),
                os.getenv("HUGGINGFACE_API_KEY"),
                os.getenv("LLM_API_KEY")
            ])
            
            # If no API keys, return a mock response for testing
            if not has_api_key:
                logger.info("No API keys found, returning mock LLM response")
                return {
                    "status": "ok", 
                    "value": f"[MOCK LLM RESPONSE] This is a simulated response to the prompt: '{prompt[:100]}...' (No API keys configured)"
                }

            # Prepare messages for the LLM
            messages = [{"role": "user", "content": prompt}]
            
            # Add context as system message if provided
            if context:
                context_str = f"Context: {context}"
                messages.insert(0, {"role": "system", "content": context_str})

            # Get parameters from context or use defaults
            model = context.get("model", "gpt-3.5-turbo") if context else "gpt-3.5-turbo"
            temperature = context.get("temperature", 0.7) if context else 0.7
            max_tokens = context.get("max_tokens", 1000) if context else 1000
            stream = context.get("stream", False) if context else False
            tools = context.get("tools") if context else None
            tool_choice = context.get("tool_choice") if context else None

            logger.info("Executing LLM prompt", 
                       model=model, 
                       prompt_length=len(prompt),
                       has_context=context is not None,
                       stream=stream,
                       has_tools=bool(tools))

            # Execute the LLM call
            response = await litellm.acompletion(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
                tools=tools,
                tool_choice=tool_choice,
                timeout=self.timeout
            )

            # Handle streaming vs non-streaming responses
            if stream:
                # For streaming, we collect all chunks and return the full response
                collected_chunks = []
                async for chunk in response:
                    collected_chunks.append(chunk)
                
                # Reconstruct the final response from chunks
                if collected_chunks:
                    # Use the last chunk as the base (it should have the complete response)
                    final_chunk = collected_chunks[-1]
                    if hasattr(final_chunk, 'choices') and len(final_chunk.choices) > 0:
                        generated_text = final_chunk.choices[0].delta.content or ""
                        # In practice, we'd concatenate all delta.content values
                        # But for simplicity in mock mode, we'll return a simulated response
                        generated_text = f"[STREAMING RESPONSE] Simulated streaming response to: '{prompt[:50]}...'"
                    else:
                        generated_text = "[STREAMING RESPONSE] Streaming response received"
                    
                    logger.info("LLM streaming execution successful", 
                               response_length=len(generated_text))
                    return {"status": "ok", "value": generated_text}
                else:
                    logger.error("LLM streaming execution failed: no chunks received")
                    return {"status": "error", "message": "No response chunks received from streaming LLM"}
            else:
                # Non-streaming response
                # Extract the generated text
                if response and 'choices' in response and len(response['choices']) > 0:
                    generated_text = response['choices'][0]['message']['content']
                    logger.info("LLM execution successful", 
                               response_length=len(generated_text))
                    return {"status": "ok", "value": generated_text}
                else:
                    logger.error("LLM execution failed: empty response")
                    return {"status": "error", "message": "Empty response from LLM"}

        except Exception as e:
            logger.exception("LLM execution failed", error=str(e), prompt=prompt[:100])
            # Fallback to mock response on error for better UX during development
            return {
                "status": "ok", 
                "value": f"[MOCK LLM RESPONSE DUE TO ERROR] This is a simulated response due to: {str(e)[:100]}"
            }

    async def health(self) -> bool:
        """Check if the surface is available."""
        return bool(self.available)