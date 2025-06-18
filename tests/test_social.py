import asyncio
import types

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


def test_amplify_actions(monkeypatch):
    bot = TwitterAgent(idx=4, name="Agent4", personality="GremlinGM", dry_run=True)
    peer = TwitterAgent(idx=5, name="Agent5", personality="GremlinMeme", dry_run=True)
    bot.client = DummyClient()
    peer.client = DummyClient()

    monkeypatch.setattr(social, "AMPLIFICATIONS_TOTAL", DummyCounter())
    monkeypatch.setattr(social.llm, "complete", lambda *_a, **_k: "ok")
    monkeypatch.setattr(social.random, "sample", lambda seq, k: seq[:k])
    monkeypatch.setattr(social.random, "choice", lambda seq: seq[0])
    monkeypatch.setattr(social.asyncio, "sleep", lambda *_a, **_k: None)

    asyncio.run(social.amplify(bot, [peer], dry=False))

    assert bot.client.liked or bot.client.retweeted or bot.client.quoted or bot.client.replied

