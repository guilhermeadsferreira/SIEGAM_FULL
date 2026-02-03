from __future__ import annotations

from pathlib import Path
from typing import Mapping

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from domain.exceptions import InfrastructureException, NetworkException
from settings import settings


def download_file(
    url: str,
    destination: Path | str,
    *,
    headers: Mapping[str, str] | None = None,
    timeout: float | None = None,
    chunk_size: int = 1024 * 1024,
    max_retries: int = 3,
) -> Path:
    timeout = float(timeout or settings.HTTP_TIMEOUT)

    @retry(
        stop=stop_after_attempt(max_retries),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
        reraise=True,
    )
    def _download_with_retry() -> Path:
        output_path = Path(destination)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with httpx.Client(timeout=timeout) as client:
                with client.stream("GET", url, headers=headers) as response:
                    response.raise_for_status()
                    with output_path.open("wb") as output_file:
                        for chunk in response.iter_bytes(chunk_size):
                            output_file.write(chunk)
            return output_path
        except httpx.HTTPStatusError as e:
            if 400 <= e.response.status_code < 500 and e.response.status_code != 429:
                raise InfrastructureException(
                    f"HTTP error {e.response.status_code} for {url}: {e}"
                ) from e
            raise NetworkException(f"HTTP error for {url}: {e}") from e
        except httpx.RequestError as e:
            raise NetworkException(f"Request error for {url}: {e}") from e
        except Exception as e:
            raise InfrastructureException(f"Unexpected error for {url}: {e}") from e

    return _download_with_retry()
