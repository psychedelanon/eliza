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
    model_name = model or ("claude-3-sonnet-20240229" if provider is Provider.ANTHROPIC else _DEFAULT_MODEL)
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
        try:
            import anthropic
        except Exception as exc:  # pragma: no cover - missing optional dep
            raise NotImplementedError("Anthropic provider requires anthropic package") from exc
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise NotImplementedError("ANTHROPIC_API_KEY not set")
        client = anthropic.Anthropic(api_key=api_key)
        start = time.monotonic()
        try:
            resp = client.messages.create(
                model=model or "claude-3-sonnet-20240229",
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
            )
            # Anthropic SDK returns the content as a list of blocks, join them if needed
            if hasattr(resp, 'content') and isinstance(resp.content, list):
                return "".join(block.text for block in resp.content if hasattr(block, 'text')).strip()
            return str(resp.content).strip()
        except Exception as exc:
            # Fallback to Claude Haiku if Sonnet fails
            print(f"Claude Sonnet failed: {exc}. Falling back to Claude Haiku.")
            return complete(prompt, model="claude-3-haiku-20240307", temperature=temperature, max_tokens=max_tokens)
        finally:
            LLM_LATENCY.observe(time.monotonic() - start)
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
