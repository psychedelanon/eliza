import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import scheduler.tasks as tasks

class DummyAgent:
    def __init__(self):
        self.name = "Agent2"
        self.post_args = None

    def post(self, args, dry_run=False):
        self.post_args = args
        return 1

class DummyRuntime:
    def __init__(self):
        self.agent = DummyAgent()
        self.dry_run = True


def test_daily_price_post(monkeypatch):
    monkeypatch.setattr(tasks.prices, "get_prices", lambda: (30000, 0.00123))
    monkeypatch.setattr(tasks.qf, "generate_price_chart", lambda b, h: Path("stub.png"))
    monkeypatch.setenv("MEDIA_ENABLE", "true")

    rt = DummyRuntime()
    asyncio.run(tasks.daily_price_post(rt))

    text, img = rt.agent.post_args
    assert "30000" in text.replace(",", "")
    assert "0.00123" in text
    assert img == Path("stub.png")
