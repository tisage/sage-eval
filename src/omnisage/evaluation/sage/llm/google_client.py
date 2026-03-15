"""
Google Gemini LLM Client

Adapter for Google Gemini API (gemini-2.5-flash-lite, etc.)
"""

import os
from typing import List, Optional
import time

from .base_llm_client import BaseLLMClient, LLMMessage, LLMResponse


class GoogleClient(BaseLLMClient):
    """
    Google Gemini API client

    Supports: gemini-2.5-flash-lite, gemini-pro, etc.
    """

    def __init__(
        self,
        model_name: str = "gemini-2.5-flash-lite",
        api_key: Optional[str] = None,
        temperature: float = 0.5,
        max_tokens: int = 1000,
        timeout: int = 30,
        retry_attempts: int = 3,
        retry_delay: float = 1.0,
    ):
        """
        Initialize Google Gemini client

        Args:
            model_name: Gemini model name
            api_key: Google API key (if None, uses GOOGLE_API_KEY env var)
            temperature: Generation temperature
            max_tokens: Max tokens to generate
            timeout: Request timeout in seconds
            retry_attempts: Number of retry attempts on failure
            retry_delay: Delay between retries (seconds)
        """
        super().__init__(model_name, api_key, temperature, max_tokens, timeout)

        # Get API key from environment if not provided
        if self.api_key is None:
            self.api_key = os.getenv("GOOGLE_API_KEY")
            if not self.api_key:
                raise ValueError(
                    "Google API key not provided and GOOGLE_API_KEY env var not set"
                )

        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay

        # Lazy import to avoid dependency at module load
        self._genai = None
        self._model = None

    def _get_model(self):
        """Lazy initialization of Google Gemini model"""
        if self._model is None:
            try:
                import google.generativeai as genai
                self._genai = genai

                # Configure API key
                genai.configure(api_key=self.api_key)

                # Initialize model
                self._model = genai.GenerativeModel(self.model_name)

            except ImportError:
                raise ImportError(
                    "google-generativeai package not installed. "
                    "Install with: pip install google-generativeai"
                )
        return self._model

    def generate(
        self,
        messages: Optional[List[LLMMessage]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
        user_prompt: Optional[str] = None,
    ) -> LLMResponse:
        """
        Generate completion from messages using Google Gemini API

        Supports two calling styles:
        1. generate(messages=[...])  # New style
        2. generate(system_prompt="...", user_prompt="...")  # Legacy style for compatibility

        Args:
            messages: List of conversation messages (new style)
            temperature: Override default temperature
            max_tokens: Override default max_tokens
            system_prompt: System prompt (legacy style)
            user_prompt: User prompt (legacy style)

        Returns:
            LLMResponse with generated content (or str for legacy style)

        Raises:
            Exception: If API call fails after all retries
        """
        # Handle legacy calling style (for compatibility with Judge classes)
        if system_prompt is not None or user_prompt is not None:
            if messages is not None:
                raise ValueError("Cannot specify both 'messages' and 'system_prompt/user_prompt'")

            # Convert to messages format
            messages = []
            if system_prompt:
                messages.append(LLMMessage(role="system", content=system_prompt))
            if user_prompt:
                messages.append(LLMMessage(role="user", content=user_prompt))

            # Call API and return only content string for legacy compatibility
            response = self._call_api(messages, temperature, max_tokens)
            return response.content

        # New style: messages parameter
        if messages is None:
            raise ValueError("Must provide either 'messages' or 'system_prompt/user_prompt'")

        return self._call_api(messages, temperature, max_tokens)

    def _call_api(
        self,
        messages: List[LLMMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """Internal method to call Google Gemini API"""
        model = self._get_model()

        # Use provided values or defaults
        temp = temperature if temperature is not None else self.temperature
        max_tok = max_tokens if max_tokens is not None else self.max_tokens

        # Convert messages to Gemini format
        # Gemini uses a different format: combine system + user into single prompt
        prompt_parts = []
        for msg in messages:
            if msg.role == "system":
                prompt_parts.append(f"System: {msg.content}")
            elif msg.role == "user":
                prompt_parts.append(f"User: {msg.content}")
            elif msg.role == "assistant":
                prompt_parts.append(f"Assistant: {msg.content}")

        full_prompt = "\n\n".join(prompt_parts)

        # Generation config
        generation_config = {
            "temperature": temp,
            "max_output_tokens": max_tok,
        }

        # Retry logic
        last_exception = None
        for attempt in range(self.retry_attempts):
            try:
                response = model.generate_content(
                    full_prompt,
                    generation_config=generation_config,
                )

                # Extract content
                content = response.text

                # Estimate usage (Gemini doesn't always provide token counts)
                usage = {
                    "prompt_tokens": len(full_prompt.split()) * 2,  # Rough estimate
                    "completion_tokens": len(content.split()) * 2,  # Rough estimate
                    "total_tokens": (len(full_prompt.split()) + len(content.split())) * 2,
                }

                # Try to get actual usage if available
                try:
                    if hasattr(response, 'usage_metadata'):
                        usage = {
                            "prompt_tokens": response.usage_metadata.prompt_token_count,
                            "completion_tokens": response.usage_metadata.candidates_token_count,
                            "total_tokens": response.usage_metadata.total_token_count,
                        }
                except:
                    pass  # Use estimates

                return LLMResponse(
                    content=content,
                    model=self.model_name,
                    usage=usage,
                    raw_response=response,
                )

            except Exception as e:
                last_exception = e
                if attempt < self.retry_attempts - 1:
                    # Exponential backoff
                    wait_time = self.retry_delay * (2 ** attempt)
                    time.sleep(wait_time)
                    continue
                else:
                    # Last attempt failed
                    raise Exception(
                        f"Google Gemini API call failed after {self.retry_attempts} attempts: {str(e)}"
                    ) from last_exception

    def validate_api_key(self) -> bool:
        """
        Validate Google API key by making a minimal API call

        Returns:
            True if valid, False otherwise
        """
        try:
            model = self._get_model()
            # Make minimal API call
            response = model.generate_content(
                "test",
                generation_config={"max_output_tokens": 1},
            )
            return True
        except Exception:
            return False


# ==================== Convenience Function ====================

def create_google_client(
    model_name: str = "gemini-2.5-flash-lite",
    api_key: Optional[str] = None,
    temperature: float = 0.5,
    max_tokens: int = 1000,
) -> GoogleClient:
    """
    Convenience function to create Google Gemini client

    Args:
        model_name: Gemini model name
        api_key: API key (optional, uses env var if None)
        temperature: Generation temperature
        max_tokens: Max tokens

    Returns:
        Configured GoogleClient
    """
    return GoogleClient(
        model_name=model_name,
        api_key=api_key,
        temperature=temperature,
        max_tokens=max_tokens,
    )
