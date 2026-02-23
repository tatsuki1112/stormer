"""Custom exceptions for connectivity checking.

This module defines the exception hierarchy used across all connectivity checkers.
"""


class ConnectivityCheckError(Exception):
    """Base exception for all connectivity check errors.

    All connectivity-related exceptions inherit from this class,
    allowing users to catch all connectivity errors with a single except clause.
    """

    pass


class AuthenticationError(ConnectivityCheckError):
    """Raised when API credentials are invalid or authentication fails.

    This typically means the API key is incorrect, expired, or lacks
    the necessary permissions.
    """

    pass


class TimeoutError(ConnectivityCheckError):
    """Raised when a service request times out.

    This indicates the service did not respond within the expected time frame.
    Note: This is a custom exception, not the built-in TimeoutError.
    """

    pass


class NetworkError(ConnectivityCheckError):
    """Raised when there's a network connectivity issue.

    This can include connection refused, DNS resolution failures,
    or other network-level problems.
    """

    pass


class ServiceUnavailableError(ConnectivityCheckError):
    """Raised when the service is temporarily unavailable.

    This typically corresponds to HTTP 5xx errors, indicating
    the service itself is having problems.
    """

    pass
