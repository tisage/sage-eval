"""
LLM Client Factory

Creates LLM clients from configuration.
"""

from typing import Dict, Any, Optional
from pathlib import Path

from .base_llm_client import BaseLLMClient
from .mock_llm_client import MockLLMClient


class LLMClientFactory:
    """
    Factory for creating LLM clients from configuration

    Usage:
        # From config file
        factory = LLMClientFactory.from_config("config/llm_models.yaml")
        client = factory.create_client("gpt-4.1-mini")

        # Direct creation
        factory = LLMClientFactory()
        client = factory.create_openai_client("gpt-4.1-mini")
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize factory

        Args:
            config: Optional configuration dict from YAML
        """
        self.config = config or {}

    @classmethod
    def from_config(cls, config_path: str) -> "LLMClientFactory":
        """
        Create factory from YAML config file

        Args:
            config_path: Path to llm_models.yaml

        Returns:
            Configured LLMClientFactory
        """
        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return cls(config)

    def create_client(
        self,
        model_name: str,
        mode: str = "production",
        **kwargs
    ) -> BaseLLMClient:
        """
        Create LLM client for a given model

        Args:
            model_name: Model name (e.g., "gpt-4.1-mini")
            mode: "development" or "production"
            **kwargs: Override parameters

        Returns:
            BaseLLMClient instance

        Raises:
            ValueError: If model not found or unsupported provider
        """
        # Development mode: use Mock LLM
        if mode == "development":
            dev_config = self.config.get("development", {})
            if dev_config.get("use_mock", True):
                return MockLLMClient(
                    deterministic=dev_config.get("mock_deterministic", True)
                )

        # Production mode: find model config
        prod_config = self.config.get("production", {})
        models = prod_config.get("models", [])

        # Find model in config
        model_config = None
        for model in models:
            if model.get("model_name") == model_name:
                model_config = model
                break

        if model_config is None:
            raise ValueError(
                f"Model '{model_name}' not found in configuration. "
                f"Available models: {[m.get('model_name') for m in models]}"
            )

        # Extract provider
        provider = model_config.get("provider")
        if not provider:
            raise ValueError(f"No provider specified for model '{model_name}'")

        # Create client based on provider
        if provider == "openai":
            return self.create_openai_client(model_name, **kwargs)
        elif provider == "google":
            return self.create_google_client(model_name, **kwargs)
        elif provider == "openrouter":
            return self.create_openrouter_client(model_name, **kwargs)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def create_openai_client(
        self,
        model_name: str = "gpt-4.1-mini",
        api_key: Optional[str] = None,
        temperature: float = 0.5,
        max_tokens: int = 1000,
        **kwargs
    ) -> BaseLLMClient:
        """
        Create OpenAI client

        Args:
            model_name: OpenAI model name
            api_key: API key (optional)
            temperature: Generation temperature
            max_tokens: Max tokens
            **kwargs: Additional parameters

        Returns:
            OpenAIClient instance
        """
        from .openai_client import OpenAIClient
        return OpenAIClient(
            model_name=model_name,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

    def create_google_client(
        self,
        model_name: str = "gemini-2.5-flash-lite",
        api_key: Optional[str] = None,
        temperature: float = 0.5,
        max_tokens: int = 1000,
        **kwargs
    ) -> BaseLLMClient:
        """
        Create Google Gemini client

        Args:
            model_name: Gemini model name
            api_key: API key (optional)
            temperature: Generation temperature
            max_tokens: Max tokens
            **kwargs: Additional parameters

        Returns:
            GoogleClient instance
        """
        from .google_client import GoogleClient
        return GoogleClient(
            model_name=model_name,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

    def create_openrouter_client(
        self,
        model_name: str = "google/gemini-2.0-flash-exp:free",
        api_key: Optional[str] = None,
        temperature: float = 0.5,
        max_tokens: int = 1000,
        **kwargs
    ) -> BaseLLMClient:
        """
        Create OpenRouter client (unified access to multiple providers)

        Args:
            model_name: OpenRouter model identifier
                Examples:
                - "google/gemini-2.0-flash-exp:free"
                - "anthropic/claude-3-haiku"
                - "openai/gpt-4o-mini"
            api_key: API key (optional)
            temperature: Generation temperature
            max_tokens: Max tokens
            **kwargs: Additional parameters

        Returns:
            OpenRouterClient instance
        """
        from .openrouter_client import OpenRouterClient
        return OpenRouterClient(
            model_name=model_name,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

    def create_mock_client(
        self,
        deterministic: bool = True
    ) -> BaseLLMClient:
        """
        Create Mock LLM client (for testing)

        Args:
            deterministic: Use deterministic responses

        Returns:
            MockLLMClient instance
        """
        return MockLLMClient(deterministic=deterministic)

    def get_layer_client(
        self,
        layer_num: int,
        mode: str = "production"
    ) -> BaseLLMClient:
        """
        Get LLM client for a specific layer based on config

        Args:
            layer_num: Layer number (4, 5, or 6)
            mode: "development" or "production"

        Returns:
            BaseLLMClient for that layer

        Raises:
            ValueError: If layer doesn't use LLM or not configured
        """
        if layer_num not in [4, 5, 6]:
            raise ValueError(f"Layer {layer_num} does not use LLM evaluation")

        # Development mode: return Mock
        if mode == "development":
            return self.create_mock_client()

        # Production mode: get from layer assignment
        layer_assignment = self.config.get("layer_assignment", {})
        layer_key = f"layer{layer_num}_" + ["cultural", "emotional", "existential"][layer_num - 4]

        layer_config = layer_assignment.get(layer_key, {})
        primary_model = layer_config.get("primary_model")

        if not primary_model:
            raise ValueError(
                f"No primary model configured for {layer_key}. "
                "Check llm_models.yaml layer_assignment section."
            )

        # Extract layer-specific parameters (temperature, max_tokens, response_format, etc.)
        layer_params = {}
        if "temperature" in layer_config:
            layer_params["temperature"] = layer_config["temperature"]
        if "max_tokens" in layer_config:
            layer_params["max_tokens"] = layer_config["max_tokens"]
        if "response_format" in layer_config:
            layer_params["response_format"] = layer_config["response_format"]

        return self.create_client(primary_model, mode="production", **layer_params)


# ==================== Convenience Functions ====================

def create_llm_client(
    model_name: str,
    config_path: Optional[str] = None,
    mode: str = "production",
    **kwargs
) -> BaseLLMClient:
    """
    Convenience function: Create LLM client

    Args:
        model_name: Model name
        config_path: Optional path to config file
        mode: "development" or "production"
        **kwargs: Additional parameters

    Returns:
        BaseLLMClient instance
    """
    if config_path:
        factory = LLMClientFactory.from_config(config_path)
        return factory.create_client(model_name, mode, **kwargs)
    else:
        factory = LLMClientFactory()
        return factory.create_client(model_name, mode, **kwargs)
