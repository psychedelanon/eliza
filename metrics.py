"""Prometheus metrics helpers."""
from __future__ import annotations

import time
from typing import Optional

from prometheus_client import Counter, Histogram, start_http_server


class CounterWrapper:
    """Wrapper exposing ``inc``, ``set`` and ``get`` for testing."""

    def __init__(self, name: str, description: str) -> None:
        self._counter = Counter(name, description)
        self._value = 0

    def inc(self, amount: int = 1) -> None:
        self._counter.inc(amount)
        self._value += amount

    def set(self, value: int) -> None:
        if value > self._value:
            self._counter.inc(value - self._value)
        self._value = value

    def get(self) -> int:
        return self._value


TWEETS_POSTED = CounterWrapper("tweets_posted_total", "Tweets successfully posted")
REPLIES_POSTED = CounterWrapper("replies_posted_total", "Replies successfully posted")
OPENAI_CALLS = CounterWrapper("openai_calls_total", "OpenAI API calls made")
LLM_LATENCY = Histogram("llm_request_seconds", "LLM request latency in seconds")
AMPLIFICATIONS_TOTAL = Counter("eliza_amplifications_total", "Boosts", ["agent", "action"])


def init_metrics(port: int = 8000) -> None:
    """Start Prometheus metrics server on given port."""
    start_http_server(port)
