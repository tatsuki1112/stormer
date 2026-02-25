"""YAML configuration loading for STORMer.

This module handles finding, loading, and merging YAML configuration files
with environment variables for STORMer application settings.
"""

import os
from pathlib import Path
from typing import Any

import yaml


def find_yaml_config() -> Path | None:
    """Find YAML configuration file in standard locations.

    Searches for configuration files in the following priority order:
    1. ./stormer.yaml or ./stormer.yml (current working directory)
    2. $HOME/.stormer/config.yaml (user home directory)

    Returns:
        Path to the first found configuration file, or None if not found
    """
    # Check current directory for stormer.yaml or stormer.yml
    cwd = Path(os.environ.get("PWD", os.getcwd()))
    for yaml_name in ["stormer.yaml", "stormer.yml"]:
        yaml_path = cwd / yaml_name
        if yaml_path.exists() and yaml_path.is_file():
            return yaml_path

    # Check home directory for ~/.stormer/config.yaml
    home = Path(os.environ.get("HOME", Path.home()))
    home_config = home / ".stormer" / "config.yaml"
    if home_config.exists() and home_config.is_file():
        return home_config

    return None


def load_yaml_config(path: Path) -> dict[str, Any] | None:
    """Load and parse YAML configuration file.

    Args:
        path: Path to the YAML file to load

    Returns:
        Parsed YAML content as a dictionary, or None if loading fails

    Note:
        This function filters out API keys from the loaded configuration
        for security reasons. API keys should only be loaded from .env files.
    """
    try:
        with open(path, "r") as f:
            content = yaml.safe_load(f)

        if not isinstance(content, dict):
            return None

        # Filter out API keys for security
        if "openrouter" in content and isinstance(content["openrouter"], dict):
            content["openrouter"].pop("api_key", None)

        if "tavily" in content and isinstance(content["tavily"], dict):
            content["tavily"].pop("api_key", None)

        return content

    except (OSError, yaml.YAMLError):
        return None


def merge_config_settings(
    yaml_dict: dict[str, Any] | None, env_vars: dict[str, str]
) -> dict[str, Any]:
    """Merge YAML configuration with environment variables.

    Environment variables take priority over YAML values, which take priority
    over defaults.

    Args:
        yaml_dict: Parsed YAML configuration (may be None)
        env_vars: Dictionary of environment variables

    Returns:
        Merged configuration dictionary with defaults applied
    """
    # Start with defaults
    config = {
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

    # Apply YAML values
    if yaml_dict:
        if "openrouter" in yaml_dict and isinstance(yaml_dict["openrouter"], dict):
            for key, value in yaml_dict["openrouter"].items():
                if key in config["openrouter"]:
                    config["openrouter"][key] = value

        if "tavily" in yaml_dict and isinstance(yaml_dict["tavily"], dict):
            for key, value in yaml_dict["tavily"].items():
                if key in config["tavily"]:
                    config["tavily"][key] = value

    # Apply environment variable overrides
    env_mapping = {
        "OPENROUTER_MODEL": ("openrouter", "model"),
        "OPENROUTER_BASE_URL": ("openrouter", "base_url"),
        "OPENROUTER_TIMEOUT": ("openrouter", "timeout"),
        "TAVILY_BASE_URL": ("tavily", "base_url"),
        "TAVILY_TIMEOUT": ("tavily", "timeout"),
    }

    for env_key, (section, config_key) in env_mapping.items():
        if env_key in env_vars and env_vars[env_key]:
            value = env_vars[env_key]

            # Convert timeout to float
            if config_key == "timeout":
                try:
                    value = float(value)
                except (ValueError, TypeError):
                    continue

            config[section][config_key] = value

    return config
