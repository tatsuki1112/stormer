"""DuckDuckGo health checker implementation.

This module provides health check functionality for DuckDuckGo search.
"""

import time

from ddgs import DDGS

from stormer.connectivity.base import HealthCheckResult, ServiceHealthChecker, ServiceStatus
from stormer.connectivity.exceptions import (
    NetworkError,
    ServiceUnavailableError,
    TimeoutError as CustomTimeoutError,
)


class DuckDuckGoHealthChecker(ServiceHealthChecker):
    """Health checker for DuckDuckGo search.

    Uses the DuckDuckGo search API via the ddgs library to verify connectivity.
    No API key is required for DuckDuckGo search.
    """

    def __init__(
        self,
        timeout: float = 10.0,
        max_results: int = 5,
    ):
        """Initialize the DuckDuckGo health checker.

        Args:
            timeout: Request timeout in seconds (not directly used by ddgs library,
                    but kept for API consistency and potential future use)
            max_results: Maximum number of search results to retrieve
        """
        self.timeout = timeout
        self.max_results = max_results

    async def check_health(self) -> HealthCheckResult:
        """Check the health of DuckDuckGo search.

        Performs a simple search query to verify:
        - DuckDuckGo service is accessible (connectivity)
        - DuckDuckGo service is operational (availability)

        Returns:
            HealthCheckResult with status, message, response time, and result count

        Raises:
            TimeoutError: If the request times out
            NetworkError: If there's a network connectivity issue
            ServiceUnavailableError: If the service is down
        """
        import asyncio

        start_time = time.time()

        # Helper function to calculate response time
        def get_response_time():
            return (time.time() - start_time) * 1000

        try:
            # Use DDGS library to perform a simple search
            # Note: DDGS is synchronous, so we run it in an executor
            loop = asyncio.get_event_loop()

            def perform_search():
                ddgs = DDGS()
                results = ddgs.text(
                    "test",
                    max_results=self.max_results,
                )
                return list(results) if results else []

            # Run the synchronous search in an executor to avoid blocking
            results = await asyncio.wait_for(
                loop.run_in_executor(None, perform_search),
                timeout=self.timeout,
            )

            response_time_ms = get_response_time()

            # Count results
            result_count = len(results)

            return HealthCheckResult(
                status=ServiceStatus.HEALTHY,
                message="DuckDuckGo search is operational",
                response_time_ms=response_time_ms,
                details={"result_count": result_count},
            )

        except asyncio.TimeoutError as e:
            raise CustomTimeoutError(f"DuckDuckGo search request timed out: {e}") from e

        except TimeoutError as e:
            raise CustomTimeoutError(f"DuckDuckGo search request timed out: {e}") from e

        except Exception as e:
            error_message = str(e).lower()

            # Check for timeout-related errors
            if "timeout" in error_message:
                raise CustomTimeoutError(f"DuckDuckGo search request timed out: {e}") from e

            # Check for network-related errors
            if any(
                term in error_message
                for term in ["connection", "network", "dns", "resolve", "refused"]
            ):
                raise NetworkError(f"DuckDuckGo network error: {e}") from e

            # Check for service unavailable errors
            if any(
                term in error_message
                for term in ["503", "service unavailable", "unavailable", "failed to initialize"]
            ):
                raise ServiceUnavailableError(f"DuckDuckGo service unavailable: {e}") from e

            # Check for rate limiting (return DEGRADED instead of raising)
            if any(term in error_message for term in ["rate limit", "too many requests", "429"]):
                response_time_ms = get_response_time()
                return HealthCheckResult(
                    status=ServiceStatus.DEGRADED,
                    message=f"DuckDuckGo rate limiting detected: {e}",
                    response_time_ms=response_time_ms,
                )

            # For any other unexpected error, return UNKNOWN status
            response_time_ms = get_response_time()
            return HealthCheckResult(
                status=ServiceStatus.UNKNOWN,
                message=f"Unexpected error checking DuckDuckGo: {e}",
                response_time_ms=response_time_ms,
            )
