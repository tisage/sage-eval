"""
LLM Module for SAGE Framework

Includes:
- Judge系统 (Layer 4-6评审器)
- LLM Client适配器 (OpenAI, Google, Mock)
"""

# Judge system
from .base_judge import BaseJudge, JSONOutputParser, create_rubric_prompt, format_output_template

# LLM Clients (lazy import to avoid dependencies)
def get_openai_client():
    """Lazy import OpenAI client"""
    from .openai_client import OpenAIClient, create_openai_client
    return OpenAIClient, create_openai_client

def get_google_client():
    """Lazy import Google client"""
    from .google_client import GoogleClient, create_google_client
    return GoogleClient, create_google_client

def get_mock_client():
    """Lazy import Mock client"""
    from .mock_llm_client import MockLLMClient
    return MockLLMClient

def get_client_factory():
    """Lazy import LLM client factory"""
    from .client_factory import LLMClientFactory, create_llm_client
    return LLMClientFactory, create_llm_client

__all__ = [
    # Judge system
    "BaseJudge",
    "JSONOutputParser",
    "create_rubric_prompt",
    "format_output_template",
    # Client accessors (lazy)
    "get_openai_client",
    "get_google_client",
    "get_mock_client",
    "get_client_factory",
]
