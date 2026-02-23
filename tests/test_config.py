"""Tests for configuration management."""

import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from stormer.config import Config, get_config
from stormer.connectivity.openrouter import OpenRouterHealthChecker
from stormer.connectivity.tavily import TavilyHealthChecker


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

    def test_config_has_tavily_base_url(self):
        """Test that Config has tavily_base_url field with correct default."""
        with patch.dict(
            os.environ,
            {
                "OPENROUTER_API_KEY": "test-openrouter-key",
                "TAVILY_API_KEY": "test-tavily-key",
            },
            clear=True,
        ):
            config = Config.from_env()

            assert config.tavily_base_url == "https://api.tavily.com"

    def test_config_with_custom_tavily_base_url(self):
        """Test that Config accepts custom tavily_base_url."""
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
                tavily_base_url="https://custom.tavily.com",
            )

            assert config.tavily_base_url == "https://custom.tavily.com"

    def test_create_openrouter_checker(self):
        """Test that create_openrouter_checker returns correct instance."""
        with patch.dict(
            os.environ,
            {
                "OPENROUTER_API_KEY": "test-openrouter-key",
                "TAVILY_API_KEY": "test-tavily-key",
            },
            clear=True,
        ):
            config = Config.from_env()
            checker = config.create_openrouter_checker()

            assert isinstance(checker, OpenRouterHealthChecker)
            assert checker.api_key == "test-openrouter-key"
            assert checker.base_url == "https://openrouter.ai/api/v1"
            assert checker.timeout == 10.0

    def test_create_openrouter_checker_with_custom_timeout(self):
        """Test that create_openrouter_checker accepts custom timeout."""
        with patch.dict(
            os.environ,
            {
                "OPENROUTER_API_KEY": "test-openrouter-key",
                "TAVILY_API_KEY": "test-tavily-key",
            },
            clear=True,
        ):
            config = Config.from_env()
            checker = config.create_openrouter_checker(timeout=5.0)

            assert checker.timeout == 5.0

    def test_create_tavily_checker(self):
        """Test that create_tavily_checker returns correct instance."""
        with patch.dict(
            os.environ,
            {
                "OPENROUTER_API_KEY": "test-openrouter-key",
                "TAVILY_API_KEY": "test-tavily-key",
            },
            clear=True,
        ):
            config = Config.from_env()
            checker = config.create_tavily_checker()

            assert isinstance(checker, TavilyHealthChecker)
            assert checker.api_key == "test-tavily-key"
            assert checker.base_url == "https://api.tavily.com"
            assert checker.timeout == 10.0

    def test_create_tavily_checker_with_custom_timeout(self):
        """Test that create_tavily_checker accepts custom timeout."""
        with patch.dict(
            os.environ,
            {
                "OPENROUTER_API_KEY": "test-openrouter-key",
                "TAVILY_API_KEY": "test-tavily-key",
            },
            clear=True,
        ):
            config = Config.from_env()
            checker = config.create_tavily_checker(timeout=5.0)

            assert checker.timeout == 5.0

    def test_create_tavily_checker_with_custom_base_url(self):
        """Test that create_tavily_checker uses config's base_url."""
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
                tavily_base_url="https://custom.tavily.com",
            )
            checker = config.create_tavily_checker()

            assert checker.base_url == "https://custom.tavily.com"
