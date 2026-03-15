# PROJECT_FOLDER/src/omnisage/core/llm_client.py
"""
Simplified LLM client for interfacing with different language model providers.
"""

import os
import asyncio
from typing import Dict, Any
from dotenv import load_dotenv

from omnisage.utils.logger import get_logger

# Load environment variables
load_dotenv()

logger = get_logger(__name__)

class LLMClient:
    """Client for making LLM API calls."""

    def __init__(self, llm_config: Dict[str, Any]):
        self.config = llm_config
        self.provider = llm_config["model_provider"]
        self.model_name = llm_config["model_name"]
        self.base_url = llm_config["base_url"]
        self.max_tokens = llm_config["model_token_size"]

        # Optional: response_format for JSON mode (Mistral, OpenAI, etc.)
        self.response_format = llm_config.get("response_format", None)

        # NEW: Reasoning parameters for different models
        # For GPT-5: reasoning.effort (default: "medium")
        self.reasoning_effort = llm_config.get("reasoning_effort", None)
        # For Gemini 2.5: thinkingBudget (default: 8192 or -1 for dynamic)
        self.thinking_budget = llm_config.get("thinking_budget", None)

        # Get API key from environment
        key_env_var = llm_config["key_value"]
        self.api_key = os.getenv(key_env_var)

        if not self.api_key:
            raise ValueError(f"API key not found in environment variable: {key_env_var}")

        self._client = self._create_client()
    
    def _create_client(self):
        """Create the appropriate client based on provider."""
        if self.provider.lower() in ["openai", "deepseek", "openrouter"]:
            from openai import OpenAI
            return OpenAI(api_key=self.api_key, base_url=self.base_url)
        elif self.provider.lower() == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            return genai
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        """Generate text using the configured LLM."""
        try:
            if self.provider.lower() == "gemini":
                # Combine prompts for Gemini
                full_prompt = f"{system_prompt}\n\n{user_prompt}"
                model = self._client.GenerativeModel(self.model_name)

                # Build generation config
                gen_config = {'max_output_tokens': self.max_tokens}

                # Add thinking_budget if specified (Gemini 2.5)
                if self.thinking_budget is not None:
                    gen_config['thinkingBudget'] = self.thinking_budget
                    logger.info(f"Using thinkingBudget={self.thinking_budget} for Gemini")
                else:
                    # Fallback to temperature if no thinking_budget
                    gen_config['temperature'] = temperature

                response = model.generate_content(full_prompt, generation_config=gen_config)
                return response.text
            elif "gpt-5" in self.model_name:
                # GPT-5 family uses the NEW Responses API
                # Key differences: responses.create(), "developer" role, "input" parameter
                input_messages = [
                    {"role": "developer", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]

                request_params = {
                    "model": self.model_name,
                    "input": input_messages,
                    "max_output_tokens": self.max_tokens,
                }

                # Add reasoning effort if specified
                if self.reasoning_effort:
                    request_params["reasoning"] = {"effort": self.reasoning_effort}
                    logger.info(f"Using reasoning.effort={self.reasoning_effort} for GPT-5")

                response = self._client.responses.create(**request_params)
                return response.output_text
            else:
                # OpenAI-compatible API (OpenAI GPT-4/3, DeepSeek, OpenRouter/Mistral)
                # Build request parameters
                request_params = {
                    "model": self.model_name,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                }

                # Handle different model families
                if "gpt-4" in self.model_name or "gpt-3" in self.model_name:
                    # Older models support temperature
                    request_params["temperature"] = temperature
                else:
                    # Other OpenAI-compatible models
                    request_params["temperature"] = temperature

                # Use max_completion_tokens for newer OpenAI models, max_tokens for older ones
                if "gpt-4" in self.model_name:
                    request_params["max_completion_tokens"] = self.max_tokens
                else:
                    request_params["max_tokens"] = self.max_tokens

                # Add response_format if specified (for JSON mode)
                if self.response_format:
                    request_params["response_format"] = self.response_format

                response = self._client.chat.completions.create(**request_params)
                return response.choices[0].message.content

        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}")
            raise

    def generate_with_messages(self, messages: list, temperature: float = 0.7) -> str:
        """
        Generate text using multi-turn conversation format.

        Args:
            messages: List of message dicts with 'role' and 'content'
                     Example: [{"role": "system", "content": "..."},
                              {"role": "user", "content": "..."},
                              {"role": "assistant", "content": "..."}]
            temperature: Generation temperature

        Returns:
            Generated text response
        """
        try:
            if self.provider.lower() == "gemini":
                # Gemini: combine all messages into a single prompt
                full_prompt = "\n\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
                model = self._client.GenerativeModel(self.model_name)

                # Build generation config
                gen_config = {'max_output_tokens': self.max_tokens}

                # Add thinking_budget if specified (Gemini 2.5)
                if self.thinking_budget is not None:
                    gen_config['thinkingBudget'] = self.thinking_budget
                    logger.info(f"Using thinkingBudget={self.thinking_budget} for Gemini")
                else:
                    # Fallback to temperature if no thinking_budget
                    gen_config['temperature'] = temperature

                response = model.generate_content(full_prompt, generation_config=gen_config)
                return response.text
            elif "gpt-5" in self.model_name:
                # GPT-5 family uses the NEW Responses API
                # Convert "system" role to "developer" role for GPT-5
                input_messages = []
                for msg in messages:
                    role = msg['role']
                    if role == 'system':
                        role = 'developer'
                    input_messages.append({"role": role, "content": msg['content']})

                request_params = {
                    "model": self.model_name,
                    "input": input_messages,
                    "max_output_tokens": self.max_tokens,
                }

                # Add reasoning effort if specified
                if self.reasoning_effort:
                    request_params["reasoning"] = {"effort": self.reasoning_effort}
                    logger.info(f"Using reasoning.effort={self.reasoning_effort} for GPT-5")

                response = self._client.responses.create(**request_params)
                return response.output_text
            else:
                # OpenAI-compatible API (supports messages natively)
                request_params = {
                    "model": self.model_name,
                    "messages": messages,
                }

                # Handle different model families
                if "gpt-4" in self.model_name or "gpt-3" in self.model_name:
                    # Older models support temperature
                    request_params["temperature"] = temperature
                else:
                    # Other OpenAI-compatible models
                    request_params["temperature"] = temperature

                # Use max_completion_tokens for newer OpenAI models, max_tokens for older ones
                if "gpt-4" in self.model_name:
                    request_params["max_completion_tokens"] = self.max_tokens
                else:
                    request_params["max_tokens"] = self.max_tokens

                # Add response_format if specified
                if self.response_format:
                    request_params["response_format"] = self.response_format

                response = self._client.chat.completions.create(**request_params)
                return response.choices[0].message.content

        except Exception as e:
            logger.error(f"LLM generation (multi-turn) failed: {str(e)}")
            raise

    async def generate_async(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        """
        Async version of generate method.

        For providers without native async support, runs in thread pool.
        """
        # Run the sync version in a thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.generate,
            system_prompt,
            user_prompt,
            temperature
        )