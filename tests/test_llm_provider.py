import os
import sys
import types

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

from eliza import llm


class DummyClient:
    def __init__(self, api_key=None):
        pass

    class chat:
        class completions:
            @staticmethod
            def create(**_kwargs):
                return types.SimpleNamespace(
                    choices=[types.SimpleNamespace(message=types.SimpleNamespace(content="hi"))]
                )


def test_openai_provider(monkeypatch):
    monkeypatch.delenv("ELIZA_LLM_PROVIDER", raising=False)
    monkeypatch.setitem(sys.modules, "openai", types.SimpleNamespace(OpenAI=lambda api_key=None: DummyClient()))
    monkeypatch.setenv("OPENAI_API_KEY", "key")
    assert llm.complete("hi", model="x", max_tokens=5) == "hi"


def test_anthropic_not_implemented(monkeypatch):
    monkeypatch.setenv("ELIZA_LLM_PROVIDER", "anthropic")
    monkeypatch.setitem(sys.modules, "openai", types.SimpleNamespace(OpenAI=lambda api_key=None: DummyClient()))
    monkeypatch.setenv("OPENAI_API_KEY", "key")
    # Should fall back to OpenAI instead of raising
    result = llm.complete("hi")
    assert result == "hi"
