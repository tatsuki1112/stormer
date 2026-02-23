"""Tests for connectivity exceptions."""

import pytest

from stormer.connectivity.exceptions import (
    AuthenticationError,
    ConnectivityCheckError,
    NetworkError,
    ServiceUnavailableError,
    TimeoutError,
)


class TestConnectivityCheckError:
    """Test suite for base ConnectivityCheckError exception."""

    def test_connectivity_check_error_creation(self):
        """Test creating a basic ConnectivityCheckError."""
        error = ConnectivityCheckError("Basic connectivity error")

        assert str(error) == "Basic connectivity error"
        assert isinstance(error, Exception)

    def test_connectivity_check_error_with_custom_message(self):
        """Test creating ConnectivityCheckError with custom message."""
        message = "Custom error message with details: service=X"
        error = ConnectivityCheckError(message)

        assert str(error) == message


class TestAuthenticationError:
    """Test suite for AuthenticationError exception."""

    def test_authentication_error_creation(self):
        """Test creating an AuthenticationError."""
        error = AuthenticationError("Invalid API key")

        assert str(error) == "Invalid API key"
        assert isinstance(error, ConnectivityCheckError)

    def test_authentication_error_inheritance(self):
        """Test that AuthenticationError inherits from ConnectivityCheckError."""
        error = AuthenticationError("Auth failed")

        assert isinstance(error, ConnectivityCheckError)
        assert isinstance(error, Exception)


class TestTimeoutError:
    """Test suite for TimeoutError exception."""

    def test_timeout_error_creation(self):
        """Test creating a TimeoutError."""
        error = TimeoutError("Request timed out after 10 seconds")

        assert str(error) == "Request timed out after 10 seconds"
        assert isinstance(error, ConnectivityCheckError)

    def test_timeout_error_inheritance(self):
        """Test that TimeoutError inherits from ConnectivityCheckError."""
        error = TimeoutError("Timeout")

        assert isinstance(error, ConnectivityCheckError)
        # Note: This is our custom TimeoutError, not the built-in one
        assert isinstance(error, Exception)


class TestNetworkError:
    """Test suite for NetworkError exception."""

    def test_network_error_creation(self):
        """Test creating a NetworkError."""
        error = NetworkError("Connection refused")

        assert str(error) == "Connection refused"
        assert isinstance(error, ConnectivityCheckError)

    def test_network_error_inheritance(self):
        """Test that NetworkError inherits from ConnectivityCheckError."""
        error = NetworkError("Network failed")

        assert isinstance(error, ConnectivityCheckError)
        assert isinstance(error, Exception)


class TestServiceUnavailableError:
    """Test suite for ServiceUnavailableError exception."""

    def test_service_unavailable_error_creation(self):
        """Test creating a ServiceUnavailableError."""
        error = ServiceUnavailableError("Service returned 500")

        assert str(error) == "Service returned 500"
        assert isinstance(error, ConnectivityCheckError)

    def test_service_unavailable_error_inheritance(self):
        """Test that ServiceUnavailableError inherits from ConnectivityCheckError."""
        error = ServiceUnavailableError("5xx error")

        assert isinstance(error, ConnectivityCheckError)
        assert isinstance(error, Exception)
