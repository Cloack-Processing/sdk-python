from __future__ import annotations

from typing import Optional


class CloakProcessingError(Exception):
    """Base SDK error."""


class APIError(CloakProcessingError):
    """Raised for non-2xx responses."""

    def __init__(
        self,
        message: str,
        status_code: int,
        error_code: Optional[str] = None,
        response_body: Optional[dict] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code
        self.response_body = response_body or {}


class TransportError(CloakProcessingError):
    """Raised when the HTTP client fails before reaching the API."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
