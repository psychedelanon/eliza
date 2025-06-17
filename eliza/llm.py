from __future__ import annotations

import os
import time
from enum import Enum
from typing import Optional

from metrics import OPENAI_CALLS, LLM_LATENCY


class Provider(str, Enum):
    """Supported large language model providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"


_DEFAULT_MODEL = "gpt-4o-mini"


def _get_provider() -> Provider:
    """Return provider selected via ``ELIZA_LLM_PROVIDER`` environment variable."""

    value = os.getenv("ELIZA_LLM_PROVIDER", Provider.OPENAI.value).lower()
    try:
        return Provider(value)
    except ValueError as exc:  # pragma: no cover - unexpected provider
        raise ValueError(f"Unsupported provider: {value}") from exc


def complete(
    prompt: str,
    *,
    model: Optional[str] = None,
    temperature: float = 0.8,
    max_tokens: int = 120,
) -> str:
    """Return a completion for *prompt* using the configured provider."""

    provider = _get_provider()

    if provider is Provider.OPENAI:
        try:
            import openai
        except Exception as exc:  # pragma: no cover - import error
            raise RuntimeError("openai package required for OPENAI provider") from exc

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set")
        client = openai.OpenAI(api_key=api_key)
        OPENAI_CALLS.inc()
        start = time.monotonic()
        try:
            resp = client.chat.completions.create(
                model=model or _DEFAULT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return resp.choices[0].message.content.strip()
        finally:
            LLM_LATENCY.observe(time.monotonic() - start)
    elif provider is Provider.ANTHROPIC:
        # TODO: integrate anthropic client
        raise NotImplementedError("Anthropic provider not yet implemented")
    raise RuntimeError(f"Unhandled provider: {provider}")
