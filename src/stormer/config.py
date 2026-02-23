"""Configuration management for STORMer.

This module handles loading and validating configuration from environment variables,
including API keys for OpenRouter and Tavily.
"""

from os import getenv

from dotenv import load_dotenv
from pydantic import BaseModel, Field, SecretStr, field_validator


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
        """Create configuration from environment variables.

        Loads environment variables from .env file if present,
        then creates a Config instance.

        Returns:
            Config instance loaded from environment

        Raises:
            ValueError: If required environment variables are not set
        """
        load_dotenv()

        openrouter_key = getenv("OPENROUTER_API_KEY")
        tavily_key = getenv("TAVILY_API_KEY")

        return cls(
            openrouter_api_key=openrouter_key,  # type: ignore[arg-type]
            tavily_api_key=tavily_key,  # type: ignore[arg-type]
        )

    def create_openrouter_checker(self, timeout: float = 10.0):
        """Create an OpenRouter health checker instance.

        Args:
            timeout: Request timeout in seconds (default: 10.0)

        Returns:
            OpenRouterHealthChecker instance configured with this config's API key and base URL
        """
        from stormer.connectivity.openrouter import OpenRouterHealthChecker

        return OpenRouterHealthChecker(
            api_key=self.openrouter_api_key.get_secret_value(),
            base_url=self.openrouter_base_url,
            timeout=timeout,
        )

    def create_tavily_checker(self, timeout: float = 10.0):
        """Create a Tavily health checker instance.

        Args:
            timeout: Request timeout in seconds (default: 10.0)

        Returns:
            TavilyHealthChecker instance configured with this config's API key and base URL
        """
        from stormer.connectivity.tavily import TavilyHealthChecker

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
