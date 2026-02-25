"""Configuration management for STORMer.

This module handles loading and validating configuration from environment variables
and YAML configuration files, including API keys for OpenRouter and Tavily.
"""

from os import getenv

from dotenv import load_dotenv
from pydantic import BaseModel, Field, SecretStr, field_validator

from stormer.yaml_config import find_yaml_config, load_yaml_config, merge_config_settings


class Config(BaseModel):
    """Configuration for STORMer application.

    Loads API keys and settings from environment variables.
    Call load_dotenv() before creating this instance to load from .env file.
    """

    openrouter_api_key: SecretStr = Field(
        default=...,
        description="OpenRouter API key for LLM access",
    )
    tavily_api_key: SecretStr = Field(
        default=...,
        description="Tavily API key for search capabilities",
    )
    openrouter_model: str = Field(
        default="anthropic/claude-3-5-sonnet",
        description="Model identifier to use with OpenRouter",
    )
    openrouter_base_url: str = Field(
        default="https://openrouter.ai/api/v1",
        description="Base URL for OpenRouter API",
    )
    tavily_base_url: str = Field(
        default="https://api.tavily.com",
        description="Base URL for Tavily API",
    )
    openrouter_timeout: float = Field(
        default=10.0,
        description="Timeout in seconds for OpenRouter API requests",
    )
    tavily_timeout: float = Field(
        default=10.0,
        description="Timeout in seconds for Tavily API requests",
    )

    @field_validator("openrouter_api_key", "tavily_api_key")
    @classmethod
    def validate_api_keys(cls, v: SecretStr | None) -> SecretStr:
        """Validate that required API keys are provided.

        Args:
            v: The secret string value to validate

        Returns:
            The validated secret string

        Raises:
            ValueError: If the API key is None or empty
        """
        if v is None or v.get_secret_value() == "":
            raise ValueError(
                "API key cannot be empty. Please set the required environment variables."
            )
        return v

    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables and YAML file.

        Loads environment variables from .env file if present,
        loads YAML configuration if present, merges them with priority:
        env vars > YAML > defaults, then creates a Config instance.

        Returns:
            Config instance loaded from environment and YAML

        Raises:
            ValueError: If required environment variables are not set
        """
        load_dotenv()

        # Load YAML configuration if present
        yaml_path = find_yaml_config()
        yaml_dict = load_yaml_config(yaml_path) if yaml_path else None

        # Get environment variables
        env_vars = {
            "OPENROUTER_MODEL": getenv("OPENROUTER_MODEL"),
            "OPENROUTER_BASE_URL": getenv("OPENROUTER_BASE_URL"),
            "OPENROUTER_TIMEOUT": getenv("OPENROUTER_TIMEOUT"),
            "TAVILY_BASE_URL": getenv("TAVILY_BASE_URL"),
            "TAVILY_TIMEOUT": getenv("TAVILY_TIMEOUT"),
        }

        # Merge configurations with priority: env > YAML > defaults
        merged_config = merge_config_settings(yaml_dict, env_vars)

        # Get API keys from environment only (never from YAML for security)
        openrouter_key = getenv("OPENROUTER_API_KEY")
        tavily_key = getenv("TAVILY_API_KEY")

        # Validate that API keys are present
        if not openrouter_key:
            raise ValueError(
                "OPENROUTER_API_KEY is required. Please set it in your .env file or environment."
            )
        if not tavily_key:
            raise ValueError(
                "TAVILY_API_KEY is required. Please set it in your .env file or environment."
            )

        return cls(
            openrouter_api_key=openrouter_key,
            tavily_api_key=tavily_key,
            openrouter_model=merged_config["openrouter"]["model"],
            openrouter_base_url=merged_config["openrouter"]["base_url"],
            openrouter_timeout=merged_config["openrouter"]["timeout"],
            tavily_base_url=merged_config["tavily"]["base_url"],
            tavily_timeout=merged_config["tavily"]["timeout"],
        )

    def create_openrouter_checker(self, timeout: float | None = None):
        """Create an OpenRouter health checker instance.

        Args:
            timeout: Request timeout in seconds (default: uses config's openrouter_timeout)

        Returns:
            OpenRouterHealthChecker instance configured with this config's API key and base URL
        """
        from stormer.connectivity.openrouter import OpenRouterHealthChecker

        if timeout is None:
            timeout = self.openrouter_timeout

        return OpenRouterHealthChecker(
            api_key=self.openrouter_api_key.get_secret_value(),
            base_url=self.openrouter_base_url,
            timeout=timeout,
        )

    def create_tavily_checker(self, timeout: float | None = None):
        """Create a Tavily health checker instance.

        Args:
            timeout: Request timeout in seconds (default: uses config's tavily_timeout)

        Returns:
            TavilyHealthChecker instance configured with this config's API key and base URL
        """
        from stormer.connectivity.tavily import TavilyHealthChecker

        if timeout is None:
            timeout = self.tavily_timeout

        return TavilyHealthChecker(
            api_key=self.tavily_api_key.get_secret_value(),
            base_url=self.tavily_base_url,
            timeout=timeout,
        )


def get_config() -> Config:
    """Get the application configuration.

    Convenience function to load configuration from environment.

    Returns:
        Config instance loaded from environment

    Raises:
        ValueError: If required environment variables are not set
    """
    return Config.from_env()
