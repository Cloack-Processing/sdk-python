from __future__ import annotations

from typing import Literal, Optional

from pydantic import AnyHttpUrl, BaseModel, Field


class SerializableModel(BaseModel):
    """Base model with API-friendly serialization."""

    model_config = {
        "populate_by_name": True,
        "str_strip_whitespace": True,
        "extra": "forbid",
    }

    def to_api(self) -> dict:
        return self.model_dump(by_alias=True, exclude_none=True)


class Source(SerializableModel):
    url: AnyHttpUrl


class BaseJob(SerializableModel):
    source: Source
    webhook_url: Optional[AnyHttpUrl] = Field(None, alias="webhook-url")
    strip_metadata: Optional[bool] = Field(True, alias="strip-metadata")


class ResizeOptions(SerializableModel):
    width: Optional[int] = None
    height: Optional[int] = None
    fit: Optional[Literal["contain", "cover", "fill"]] = None


class WatermarkOptions(SerializableModel):
    image_url: Optional[AnyHttpUrl] = Field(None, alias="image-url")
    position: Optional[
        Literal["top-left", "top-right", "bottom-left", "bottom-right", "center"]
    ] = None
    opacity: Optional[float] = None
    scale: Optional[float] = None


class ImageOutputOptions(SerializableModel):
    quality: Optional[int] = Field(None, ge=1, le=100, default=80)


class VideoOutputOptions(SerializableModel):
    max_duration: Optional[int] = Field(None, alias="max-duration")
    bitrate: Optional[str] = None


class ImageJobRequest(BaseJob):
    resize: Optional[ResizeOptions] = None
    watermark: Optional[WatermarkOptions] = None
    output: Optional[ImageOutputOptions] = None


class VideoJobRequest(BaseJob):
    resize: Optional[ResizeOptions] = None
    watermark: Optional[WatermarkOptions] = None
    output: Optional[VideoOutputOptions] = None


class WatermarkOnlyRequest(BaseJob):
    watermark: WatermarkOptions


class ResizeOnlyRequest(BaseJob):
    resize: ResizeOptions


class JobResponse(SerializableModel):
    job_id: Optional[str] = Field(None, alias="job-id")
    status: Optional[str] = None
    expires_at: Optional[str] = Field(None, alias="expires-at")


class JobOutput(SerializableModel):
    url: AnyHttpUrl
    size_bytes: Optional[int] = Field(None, alias="size-bytes")
    expires_at: Optional[str] = Field(None, alias="expires-at")


class JobStatus(SerializableModel):
    id: str
    status: Literal["queued", "processing", "completed", "failed"]
    output: Optional[JobOutput] = None


class TokenInfo(SerializableModel):
    balance: int
    unit: Optional[str] = None


class ErrorModel(SerializableModel):
    code: Optional[str] = None
    message: Optional[str] = None
