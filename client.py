from __future__ import annotations

from typing import Any, Dict, Optional, Type, TypeVar

import httpx

from .exceptions import APIError, CloakProcessingError, TransportError
from .models import (
    BaseJob,
    ImageJobRequest,
    JobResponse,
    JobStatus,
    ResizeOnlyRequest,
    TokenInfo,
    VideoJobRequest,
    WatermarkOnlyRequest,
)

RequestT = TypeVar("RequestT", bound=BaseJob)


class CloakProcessingClient:
    """
    Typed client for the CloakProcessing API.

    Usage:
        with CloakProcessingClient(api_key="token") as client:
            job = client.create_image_job(source_url="https://example.com/image.jpg")
            status = client.get_job_status(job.job_id)
    """

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = "https://api.cloakprocessing.com",
        timeout: float = 10.0,
        http_client: Optional[httpx.Client] = None,
    ) -> None:
        if not api_key:
            raise ValueError("api_key is required")
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._client = http_client or httpx.Client(
            base_url=self._base_url, headers=self._default_headers
        )
        self._owns_client = http_client is None

    @property
    def _default_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _post_job(self, path: str, payload: BaseJob) -> JobResponse:
        try:
            response = self._client.post(
                path, json=payload.to_api(), timeout=self._timeout
            )
        except httpx.HTTPError as exc:
            raise TransportError(str(exc)) from exc
        self._raise_for_status(response)
        return JobResponse.model_validate(response.json())

    def create_image_job(
        self,
        *,
        request: Optional[ImageJobRequest] = None,
        **kwargs: Any,
    ) -> JobResponse:
        """
        Create an image job. You can pass a pre-built ImageJobRequest or keyword
        arguments matching its fields (e.g., source_url, resize, watermark).
        """
        job_request = self._coerce_request(ImageJobRequest, request, kwargs)
        return self._post_job("/v1/jobs/image", job_request)

    def create_video_job(
        self,
        *,
        request: Optional[VideoJobRequest] = None,
        **kwargs: Any,
    ) -> JobResponse:
        job_request = self._coerce_request(VideoJobRequest, request, kwargs)
        return self._post_job("/v1/jobs/video", job_request)

    def create_watermark_job(
        self, *, request: Optional[WatermarkOnlyRequest] = None, **kwargs: Any
    ) -> JobResponse:
        job_request = self._coerce_request(WatermarkOnlyRequest, request, kwargs)
        return self._post_job("/v1/jobs/watermark", job_request)

    def create_resize_job(
        self, *, request: Optional[ResizeOnlyRequest] = None, **kwargs: Any
    ) -> JobResponse:
        job_request = self._coerce_request(ResizeOnlyRequest, request, kwargs)
        return self._post_job("/v1/jobs/resize", job_request)

    def create_metadata_strip_job(
        self, *, request: Optional[BaseJob] = None, **kwargs: Any
    ) -> JobResponse:
        job_request = self._coerce_request(BaseJob, request, kwargs)
        return self._post_job("/v1/jobs/metadata-strip", job_request)

    def get_job_status(self, job_id: str) -> JobStatus:
        try:
            response = self._client.get(
                f"/v1/jobs/{job_id}", timeout=self._timeout, headers=self._default_headers
            )
        except httpx.HTTPError as exc:
            raise TransportError(str(exc)) from exc
        self._raise_for_status(response)
        return JobStatus.model_validate(response.json())

    def get_token_balance(self) -> TokenInfo:
        try:
            response = self._client.get(
                "/v1/tokens", timeout=self._timeout, headers=self._default_headers
            )
        except httpx.HTTPError as exc:
            raise TransportError(str(exc)) from exc
        self._raise_for_status(response)
        return TokenInfo.model_validate(response.json())

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> "CloakProcessingClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def _raise_for_status(self, response: httpx.Response) -> None:
        if 200 <= response.status_code < 300:
            return
        try:
            error_body = response.json()
        except ValueError:
            error_body = {}
        error_code = None
        if isinstance(error_body, dict):
            error_code = error_body.get("code") or error_body.get("error")
        message = error_body.get("message") if isinstance(error_body, dict) else ""
        raise APIError(
            message=message or f"API request failed with status {response.status_code}",
            status_code=response.status_code,
            error_code=error_code,
            response_body=error_body if isinstance(error_body, dict) else {},
        )

    def _coerce_request(
        self,
        model: Type[RequestT],
        request: Optional[RequestT],
        kwargs: Dict[str, Any],
    ) -> RequestT:
        if request:
            return request
        # Convenience: allow source_url instead of nested Source model.
        if "source_url" in kwargs and "source" not in kwargs:
            kwargs = dict(kwargs)
            kwargs["source"] = {"url": kwargs.pop("source_url")}
        return model(**kwargs)


class AsyncCloakProcessingClient:
    """Async variant of the CloakProcessing client."""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = "https://api.cloakprocessing.com",
        timeout: float = 10.0,
        http_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        if not api_key:
            raise ValueError("api_key is required")
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._client = http_client or httpx.AsyncClient(
            base_url=self._base_url, headers=self._default_headers
        )
        self._owns_client = http_client is None

    @property
    def _default_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def _post_job(self, path: str, payload: BaseJob) -> JobResponse:
        try:
            response = await self._client.post(
                path, json=payload.to_api(), timeout=self._timeout
            )
        except httpx.HTTPError as exc:
            raise TransportError(str(exc)) from exc
        self._raise_for_status(response)
        return JobResponse.model_validate(response.json())

    async def create_image_job(
        self,
        *,
        request: Optional[ImageJobRequest] = None,
        **kwargs: Any,
    ) -> JobResponse:
        job_request = self._coerce_request(ImageJobRequest, request, kwargs)
        return await self._post_job("/v1/jobs/image", job_request)

    async def create_video_job(
        self,
        *,
        request: Optional[VideoJobRequest] = None,
        **kwargs: Any,
    ) -> JobResponse:
        job_request = self._coerce_request(VideoJobRequest, request, kwargs)
        return await self._post_job("/v1/jobs/video", job_request)

    async def create_watermark_job(
        self, *, request: Optional[WatermarkOnlyRequest] = None, **kwargs: Any
    ) -> JobResponse:
        job_request = self._coerce_request(WatermarkOnlyRequest, request, kwargs)
        return await self._post_job("/v1/jobs/watermark", job_request)

    async def create_resize_job(
        self, *, request: Optional[ResizeOnlyRequest] = None, **kwargs: Any
    ) -> JobResponse:
        job_request = self._coerce_request(ResizeOnlyRequest, request, kwargs)
        return await self._post_job("/v1/jobs/resize", job_request)

    async def create_metadata_strip_job(
        self, *, request: Optional[BaseJob] = None, **kwargs: Any
    ) -> JobResponse:
        job_request = self._coerce_request(BaseJob, request, kwargs)
        return await self._post_job("/v1/jobs/metadata-strip", job_request)

    async def get_job_status(self, job_id: str) -> JobStatus:
        try:
            response = await self._client.get(
                f"/v1/jobs/{job_id}",
                timeout=self._timeout,
                headers=self._default_headers,
            )
        except httpx.HTTPError as exc:
            raise TransportError(str(exc)) from exc
        self._raise_for_status(response)
        return JobStatus.model_validate(response.json())

    async def get_token_balance(self) -> TokenInfo:
        try:
            response = await self._client.get(
                "/v1/tokens", timeout=self._timeout, headers=self._default_headers
            )
        except httpx.HTTPError as exc:
            raise TransportError(str(exc)) from exc
        self._raise_for_status(response)
        return TokenInfo.model_validate(response.json())

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def __aenter__(self) -> "AsyncCloakProcessingClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    def _raise_for_status(self, response: httpx.Response) -> None:
        if 200 <= response.status_code < 300:
            return
        try:
            error_body = response.json()
        except ValueError:
            error_body = {}
        error_code = None
        if isinstance(error_body, dict):
            error_code = error_body.get("code") or error_body.get("error")
        message = error_body.get("message") if isinstance(error_body, dict) else ""
        raise APIError(
            message=message or f"API request failed with status {response.status_code}",
            status_code=response.status_code,
            error_code=error_code,
            response_body=error_body if isinstance(error_body, dict) else {},
        )

    def _coerce_request(
        self,
        model: Type[RequestT],
        request: Optional[RequestT],
        kwargs: Dict[str, Any],
    ) -> RequestT:
        if request:
            return request
        if "source_url" in kwargs and "source" not in kwargs:
            kwargs = dict(kwargs)
            kwargs["source"] = {"url": kwargs.pop("source_url")}
        return model(**kwargs)
