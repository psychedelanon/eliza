import asyncio
import random
import types
import os
import sys
import pathlib
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scheduler.tasks import AgentRuntime
from agents.base import TwitterAgent
from eliza import shared_memory


class DummyAgent(TwitterAgent):
    def __init__(self, name: str):
        super().__init__(idx=1, name=name, personality="p", dry_run=True)
        self.likes = 0
        self.replies = 0

    def create_post(self):
        return "hi", None

    async def post(self, text, img):
        return 1

    async def reply(self, tweet_id, original_text, *, dry_run=None):
        self.replies += 1
        return 2

    async def like(self, tweet_id, *, dry_run=None):
        self.likes += 1


@pytest.mark.asyncio
async def test_cross_engagement(monkeypatch):
    agent = DummyAgent("A")
    rt = AgentRuntime(agent, dry_run=True)
    await shared_memory.write("recent_tweets", [{"id": 10, "agent": "B", "text": "hey"}])

    seq = iter([0.1, 0.4, 0.5, 0.05, 0.33, 0.9, 0.2, 0.8, 0.7, 0.6])
    monkeypatch.setattr(random, "random", lambda: next(seq))
    monkeypatch.setattr(random, "choice", lambda x: x[0])
    monkeypatch.setattr(asyncio, "sleep", lambda *_a, **_k: None)

    runs = 10
    for _ in range(runs):
        await rt._cross_engage()

    assert 2 <= agent.likes + agent.replies <= 4
