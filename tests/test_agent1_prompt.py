import datetime as dt
import os
import sys
import random

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents import agent1


def test_build_prompt(monkeypatch):
    monkeypatch.setattr(random, "sample", lambda corpus, k: corpus[:k])

    class FakeDT(dt.datetime):
        @classmethod
        def now(cls, tz=None):
            return dt.datetime(2024, 1, 1, tzinfo=dt.timezone.utc)

    monkeypatch.setattr(agent1.dt, "datetime", FakeDT)
    prompt = agent1._build_prompt("onions")
    assert "Sproto" in prompt
    assert "1-240" in prompt or "240" in prompt
    assert "onions" in prompt
    assert "Style examples" in prompt
    assert "Tweet:" in prompt
