import asyncio
import random
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scheduler.tasks import AgentRuntime
from agents.base import TwitterAgent
from eliza import shared_memory


class DummyAgent(TwitterAgent):
    def __init__(self, name="test", personality="test"):
        super().__init__(name=name, personality=personality, dry_run=True)
        self.posted = False
        self.replied = False

    async def post(self, content):
        self.posted = True
        return 123

    async def reply(self, tweet_id, text):
        self.replied = True
        return 456


@pytest.mark.asyncio
async def test_cross_engagement():
    # Test shared memory operations
    await shared_memory.append_list("recent_tweets", {"id": 10, "agent": "B", "text": "hey"})
    
    # Test latest retrieval
    latest_data = await shared_memory.latest("recent_tweets")
    assert latest_data == {"id": 10, "agent": "B", "text": "hey"}
    
    # Test append list
    await shared_memory.append_list("test_list", "new item")
    latest_item = await shared_memory.latest("test_list")
    assert latest_item == "new item"
