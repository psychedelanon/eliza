import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import quickfire


def test_env_overrides_hashtags(monkeypatch):
    monkeypatch.setenv("AQUA_HASHTAGS", "#Foo,#Bar")
    monkeypatch.setattr(quickfire, "_get_openai", lambda: None)
    monkeypatch.setattr(quickfire.random, "choice", lambda seq: seq[0])
    text = quickfire.create_post("demo")
    assert "#Foo" in text

