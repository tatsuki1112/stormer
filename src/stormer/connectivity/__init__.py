"""Connectivity checking module for STORMer external services.

This module provides health check functionality for external services used by STORMer:
- OpenRouter (LLM API)
- Tavily (search API)
"""

from stormer.connectivity.base import HealthCheckResult, ServiceHealthChecker, ServiceStatus
from stormer.connectivity.exceptions import (
    AuthenticationError,
    ConnectivityCheckError,
    NetworkError,
    ServiceUnavailableError,
    TimeoutError,
)
from stormer.connectivity.openrouter import OpenRouterHealthChecker
from stormer.connectivity.tavily import TavilyHealthChecker

__all__ = [
    # Base abstractions
    "ServiceStatus",
    "HealthCheckResult",
    "ServiceHealthChecker",
    # Exceptions
    "ConnectivityCheckError",
    "AuthenticationError",
    "TimeoutError",
    "NetworkError",
    "ServiceUnavailableError",
    # Service checkers
    "OpenRouterHealthChecker",
    "TavilyHealthChecker",
]
