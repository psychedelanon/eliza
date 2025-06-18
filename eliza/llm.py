from __future__ import annotations

import os
import time
from enum import Enum
from typing import Optional, AsyncGenerator

from metrics import OPENAI_CALLS, LLM_LATENCY

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()


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
        print(f"Warning: Unsupported provider: {value}, falling back to OpenAI")
        return Provider.OPENAI


def complete(
    prompt: str,
    *,
    model: Optional[str] = None,
    temperature: float = 0.8,
    max_tokens: int = 120,
    force_provider: Optional[Provider] = None,
) -> str:
    """Return a completion for *prompt* using the configured provider."""
    provider = force_provider or _get_provider()
    model_name = model or _DEFAULT_MODEL
    print(f"LLM provider = {provider}, model = {model_name}")

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
        # Fallback to OpenAI if Anthropic fails
        print("Warning: Anthropic provider not available, falling back to OpenAI")
        return complete(prompt, model=model, temperature=temperature, max_tokens=max_tokens, force_provider=Provider.OPENAI)
    raise RuntimeError(f"Unhandled provider: {provider}")


async def complete_stream(
    prompt: str,
    *,
    model: Optional[str] = None,
    temperature: float = 0.8,
    max_tokens: int = 120,
) -> AsyncGenerator[str, None]:
    """Stream a completion for *prompt* using the configured provider."""
    provider = _get_provider()

    if provider is Provider.OPENAI:
        try:
            import openai
        except Exception as exc:
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
                stream=True,
            )
            for chunk in resp:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        finally:
            LLM_LATENCY.observe(time.monotonic() - start)
    elif provider is Provider.ANTHROPIC:
        try:
            import anthropic
        except Exception as exc:
            raise RuntimeError("anthropic package required for ANTHROPIC provider") from exc
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not set")
        client = anthropic.Anthropic(api_key=api_key)
        start = time.monotonic()
        try:
            resp = client.messages.create(
                model=model or "claude-3-sonnet-20240229",
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
                stream=True,
            )
            for chunk in resp:
                if hasattr(chunk, 'content') and chunk.content:
                    yield chunk.content
        finally:
            LLM_LATENCY.observe(time.monotonic() - start)
    else:
        raise RuntimeError(f"Unhandled provider: {provider}")
