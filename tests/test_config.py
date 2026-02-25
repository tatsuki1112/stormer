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
        with patch("stormer.config.load_dotenv"), patch.dict(
            os.environ,
            {
                "TAVILY_API_KEY": "test-tavily-key",
            },
            clear=True,
        ):
            with pytest.raises(ValueError) as exc_info:
                Config.from_env()

            assert "OPENROUTER_API_KEY" in str(exc_info.value)

    def test_config_from_env_with_missing_tavily_key(self):
        """Test that Config raises error when Tavily API key is missing."""
        with patch("stormer.config.load_dotenv"), patch.dict(
            os.environ,
            {
                "OPENROUTER_API_KEY": "test-openrouter-key",
            },
            clear=True,
        ):
            with pytest.raises(ValueError) as exc_info:
                Config.from_env()

            assert "TAVILY_API_KEY" in str(exc_info.value)

    def test_config_from_env_with_empty_keys(self):
        """Test that Config raises error when API keys are empty strings."""
        with patch("stormer.config.load_dotenv"), patch.dict(
            os.environ,
            {
                "OPENROUTER_API_KEY": "",
                "TAVILY_API_KEY": "",
            },
            clear=True,
        ):
            with pytest.raises(ValueError) as exc_info:
                Config.from_env()

            assert "OPENROUTER_API_KEY" in str(exc_info.value)

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


class TestConfigYamlSupport:
    """Test suite for YAML configuration support."""

    def test_from_env_uses_yaml_when_env_not_set(self, tmp_path):
        """Test that Config uses YAML values when env vars are not set."""
        config_file = tmp_path / "stormer.yaml"
        config_file.write_text(
            """
openrouter:
  model: yaml-model
  base_url: https://yaml.example.com
  timeout: 15.0
tavily:
  base_url: https://yaml-tavily.example.com
  timeout: 20.0
"""
        )

        with patch.dict(
            os.environ,
            {
                "OPENROUTER_API_KEY": "test-openrouter-key",
                "TAVILY_API_KEY": "test-tavily-key",
                "PWD": str(tmp_path),
            },
            clear=True,
        ):
            config = Config.from_env()

        assert config.openrouter_model == "yaml-model"
        assert config.openrouter_base_url == "https://yaml.example.com"
        assert config.openrouter_timeout == 15.0
        assert config.tavily_base_url == "https://yaml-tavily.example.com"
        assert config.tavily_timeout == 20.0

    def test_env_var_overrides_yaml_model(self, tmp_path):
        """Test that env vars override YAML model setting."""
        config_file = tmp_path / "stormer.yaml"
        config_file.write_text(
            """
openrouter:
  model: yaml-model
"""
        )

        with patch.dict(
            os.environ,
            {
                "OPENROUTER_API_KEY": "test-openrouter-key",
                "TAVILY_API_KEY": "test-tavily-key",
                "OPENROUTER_MODEL": "env-model",
                "PWD": str(tmp_path),
            },
            clear=True,
        ):
            config = Config.from_env()

        assert config.openrouter_model == "env-model"

    def test_env_var_overrides_yaml_base_url(self, tmp_path):
        """Test that env vars override YAML base URL setting."""
        config_file = tmp_path / "stormer.yaml"
        config_file.write_text(
            """
openrouter:
  base_url: https://yaml.example.com
"""
        )

        with patch.dict(
            os.environ,
            {
                "OPENROUTER_API_KEY": "test-openrouter-key",
                "TAVILY_API_KEY": "test-tavily-key",
                "OPENROUTER_BASE_URL": "https://env.example.com",
                "PWD": str(tmp_path),
            },
            clear=True,
        ):
            config = Config.from_env()

        assert config.openrouter_base_url == "https://env.example.com"

    def test_yaml_timeout_propagates_to_config(self, tmp_path):
        """Test that YAML timeout values are propagated to Config."""
        config_file = tmp_path / "stormer.yaml"
        config_file.write_text(
            """
openrouter:
  timeout: 25.0
tavily:
  timeout: 30.0
"""
        )

        with patch.dict(
            os.environ,
            {
                "OPENROUTER_API_KEY": "test-openrouter-key",
                "TAVILY_API_KEY": "test-tavily-key",
                "PWD": str(tmp_path),
            },
            clear=True,
        ):
            config = Config.from_env()

        assert config.openrouter_timeout == 25.0
        assert config.tavily_timeout == 30.0

    def test_api_keys_ignore_yaml_values(self, tmp_path):
        """Test that API keys from YAML are ignored for security."""
        config_file = tmp_path / "stormer.yaml"
        config_file.write_text(
            """
openrouter:
  api_key: yaml-key-should-be-ignored
  model: test-model
tavily:
  api_key: yaml-key-should-be-ignored
"""
        )

        with patch.dict(
            os.environ,
            {
                "OPENROUTER_API_KEY": "env-openrouter-key",
                "TAVILY_API_KEY": "env-tavily-key",
                "PWD": str(tmp_path),
            },
            clear=True,
        ):
            config = Config.from_env()

        # Should use env keys, not YAML keys
        assert config.openrouter_api_key.get_secret_value() == "env-openrouter-key"
        assert config.tavily_api_key.get_secret_value() == "env-tavily-key"

    def test_backward_compat_without_yaml(self):
        """Test that Config works without YAML file (backward compatibility)."""
        with patch.dict(
            os.environ,
            {
                "OPENROUTER_API_KEY": "test-openrouter-key",
                "TAVILY_API_KEY": "test-tavily-key",
            },
            clear=True,
        ):
            config = Config.from_env()

        # Should use defaults
        assert config.openrouter_model == "anthropic/claude-3-5-sonnet"
        assert config.openrouter_base_url == "https://openrouter.ai/api/v1"
        assert config.tavily_base_url == "https://api.tavily.com"
        assert config.openrouter_timeout == 10.0
        assert config.tavily_timeout == 10.0

    def test_malformed_yaml_falls_back_to_defaults(self, tmp_path):
        """Test that malformed YAML falls back to defaults."""
        config_file = tmp_path / "stormer.yaml"
        config_file.write_text("invalid: yaml: content: [unclosed")

        with patch.dict(
            os.environ,
            {
                "OPENROUTER_API_KEY": "test-openrouter-key",
                "TAVILY_API_KEY": "test-tavily-key",
                "PWD": str(tmp_path),
            },
            clear=True,
        ):
            config = Config.from_env()

        # Should use defaults when YAML is malformed
        assert config.openrouter_model == "anthropic/claude-3-5-sonnet"
        assert config.openrouter_base_url == "https://openrouter.ai/api/v1"
        assert config.openrouter_timeout == 10.0

    def test_yaml_timeout_used_in_openrouter_checker(self, tmp_path):
        """Test that YAML timeout is used in OpenRouter checker."""
        config_file = tmp_path / "stormer.yaml"
        config_file.write_text(
            """
openrouter:
  timeout: 15.0
"""
        )

        with patch.dict(
            os.environ,
            {
                "OPENROUTER_API_KEY": "test-openrouter-key",
                "TAVILY_API_KEY": "test-tavily-key",
                "PWD": str(tmp_path),
            },
            clear=True,
        ):
            config = Config.from_env()
            checker = config.create_openrouter_checker()

        assert checker.timeout == 15.0

    def test_yaml_timeout_used_in_tavily_checker(self, tmp_path):
        """Test that YAML timeout is used in Tavily checker."""
        config_file = tmp_path / "stormer.yaml"
        config_file.write_text(
            """
tavily:
  timeout: 20.0
"""
        )

        with patch.dict(
            os.environ,
            {
                "OPENROUTER_API_KEY": "test-openrouter-key",
                "TAVILY_API_KEY": "test-tavily-key",
                "PWD": str(tmp_path),
            },
            clear=True,
        ):
            config = Config.from_env()
            checker = config.create_tavily_checker()

        assert checker.timeout == 20.0

    def test_checker_param_overrides_yaml_timeout(self, tmp_path):
        """Test that checker parameter overrides YAML timeout."""
        config_file = tmp_path / "stormer.yaml"
        config_file.write_text(
            """
openrouter:
  timeout: 15.0
"""
        )

        with patch.dict(
            os.environ,
            {
                "OPENROUTER_API_KEY": "test-openrouter-key",
                "TAVILY_API_KEY": "test-tavily-key",
                "PWD": str(tmp_path),
            },
            clear=True,
        ):
            config = Config.from_env()
            checker = config.create_openrouter_checker(timeout=5.0)

        assert checker.timeout == 5.0

