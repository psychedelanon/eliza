import os
import sys
import random

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents import agent1


def test_build_prompt(monkeypatch):
    monkeypatch.setattr(random, "sample", lambda corpus, k: corpus[:k])

    prompt = agent1._build_prompt("onions")
    assert "Sproto" in prompt
    assert "1-240" in prompt or "240" in prompt
    assert "onions" in prompt
    assert "Style examples" in prompt
    assert "Tweet:" in prompt
