# CloakProcessing Python SDK

Typed, Pythonic access to the CloakProcessing anonymous media API (watermarking, resizing, WebP/WebM conversion).

## Installation

```bash
pip install cloakprocessing
```

Python 3.9+ is supported.

## Quickstart (sync)

```python
from cloakprocessing import CloakProcessingClient, ResizeOptions

with CloakProcessingClient(api_key="YOUR_API_KEY") as client:
    job = client.create_image_job(
        source_url="https://example.com/input.jpg",
        resize=ResizeOptions(width=1200, fit="cover"),
        strip_metadata=True,
    )
    status = client.get_job_status(job.job_id)
    print(status.status, status.output)
```

## Async example

```python
import asyncio
from cloakprocessing import AsyncCloakProcessingClient, WatermarkOptions


async def main() -> None:
    async with AsyncCloakProcessingClient(api_key="YOUR_API_KEY") as client:
        job = await client.create_video_job(
            source_url="https://example.com/input.mp4",
            watermark=WatermarkOptions(
                image_url="https://example.com/brand.png",
                position="bottom-right",
                opacity=0.65,
            ),
            output={"bitrate": "2M", "max_duration": 120},
        )
        status = await client.get_job_status(job.job_id)
        print(status)


asyncio.run(main())
```

## API Coverage

- `create_image_job` → `POST /v1/jobs/image`
- `create_video_job` → `POST /v1/jobs/video`
- `create_watermark_job` → `POST /v1/jobs/watermark`
- `create_resize_job` → `POST /v1/jobs/resize`
- `create_metadata_strip_job` → `POST /v1/jobs/metadata-strip`
- `get_job_status` → `GET /v1/jobs/{job-id}`
- `get_token_balance` → `GET /v1/tokens`

Every create method accepts either a typed request model or convenient keyword arguments. The `source_url` keyword is expanded to the required `{"source": {"url": ...}}` structure automatically.

## Models & typing

All request/response objects are Pydantic models with proper field aliases:

- `ResizeOptions`, `WatermarkOptions`, `ImageOutputOptions`, `VideoOutputOptions`
- `ImageJobRequest`, `VideoJobRequest`, `ResizeOnlyRequest`, `WatermarkOnlyRequest`, `BaseJob`
- `JobResponse`, `JobStatus`, `TokenInfo`

Use `.to_api()` to inspect the exact payload sent to the API.

## Error handling

- `APIError` for non-2xx responses (includes `status_code`, `error_code`, and parsed `response_body`).
- `TransportError` for network/transport issues before the API is reached.

```python
from cloakprocessing import APIError, CloakProcessingClient

try:
    CloakProcessingClient(api_key="bad").get_token_balance()
except APIError as exc:
    print(exc.status_code, exc.error_code)
```

## Configuration tips

- `base_url`: override for testing/staging environments.
- `timeout`: per-request timeout (seconds).
- Pass your own `httpx.Client`/`AsyncClient` if you need custom transports, retries, or proxies.

## Local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"  # optionally add your own extras
```

Publish to PyPI via `python -m build` then `twine upload dist/*`.
