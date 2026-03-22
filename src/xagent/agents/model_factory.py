# -*- coding: utf-8 -*-
"""Factory for creating chat models and formatters.

This module provides a unified factory for creating chat model instances
and their corresponding formatters based on configuration.

Supported provider types:
- openai: Uses OpenAIChatModel + OpenAIChatFormatter
- claude: Uses AnthropicChatModel + AnthropicChatFormatter  
- gemini: Uses GeminiChatModel + GeminiChatFormatter
"""

import os
import logging
from typing import Tuple, Union

from agentscope.formatter import (
    OpenAIChatFormatter,
    AnthropicChatFormatter,
    GeminiChatFormatter,
)
from agentscope.model import (
    OpenAIChatModel,
    AnthropicChatModel,
    GeminiChatModel,
)

logger = logging.getLogger(__name__)

# Type aliases for clarity
ChatModel = Union[OpenAIChatModel, AnthropicChatModel, GeminiChatModel]
ChatFormatter = Union[OpenAIChatFormatter, AnthropicChatFormatter, GeminiChatFormatter]


def create_model_and_formatter(provider_type: str = "openai") -> Tuple[ChatModel, ChatFormatter]:
    """Factory method to create model and formatter instances.

    This method creates a chat model and its corresponding formatter based on provider type.
    Each provider type uses its native model and formatter for proper API compatibility,
    especially for features like tool calling.

    Args:
        provider_type: Provider type. Supported values:
            - "openai": OpenAI API (GPT-4, etc.)
            - "claude": Anthropic Claude API
            - "gemini": Google Gemini API

    Returns:
        Tuple of (model_instance, formatter_instance)
        
    Note:
        Configuration is read from environment variables:
        - OpenAI: OPENAI_API_KEY, OPENAI_MODEL, OPENAI_BASE_URL
        - Claude: ANTHROPIC_API_KEY, ANTHROPIC_MODEL, ANTHROPIC_BASE_URL
        - Gemini: GEMINI_API_KEY, GEMINI_MODEL
    """
    logger.info(f"[create_model_and_formatter] provider_type: {provider_type}")
    
    if provider_type == "openai":
        return _create_openai_model_and_formatter()
    elif provider_type == "claude":
        return _create_claude_model_and_formatter()
    elif provider_type == "gemini":
        return _create_gemini_model_and_formatter()
    else:
        # Unknown provider type, default to OpenAI with warning
        logger.warning(f"[create_model_and_formatter] Unknown provider_type '{provider_type}', defaulting to OpenAI")
        return _create_openai_model_and_formatter()


def _create_openai_model_and_formatter() -> Tuple[OpenAIChatModel, OpenAIChatFormatter]:
    """Create OpenAI model and formatter.
    
    Returns:
        Tuple of (OpenAIChatModel, OpenAIChatFormatter)
    """
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o")
    api_key = os.getenv("OPENAI_API_KEY", "")
    base_url = os.getenv("OPENAI_BASE_URL", None)
    
    logger.info(f"[create_model_and_formatter] OpenAI config: model={model_name}, base_url={base_url}")
    
    # Create model instance
    client_kwargs = {"base_url": base_url} if base_url else {}
    # Add custom headers for API-KEY authentication (for custom OpenAI-compatible APIs)
    if api_key:
        client_kwargs["default_headers"] = {"API-KEY": api_key}
    
    model = OpenAIChatModel(
        model_name,
        api_key=api_key,
        stream=True,
        client_kwargs=client_kwargs
    )
    
    # Create formatter instance
    formatter = OpenAIChatFormatter()
    
    return model, formatter


def _create_claude_model_and_formatter() -> Tuple[AnthropicChatModel, AnthropicChatFormatter]:
    """Create Anthropic Claude model and formatter.
    
    Uses AnthropicChatModel for proper tool calling support with Claude API.
    
    Returns:
        Tuple of (AnthropicChatModel, AnthropicChatFormatter)
    """
    model_name = os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    base_url = os.getenv("ANTHROPIC_BASE_URL", None)
    
    logger.info(f"[create_model_and_formatter] Claude config: model={model_name}, base_url={base_url}")
    
    # Create model instance using AnthropicChatModel for proper tool calling support
    client_kwargs = {"base_url": base_url} if base_url else {}
    model = AnthropicChatModel(
        model_name,
        api_key=api_key,
        stream=True,
        client_kwargs=client_kwargs
    )
    
    # Create formatter instance
    formatter = AnthropicChatFormatter()
    
    return model, formatter


def _create_gemini_model_and_formatter() -> Tuple[GeminiChatModel, GeminiChatFormatter]:
    """Create Google Gemini model and formatter.
    
    Uses GeminiChatModel for proper tool calling support with Gemini API.
    
    Returns:
        Tuple of (GeminiChatModel, GeminiChatFormatter)
    """
    model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-pro-latest")
    api_key = os.getenv("GEMINI_API_KEY", "")
    
    logger.info(f"[create_model_and_formatter] Gemini config: model={model_name}")
    
    # Create model instance using GeminiChatModel for proper tool calling support
    # Note: Gemini uses Google's API which doesn't require base_url configuration
    model = GeminiChatModel(
        model_name,
        api_key=api_key,
        stream=True
    )
    
    # Create formatter instance
    formatter = GeminiChatFormatter()
    
    return model, formatter


__all__ = [
    "create_model_and_formatter",
]
