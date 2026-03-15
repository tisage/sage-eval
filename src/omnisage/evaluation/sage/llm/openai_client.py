"""
OpenAI LLM Client

Adapter for OpenAI API (GPT-4.1-mini, etc.)
"""

import os
from typing import List, Optional
import time
from dotenv import load_dotenv

from .base_llm_client import BaseLLMClient, LLMMessage, LLMResponse

# Load environment variables from .env file
load_dotenv()


class OpenAIClient(BaseLLMClient):
    """
    OpenAI API client

    Supports: gpt-4.1-mini, gpt-4-turbo, etc.
    """

    def __init__(
        self,
        model_name: str = "gpt-4.1-mini",
        api_key: Optional[str] = None,
        temperature: float = 0.5,
        max_tokens: int = 1000,
        timeout: int = 30,
        retry_attempts: int = 3,
        retry_delay: float = 1.0,
    ):
        """
        Initialize OpenAI client

        Args:
            model_name: OpenAI model name
            api_key: OpenAI API key (if None, uses OPENAI_API_KEY env var)
            temperature: Generation temperature
            max_tokens: Max tokens to generate
            timeout: Request timeout in seconds
            retry_attempts: Number of retry attempts on failure
            retry_delay: Delay between retries (seconds)
        """
        super().__init__(model_name, api_key, temperature, max_tokens, timeout)

        # Get API key from environment if not provided
        if self.api_key is None:
            self.api_key = os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError(
                    "OpenAI API key not provided and OPENAI_API_KEY env var not set"
                )

        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay

        # Lazy import to avoid dependency at module load
        self._client = None

    def _get_client(self):
        """Lazy initialization of OpenAI client"""
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(
                    api_key=self.api_key,
                    timeout=self.timeout,
                )
            except ImportError:
                raise ImportError(
                    "openai package not installed. Install with: pip install openai"
                )
        return self._client

    def generate(
        self,
        messages: Optional[List[LLMMessage]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
        user_prompt: Optional[str] = None,
    ) -> LLMResponse:
        """
        Generate completion from messages using OpenAI API

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
        """Internal method to call OpenAI API"""
        client = self._get_client()

        # Use provided values or defaults
        temp = temperature if temperature is not None else self.temperature
        max_tok = max_tokens if max_tokens is not None else self.max_tokens

        # Convert messages to OpenAI format
        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        # Determine which parameter to use for max tokens
        # GPT-5 models use max_completion_tokens instead of max_tokens
        use_completion_tokens = any(
            model_prefix in self.model_name.lower()
            for model_prefix in ["gpt-5", "o1", "o3"]
        )

        # Retry logic
        last_exception = None
        for attempt in range(self.retry_attempts):
            try:
                # Build API call parameters
                api_params = {
                    "model": self.model_name,
                    "messages": openai_messages,
                }

                # Some models (o1, o3, gpt-5-mini) don't support temperature parameter
                # Only add temperature for models that support it
                supports_temperature = not any(
                    model_prefix in self.model_name.lower()
                    for model_prefix in ["o1", "o3", "gpt-5-mini"]
                )
                if supports_temperature:
                    api_params["temperature"] = temp

                # Use appropriate max tokens parameter
                if use_completion_tokens:
                    api_params["max_completion_tokens"] = max_tok
                else:
                    api_params["max_tokens"] = max_tok

                response = client.chat.completions.create(**api_params)

                # Extract response
                content = response.choices[0].message.content

                # Extract usage stats
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }

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
                        f"OpenAI API call failed after {self.retry_attempts} attempts: {str(e)}"
                    ) from last_exception

    def validate_api_key(self) -> bool:
        """
        Validate OpenAI API key by making a minimal API call

        Returns:
            True if valid, False otherwise
        """
        try:
            client = self._get_client()

            # Determine which parameter to use
            use_completion_tokens = any(
                model_prefix in self.model_name.lower()
                for model_prefix in ["gpt-5", "o1", "o3"]
            )

            # Build API parameters
            api_params = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": "test"}],
            }

            if use_completion_tokens:
                api_params["max_completion_tokens"] = 1
            else:
                api_params["max_tokens"] = 1

            # Make minimal API call
            response = client.chat.completions.create(**api_params)
            return True
        except Exception:
            return False


# ==================== Convenience Function ====================

def create_openai_client(
    model_name: str = "gpt-4.1-mini",
    api_key: Optional[str] = None,
    temperature: float = 0.5,
    max_tokens: int = 1000,
) -> OpenAIClient:
    """
    Convenience function to create OpenAI client

    Args:
        model_name: OpenAI model name
        api_key: API key (optional, uses env var if None)
        temperature: Generation temperature
        max_tokens: Max tokens

    Returns:
        Configured OpenAIClient
    """
    return OpenAIClient(
        model_name=model_name,
        api_key=api_key,
        temperature=temperature,
        max_tokens=max_tokens,
    )
