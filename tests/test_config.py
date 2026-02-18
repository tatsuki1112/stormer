"""Tests for configuration management."""

import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from stormer.config import Config, get_config


class TestConfig:
    """Test suite for Config class."""

    def test_config_from_env_with_valid_keys(self):
        """Test that Config loads successfully with valid API keys."""
        with patch.dict(
            os.environ,
            {
                "OPENROUTER_API_KEY": "test-openrouter-key",
                "TAVILY_API_KEY": "test-tavily-key",
            },
            clear=True,
        ):
            config = Config.from_env()

            assert config.openrouter_api_key.get_secret_value() == "test-openrouter-key"
            assert config.tavily_api_key.get_secret_value() == "test-tavily-key"
            assert config.openrouter_model == "anthropic/claude-3-5-sonnet"
            assert config.openrouter_base_url == "https://openrouter.ai/api/v1"

    def test_config_from_env_with_missing_openrouter_key(self):
        """Test that Config raises error when OpenRouter API key is missing."""
        with patch.dict(
            os.environ,
            {
                "TAVILY_API_KEY": "test-tavily-key",
            },
            clear=True,
        ):
            with pytest.raises(ValidationError) as exc_info:
                Config.from_env()

            # Pydantic raises validation error for None/missing SecretStr
            assert "openrouter_api_key" in str(exc_info.value).lower()

    def test_config_from_env_with_missing_tavily_key(self):
        """Test that Config raises error when Tavily API key is missing."""
        with patch.dict(
            os.environ,
            {
                "OPENROUTER_API_KEY": "test-openrouter-key",
            },
            clear=True,
        ):
            with pytest.raises(ValidationError) as exc_info:
                Config.from_env()

            # Pydantic raises validation error for None/missing SecretStr
            assert "tavily_api_key" in str(exc_info.value).lower()

    def test_config_from_env_with_empty_keys(self):
        """Test that Config raises error when API keys are empty strings."""
        with patch.dict(
            os.environ,
            {
                "OPENROUTER_API_KEY": "",
                "TAVILY_API_KEY": "",
            },
            clear=True,
        ):
            with pytest.raises(ValidationError) as exc_info:
                Config.from_env()

            assert "API key cannot be empty" in str(exc_info.value)

    def test_config_with_custom_model(self):
        """Test that Config accepts custom model configuration."""
        with patch.dict(
            os.environ,
            {
                "OPENROUTER_API_KEY": "test-openrouter-key",
                "TAVILY_API_KEY": "test-tavily-key",
            },
            clear=True,
        ):
            config = Config(
                openrouter_api_key="test-key",
                tavily_api_key="test-key",
                openrouter_model="custom/model-name",
            )

            assert config.openrouter_model == "custom/model-name"

    def test_get_config_convenience_function(self):
        """Test the get_config convenience function."""
        with patch.dict(
            os.environ,
            {
                "OPENROUTER_API_KEY": "test-openrouter-key",
                "TAVILY_API_KEY": "test-tavily-key",
            },
            clear=True,
        ):
            config = get_config()

            assert isinstance(config, Config)
            assert config.openrouter_api_key.get_secret_value() == "test-openrouter-key"
            assert config.tavily_api_key.get_secret_value() == "test-tavily-key"
