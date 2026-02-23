"""Base abstractions for connectivity checking.

This module defines the core interfaces and data models used across
all connectivity checkers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum


class ServiceStatus(str, Enum):
    """Status of a service health check.

    Attributes:
        HEALTHY: Service is fully operational
        UNHEALTHY: Service is not operational
        DEGRADED: Service is operational but with limitations
        TIMEOUT: Service did not respond within the timeout period
        AUTHENTICATION_FAILED: Service rejected the API credentials
        UNKNOWN: Unable to determine service status
    """

    HEALTHY = "HEALTHY"
    UNHEALTHY = "UNHEALTHY"
    DEGRADED = "DEGRADED"
    TIMEOUT = "TIMEOUT"
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    UNKNOWN = "UNKNOWN"


@dataclass
class HealthCheckResult:
    """Result of a service health check.

    Attributes:
        status: The service status
        message: Human-readable status message
        response_time_ms: Response time in milliseconds, if available
        details: Additional service-specific details, if available
    """

    status: ServiceStatus
    message: str
    response_time_ms: float | None = None
    details: dict[str, object] | None = None


class ServiceHealthChecker(ABC):
    """Abstract base class for service health checkers.

    All service-specific health checkers should inherit from this class
    and implement the check_health method.
    """

    @abstractmethod
    async def check_health(self) -> HealthCheckResult:
        """Check the health of the service.

        Returns:
            HealthCheckResult containing the service status and details

        Raises:
            AuthenticationError: If API credentials are invalid
            TimeoutError: If the request times out
            NetworkError: If there's a network connectivity issue
            ServiceUnavailableError: If the service is down (5xx errors)
        """
        pass
