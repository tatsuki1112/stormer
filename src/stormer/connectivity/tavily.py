"""Tavily health checker implementation.

This module provides health check functionality for the Tavily API.
"""

import time

import httpx

from stormer.connectivity.base import HealthCheckResult, ServiceHealthChecker, ServiceStatus
from stormer.connectivity.exceptions import (
    AuthenticationError,
    NetworkError,
    ServiceUnavailableError,
    TimeoutError as CustomTimeoutError,
)


class TavilyHealthChecker(ServiceHealthChecker):
    """Health checker for Tavily API.

    Uses the /search endpoint with a minimal query to verify API connectivity and authentication.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.tavily.com",
        timeout: float = 10.0,
    ):
        """Initialize the Tavily health checker.

        Args:
            api_key: Tavily API key
            base_url: Base URL for Tavily API
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout

    async def check_health(self) -> HealthCheckResult:
        """Check the health of the Tavily API.

        Makes a lightweight POST request to the /search endpoint with a minimal query
        to verify:
        - API key is valid (authentication)
        - Service is accessible (connectivity)
        - Service is operational (availability)

        Returns:
            HealthCheckResult with status, message, response time, and answer presence

        Raises:
            AuthenticationError: If API key is invalid (401)
            TimeoutError: If the request times out
            NetworkError: If there's a network connectivity issue
            ServiceUnavailableError: If the service is down (5xx errors)
        """
        url = f"{self.base_url}/search"
        payload = {
            "api_key": self.api_key,
            "query": "test",
            "max_results": 1,
        }

        start_time = time.time()

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)

            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000

            # Handle authentication failure
            if response.status_code == 401:
                raise AuthenticationError("Tavily authentication failed: Invalid API key (401)")

            # Handle rate limiting (degraded status, not an exception)
            if response.status_code == 429:
                return HealthCheckResult(
                    status=ServiceStatus.DEGRADED,
                    message="Tavily API is rate limited (429)",
                    response_time_ms=response_time_ms,
                )

            # Handle server errors
            if response.status_code >= 500:
                raise ServiceUnavailableError(
                    f"Tavily API unavailable: {response.status_code} {response.text}"
                )

            # Handle other HTTP errors
            if response.status_code >= 400:
                return HealthCheckResult(
                    status=ServiceStatus.UNHEALTHY,
                    message=f"Tavily API error: {response.status_code} {response.text}",
                    response_time_ms=response_time_ms,
                )

            # Parse response
            try:
                data = response.json()
            except ValueError as e:
                return HealthCheckResult(
                    status=ServiceStatus.UNHEALTHY,
                    message=f"Failed to parse Tavily response: {e}",
                    response_time_ms=response_time_ms,
                )

            # Check if answer is present
            has_answer = "answer" in data and bool(data.get("answer"))

            return HealthCheckResult(
                status=ServiceStatus.HEALTHY,
                message="Tavily API is operational",
                response_time_ms=response_time_ms,
                details={"has_answer": has_answer},
            )

        except httpx.TimeoutException as e:
            raise CustomTimeoutError(f"Tavily API request timed out: {e}") from e

        except httpx.NetworkError as e:
            raise NetworkError(f"Tavily API network error: {e}") from e

        except httpx.RequestError as e:
            raise NetworkError(f"Tavily API request error: {e}") from e

        except httpx.HTTPStatusError as e:
            # This shouldn't happen as we handle status codes above,
            # but keeping it for safety
            if e.response.status_code >= 500:
                raise ServiceUnavailableError(
                    f"Tavily API unavailable: {e.response.status_code}"
                ) from e
            elif e.response.status_code == 401:
                raise AuthenticationError(
                    f"Tavily authentication failed: {e.response.status_code}"
                ) from e
            else:
                raise

        except AuthenticationError:
            raise

        except CustomTimeoutError:
            raise

        except NetworkError:
            raise

        except ServiceUnavailableError:
            raise

        except Exception as e:
            return HealthCheckResult(
                status=ServiceStatus.UNKNOWN,
                message=f"Unexpected error checking Tavily: {e}",
            )
