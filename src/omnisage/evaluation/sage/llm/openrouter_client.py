"""
OpenRouter LLM Client

Adapter for OpenRouter API - unified access to multiple LLM providers
Supports: Gemini, Claude, GPT, etc.
"""

import os
from typing import List, Optional
import time

from .base_llm_client import BaseLLMClient, LLMMessage, LLMResponse


class OpenRouterClient(BaseLLMClient):
    """
    OpenRouter API client

    Provides unified access to multiple LLM providers through OpenRouter.
    Supports: Google Gemini, Anthropic Claude, OpenAI GPT, and many more.

    API Docs: https://openrouter.ai/docs
    """

    def __init__(
        self,
        model_name: str = "google/gemini-2.0-flash-exp:free",
        api_key: Optional[str] = None,
        temperature: float = 0.5,
        max_tokens: int = 1000,
        timeout: int = 30,
        retry_attempts: int = 3,
        retry_delay: float = 1.0,
        site_url: Optional[str] = None,
        app_name: Optional[str] = None,
        response_format: Optional[dict] = None,
    ):
        """
        Initialize OpenRouter client

        Args:
            model_name: OpenRouter model identifier
                Examples:
                - "google/gemini-2.0-flash-exp:free"
                - "google/gemini-pro"
                - "anthropic/claude-3-haiku"
                - "openai/gpt-4o-mini"
            api_key: OpenRouter API key (if None, uses OPENROUTER_API_KEY env var)
            temperature: Generation temperature
            max_tokens: Max tokens to generate
            timeout: Request timeout in seconds
            retry_attempts: Number of retry attempts on failure
            retry_delay: Delay between retries (seconds)
            site_url: Optional site URL for OpenRouter rankings
            app_name: Optional app name for OpenRouter rankings
        """
        super().__init__(model_name, api_key, temperature, max_tokens, timeout)

        # Get API key from environment if not provided
        if self.api_key is None:
            self.api_key = os.getenv("OPENROUTER_API_KEY")
            if not self.api_key:
                raise ValueError(
                    "OpenRouter API key not provided and OPENROUTER_API_KEY env var not set"
                )

        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.site_url = site_url or os.getenv("OPENROUTER_SITE_URL", "")
        self.app_name = app_name or os.getenv("OPENROUTER_APP_NAME", "SAGE Framework")

        # Response format for structured output (e.g., JSON mode for Mistral)
        self.response_format = response_format

        # OpenRouter API endpoint
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"

        # Lazy import to avoid dependency at module load
        self._requests = None

    def _get_requests(self):
        """Lazy initialization of requests library"""
        if self._requests is None:
            try:
                import requests
                self._requests = requests
            except ImportError:
                raise ImportError(
                    "requests package not installed. Install with: pip install requests"
                )
        return self._requests

    def generate(
        self,
        messages: Optional[List[LLMMessage]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
        user_prompt: Optional[str] = None,
    ) -> LLMResponse:
        """
        Generate completion using OpenRouter API

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
        """Internal method to call OpenRouter API"""
        requests = self._get_requests()

        # Use provided values or defaults
        temp = temperature if temperature is not None else self.temperature
        max_tok = max_tokens if max_tokens is not None else self.max_tokens

        # Convert messages to OpenAI-compatible format (OpenRouter uses same format)
        api_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        # Request headers
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # Optional headers for OpenRouter rankings
        if self.site_url:
            headers["HTTP-Referer"] = self.site_url
        if self.app_name:
            headers["X-Title"] = self.app_name

        # Request body
        body = {
            "model": self.model_name,
            "messages": api_messages,
            "temperature": temp,
            "max_tokens": max_tok,
        }

        # Add response_format if specified (for JSON mode)
        if self.response_format:
            body["response_format"] = self.response_format

        # Retry logic
        last_exception = None
        for attempt in range(self.retry_attempts):
            try:
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=body,
                    timeout=self.timeout,
                )

                # Check for HTTP errors
                response.raise_for_status()

                # Parse response
                data = response.json()

                # Extract content
                content = data["choices"][0]["message"]["content"]

                # Extract usage stats
                usage_data = data.get("usage", {})
                usage = {
                    "prompt_tokens": usage_data.get("prompt_tokens", 0),
                    "completion_tokens": usage_data.get("completion_tokens", 0),
                    "total_tokens": usage_data.get("total_tokens", 0),
                }

                return LLMResponse(
                    content=content,
                    model=self.model_name,
                    usage=usage,
                    raw_response=data,
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
                        f"OpenRouter API call failed after {self.retry_attempts} attempts: {str(e)}"
                    ) from last_exception

    def validate_api_key(self) -> bool:
        """
        Validate OpenRouter API key by making a minimal API call

        Returns:
            True if valid, False otherwise
        """
        try:
            # Make minimal API call
            test_messages = [LLMMessage(role="user", content="test")]
            self._call_api(test_messages, max_tokens=1)
            return True
        except Exception:
            return False


# ==================== Convenience Function ====================

def create_openrouter_client(
    model_name: str = "google/gemini-2.0-flash-exp:free",
    api_key: Optional[str] = None,
    temperature: float = 0.5,
    max_tokens: int = 1000,
) -> OpenRouterClient:
    """
    Convenience function to create OpenRouter client

    Args:
        model_name: OpenRouter model identifier
        api_key: API key (optional, uses env var if None)
        temperature: Generation temperature
        max_tokens: Max tokens

    Returns:
        Configured OpenRouterClient

    Examples:
        # Gemini via OpenRouter
        client = create_openrouter_client("google/gemini-2.0-flash-exp:free")

        # Claude via OpenRouter
        client = create_openrouter_client("anthropic/claude-3-haiku")

        # GPT via OpenRouter
        client = create_openrouter_client("openai/gpt-4o-mini")
    """
    return OpenRouterClient(
        model_name=model_name,
        api_key=api_key,
        temperature=temperature,
        max_tokens=max_tokens,
    )
