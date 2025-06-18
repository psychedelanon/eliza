import asyncio
import types
import pytest

from agents import social
from agents.base import TwitterAgent


class DummyClient:
    def __init__(self):
        self.liked = False
        self.retweeted = False
        self.quoted = False
        self.replied = False

    def user_timeline(self, count=1):
        tweet = types.SimpleNamespace(id=123)
        return [tweet]

    def like(self, tweet_id):
        self.liked = True

    def retweet(self, tweet_id):
        self.retweeted = True

    def create_tweet(self, **kwargs):
        if "quote_tweet_id" in kwargs:
            self.quoted = True
        if "in_reply_to_tweet_id" in kwargs:
            self.replied = True
        return types.SimpleNamespace(data={"id": 456})


class DummyCounter:
    def __init__(self):
        self.labels_called = []

    def labels(self, agent, action):
        def inc():
            self.labels_called.append((agent, action))
        return types.SimpleNamespace(inc=inc)


@pytest.mark.asyncio
async def test_amplify_actions(monkeypatch):
    bot = TwitterAgent(name="Agent4", personality="GremlinGM", dry_run=True)
    peer = TwitterAgent(name="Agent5", personality="GremlinMeme", dry_run=True)
    bot.client = DummyClient()
    peer.client = DummyClient()
    peer.last_post_id = 123  # Set a last_post_id so amplify has something to work with

    monkeypatch.setattr(social, "AMPLIFICATIONS_TOTAL", DummyCounter())
    monkeypatch.setattr(bot, "llm", lambda *_a, **_k: "ok")
    monkeypatch.setattr(social.random, "sample", lambda seq, k: seq[:k])
    monkeypatch.setattr(social.random, "choice", lambda seq: seq[0])
    
    # Mock asyncio.sleep to return a proper coroutine
    async def mock_sleep(secs):
        pass
    monkeypatch.setattr(social.asyncio, "sleep", mock_sleep)

    await social.amplify(bot, [peer], dry=False)

    assert bot.client.liked or bot.client.retweeted or bot.client.quoted or bot.client.replied

