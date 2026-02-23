"""Tests for connectivity base abstractions."""

import time

import pytest

from stormer.connectivity.base import HealthCheckResult, ServiceHealthChecker, ServiceStatus


class TestServiceStatus:
    """Test suite for ServiceStatus enum."""

    def test_service_status_values(self):
        """Test that ServiceStatus has all expected values."""
        expected_values = {
            "HEALTHY",
            "UNHEALTHY",
            "DEGRADED",
            "TIMEOUT",
            "AUTHENTICATION_FAILED",
            "UNKNOWN",
        }
        actual_values = {status.value for status in ServiceStatus}

        assert actual_values == expected_values

    def test_service_status_string_representation(self):
        """Test that ServiceStatus enum values have correct string representation."""
        assert ServiceStatus.HEALTHY.value == "HEALTHY"
        assert ServiceStatus.UNHEALTHY.value == "UNHEALTHY"
        assert ServiceStatus.DEGRADED.value == "DEGRADED"
        assert ServiceStatus.TIMEOUT.value == "TIMEOUT"
        assert ServiceStatus.AUTHENTICATION_FAILED.value == "AUTHENTICATION_FAILED"
        assert ServiceStatus.UNKNOWN.value == "UNKNOWN"


class TestHealthCheckResult:
    """Test suite for HealthCheckResult dataclass."""

    def test_health_check_result_creation(self):
        """Test creating a HealthCheckResult with all fields."""
        result = HealthCheckResult(
            status=ServiceStatus.HEALTHY,
            message="Service is operational",
            response_time_ms=123.45,
            details={"model_count": 100},
        )

        assert result.status == ServiceStatus.HEALTHY
        assert result.message == "Service is operational"
        assert result.response_time_ms == 123.45
        assert result.details == {"model_count": 100}

    def test_health_check_result_with_optional_fields(self):
        """Test creating a HealthCheckResult with minimal required fields."""
        result = HealthCheckResult(
            status=ServiceStatus.HEALTHY,
            message="Service is operational",
        )

        assert result.status == ServiceStatus.HEALTHY
        assert result.message == "Service is operational"
        assert result.response_time_ms is None
        assert result.details is None

    def test_health_check_result_with_none_details(self):
        """Test that details can be None."""
        result = HealthCheckResult(
            status=ServiceStatus.UNHEALTHY,
            message="Service unavailable",
            response_time_ms=50.0,
            details=None,
        )

        assert result.details is None


class TestServiceHealthChecker:
    """Test suite for ServiceHealthChecker abstract base class."""

    def test_service_health_checker_is_abstract(self):
        """Test that ServiceHealthChecker cannot be instantiated directly."""
        with pytest.raises(TypeError):
            ServiceHealthChecker()  # type: ignore[abstract]

    def test_service_health_checker_requires_check_health_method(self):
        """Test that subclasses must implement check_health method."""

        # This should work because we implement the abstract method
        class MockChecker(ServiceHealthChecker):
            async def check_health(self) -> HealthCheckResult:
                return HealthCheckResult(
                    status=ServiceStatus.HEALTHY,
                    message="Mock service is healthy",
                )

        checker = MockChecker()
        assert callable(checker.check_health)
