"""
Base LLM Client Interface

Defines the abstract interface for all LLM clients.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class LLMMessage:
    """Single message in a conversation"""
    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class LLMResponse:
    """Response from LLM"""
    content: str
    model: str
    usage: Dict[str, int]  # e.g., {"prompt_tokens": 100, "completion_tokens": 50}
    raw_response: Optional[Any] = None


class BaseLLMClient(ABC):
    """
    Abstract base class for LLM clients

    All LLM providers (OpenAI, Google, etc.) must implement this interface.
    """

    def __init__(
        self,
        model_name: str,
        api_key: Optional[str] = None,
        temperature: float = 0.5,
        max_tokens: int = 1000,
        timeout: int = 30,
    ):
        """
        Initialize LLM client

        Args:
            model_name: Name of the model (e.g., "gpt-4.1-mini")
            api_key: API key (if None, will try to get from environment)
            temperature: Generation temperature (0.0-2.0)
            max_tokens: Maximum tokens to generate
            timeout: Request timeout in seconds
        """
        self.model_name = model_name
        self.api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout

    @abstractmethod
    def generate(
        self,
        messages: List[LLMMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """
        Generate completion from messages

        Args:
            messages: List of conversation messages
            temperature: Override default temperature
            max_tokens: Override default max_tokens

        Returns:
            LLMResponse with generated content

        Raises:
            Exception: If API call fails
        """
        pass

    def generate_from_prompt(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """
        Convenience method: Generate from system + user prompts

        Args:
            system_prompt: System message
            user_prompt: User message
            temperature: Override default temperature
            max_tokens: Override default max_tokens

        Returns:
            LLMResponse
        """
        messages = [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=user_prompt),
        ]
        return self.generate(messages, temperature, max_tokens)

    @abstractmethod
    def validate_api_key(self) -> bool:
        """
        Validate that API key is valid

        Returns:
            True if valid, False otherwise
        """
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model={self.model_name})"
