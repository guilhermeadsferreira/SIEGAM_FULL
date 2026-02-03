from __future__ import annotations

import time
from types import TracebackType
from typing import Optional, Type


class Timer:
    def __init__(self) -> None:
        self._start: float = 0.0

    def __enter__(self) -> "Timer":
        self._start = time.time()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        pass

    @property
    def elapsed_seconds(self) -> float:
        return round((time.time() - self._start), 2)
