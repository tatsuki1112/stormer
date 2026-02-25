"""Tests for YAML configuration loading."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from stormer.yaml_config import (
    find_yaml_config,
    load_yaml_config,
    merge_config_settings,
)


class TestFindYamlConfig:
    """Test suite for find_yaml_config function."""

    def test_find_yaml_in_current_directory(self, tmp_path):
        """Test that find_yaml_config finds stormer.yaml in current directory."""
        config_file = tmp_path / "stormer.yaml"
        config_file.write_text("openrouter:\n  model: test-model\n")

        with patch.dict(os.environ, {"PWD": str(tmp_path)}):
            result = find_yaml_config()

        assert result == config_file

    def test_find_yaml_in_current_directory_yml_extension(self, tmp_path):
        """Test that find_yaml_config finds stormer.yml in current directory."""
        config_file = tmp_path / "stormer.yml"
        config_file.write_text("openrouter:\n  model: test-model\n")

        with patch.dict(os.environ, {"PWD": str(tmp_path)}):
            result = find_yaml_config()

        assert result == config_file

    def test_find_yaml_returns_none_when_missing(self, tmp_path):
        """Test that find_yaml_config returns None when no YAML file exists."""
        with patch.dict(os.environ, {"PWD": str(tmp_path)}):
            result = find_yaml_config()

        assert result is None


class TestLoadYamlConfig:
    """Test suite for load_yaml_config function."""

    def test_load_valid_yaml_file(self, tmp_path):
        """Test that load_yaml_config parses valid YAML correctly."""
        config_file = tmp_path / "stormer.yaml"
        config_content = {
            "openrouter": {
                "model": "anthropic/claude-3-5-sonnet",
                "base_url": "https://openrouter.ai/api/v1",
                "timeout": 10.0,
            },
            "tavily": {
                "base_url": "https://api.tavily.com",
                "timeout": 10.0,
            },
        }
        with open(config_file, "w") as f:
            yaml.dump(config_content, f)

        result = load_yaml_config(config_file)

        assert result == config_content

    def test_load_yaml_returns_none_on_parse_error(self, tmp_path):
        """Test that load_yaml_config returns None on invalid YAML."""
        config_file = tmp_path / "stormer.yaml"
        config_file.write_text("invalid: yaml: content: [unclosed")

        result = load_yaml_config(config_file)

        assert result is None

    def test_load_yaml_with_empty_file(self, tmp_path):
        """Test that load_yaml_config handles empty files."""
        config_file = tmp_path / "stormer.yaml"
        config_file.write_text("")

        result = load_yaml_config(config_file)

        assert result is None

    def test_load_yaml_with_nonexistent_file(self, tmp_path):
        """Test that load_yaml_config returns None for nonexistent files."""
        config_file = tmp_path / "nonexistent.yaml"

        result = load_yaml_config(config_file)

        assert result is None

    def test_load_yaml_ignores_api_keys(self, tmp_path):
        """Test that load_yaml_config filters out API keys for security."""
        config_file = tmp_path / "stormer.yaml"
        config_content = {
            "openrouter": {
                "model": "test-model",
                "api_key": "should-be-ignored",  # This should be filtered
            },
            "tavily": {
                "api_key": "should-be-ignored",  # This should be filtered
            },
        }
        with open(config_file, "w") as f:
            yaml.dump(config_content, f)

        result = load_yaml_config(config_file)

        # API keys should be filtered out
        assert "api_key" not in result.get("openrouter", {})
        assert "api_key" not in result.get("tavily", {})


class TestMergeConfigSettings:
    """Test suite for merge_config_settings function."""

    def test_merge_env_overrides_yaml(self):
        """Test that environment variables override YAML values."""
        yaml_dict = {
            "openrouter": {"model": "yaml-model", "base_url": "https://yaml.example.com"},
            "tavily": {"base_url": "https://yaml.example.com"},
        }
        env_vars = {
            "OPENROUTER_MODEL": "env-model",
            "OPENROUTER_BASE_URL": "https://env.example.com",
            "TAVILY_BASE_URL": "https://env-tavily.example.com",
        }

        result = merge_config_settings(yaml_dict, env_vars)

        assert result["openrouter"]["model"] == "env-model"
        assert result["openrouter"]["base_url"] == "https://env.example.com"
        assert result["tavily"]["base_url"] == "https://env-tavily.example.com"

    def test_merge_yaml_used_when_env_not_set(self):
        """Test that YAML values are used when env vars are not set."""
        yaml_dict = {
            "openrouter": {"model": "yaml-model", "base_url": "https://yaml.example.com"},
            "tavily": {"base_url": "https://yaml.example.com"},
        }
        env_vars = {}

        result = merge_config_settings(yaml_dict, env_vars)

        assert result["openrouter"]["model"] == "yaml-model"
        assert result["openrouter"]["base_url"] == "https://yaml.example.com"
        assert result["tavily"]["base_url"] == "https://yaml.example.com"

    def test_merge_uses_defaults_when_both_missing(self):
        """Test that defaults are used when both YAML and env are missing."""
        yaml_dict = {}
        env_vars = {}

        result = merge_config_settings(yaml_dict, env_vars)

        # Should have default values
        assert "openrouter" in result
        assert "tavily" in result
        assert result["openrouter"]["model"] == "anthropic/claude-3-5-sonnet"
        assert result["openrouter"]["base_url"] == "https://openrouter.ai/api/v1"
        assert result["tavily"]["base_url"] == "https://api.tavily.com"

    def test_merge_timeout_values(self):
        """Test that timeout values are merged correctly."""
        yaml_dict = {
            "openrouter": {"timeout": 15.0},
            "tavily": {"timeout": 20.0},
        }
        env_vars = {}

        result = merge_config_settings(yaml_dict, env_vars)

        assert result["openrouter"]["timeout"] == 15.0
        assert result["tavily"]["timeout"] == 20.0

    def test_merge_env_timeout_overrides_yaml(self):
        """Test that env timeout overrides YAML timeout."""
        yaml_dict = {
            "openrouter": {"timeout": 15.0},
        }
        env_vars = {"OPENROUTER_TIMEOUT": "30.0"}

        result = merge_config_settings(yaml_dict, env_vars)

        assert result["openrouter"]["timeout"] == 30.0

    def test_merge_handles_none_yaml(self):
        """Test that merge handles None YAML dict gracefully."""
        yaml_dict = None
        env_vars = {}

        result = merge_config_settings(yaml_dict, env_vars)

        # Should have default values
        assert "openrouter" in result
        assert "tavily" in result
