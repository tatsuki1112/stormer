"""Tests for OpenRouter health checker."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import HTTPStatusError, RequestError, TimeoutException

from stormer.connectivity.base import ServiceStatus
from stormer.connectivity.exceptions import (
    AuthenticationError,
    NetworkError,
    ServiceUnavailableError,
    TimeoutError,
)
from stormer.connectivity.openrouter import OpenRouterHealthChecker


class TestOpenRouterHealthChecker:
    """Test suite for OpenRouterHealthChecker."""

    @pytest.fixture
    def checker(self):
        """Create an OpenRouterHealthChecker instance for testing."""
        return OpenRouterHealthChecker(
            api_key="test-api-key",
            base_url="https://openrouter.ai/api/v1",
            timeout=10.0,
        )

    def test_initialization(self, checker):
        """Test that OpenRouterHealthChecker initializes correctly."""
        assert checker.api_key == "test-api-key"
        assert checker.base_url == "https://openrouter.ai/api/v1"
        assert checker.timeout == 10.0

    @pytest.mark.asyncio
    async def test_successful_health_check(self, checker):
        """Test successful health check with 200 response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [{"id": "model1"}, {"id": "model2"}]}
        mock_response.text = ""
        mock_response.headers = {}

        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_client_instance
            result = await checker.check_health()

            assert result.status == ServiceStatus.HEALTHY
            assert "operational" in result.message.lower()
            assert result.response_time_ms is not None
            assert result.response_time_ms > 0
            assert result.details == {"model_count": 2}

    @pytest.mark.asyncio
    async def test_authentication_failure_401(self, checker):
        """Test health check with 401 authentication failure."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_response.headers = {}
        mock_request = MagicMock()

        error = HTTPStatusError(
            "Unauthorized", request=mock_request, response=mock_response
        )

        mock_client_instance = AsyncMock()
        mock_client_instance.get.side_effect = error

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_client_instance
            with pytest.raises(AuthenticationError) as exc_info:
                await checker.check_health()

            assert (
                "authentication" in str(exc_info.value).lower()
                or "unauthorized" in str(exc_info.value).lower()
            )

    @pytest.mark.asyncio
    async def test_rate_limiting_429_degraded(self, checker):
        """Test health check with 429 rate limiting returns DEGRADED status."""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.text = "Too Many Requests"
        mock_response.headers = {}

        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_client_instance
            result = await checker.check_health()

            assert result.status == ServiceStatus.DEGRADED
            assert "rate limit" in result.message.lower()

    @pytest.mark.asyncio
    async def test_server_error_500(self, checker):
        """Test health check with 500 server error."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.headers = {}
        mock_request = MagicMock()

        error = HTTPStatusError("Server error", request=mock_request, response=mock_response)

        mock_client_instance = AsyncMock()
        mock_client_instance.get.side_effect = error

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_client_instance
            with pytest.raises(ServiceUnavailableError):
                await checker.check_health()

    @pytest.mark.asyncio
    async def test_timeout_error(self, checker):
        """Test health check with timeout."""
        mock_client_instance = AsyncMock()
        mock_client_instance.get.side_effect = TimeoutException("Request timed out")

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_client_instance
            with pytest.raises(TimeoutError):
                await checker.check_health()

    @pytest.mark.asyncio
    async def test_network_error(self, checker):
        """Test health check with network error."""
        mock_client_instance = AsyncMock()
        mock_client_instance.get.side_effect = RequestError("Connection refused")

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_client_instance
            with pytest.raises(NetworkError):
                await checker.check_health()

    @pytest.mark.asyncio
    async def test_malformed_json_response(self, checker):
        """Test health check with malformed JSON response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.headers = {}

        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_client_instance
            result = await checker.check_health()

            assert result.status == ServiceStatus.UNHEALTHY
            assert "parse" in result.message.lower() or "malformed" in result.message.lower()

    @pytest.mark.asyncio
    async def test_response_time_calculation(self, checker):
        """Test that response time is calculated accurately."""
        import time

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        mock_response.headers = {}

        async def slow_get(*args, **kwargs):
            await asyncio.sleep(0.01)  # Sleep for 10ms
            return mock_response

        mock_client_instance = AsyncMock()
        mock_client_instance.get = slow_get

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_client_instance
            result = await checker.check_health()

            assert result.response_time_ms is not None
            assert result.response_time_ms >= 10  # At least 10ms

    @pytest.mark.asyncio
    async def test_empty_model_list(self, checker):
        """Test health check with empty model list."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        mock_response.headers = {}

        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_client_instance
            result = await checker.check_health()

            assert result.status == ServiceStatus.HEALTHY
            assert result.details == {"model_count": 0}

    @pytest.mark.asyncio
    async def test_missing_data_key_in_response(self, checker):
        """Test health check with missing 'data' key in response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": []}
        mock_response.headers = {}

        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_client_instance
            result = await checker.check_health()

            assert result.status == ServiceStatus.UNHEALTHY
            assert "unexpected" in result.message.lower()
