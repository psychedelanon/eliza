import os
import sys
import pytest
import types

sys.modules.setdefault(
    "tweepy",
    types.SimpleNamespace(
        OAuth1UserHandler=type(
            "OAuth1UserHandler",
            (),
            {"__init__": lambda self, *a, **k: None},
        ),
        API=type(
            "API",
            (),
            {
                "__init__": lambda self, *a, **k: None,
                "mentions_timeline": lambda *a, **k: [],
            },
        ),
        Client=type(
            "Client",
            (),
            {
                "__init__": lambda self, *a, **k: None,
                "create_tweet": lambda self, **_k: types.SimpleNamespace(data={"id": 123}),
            },
        ),
        TweepyException=Exception,
    ),
)
sys.modules.setdefault(
    "tenacity",
    types.SimpleNamespace(
        retry=lambda **_kwargs: (lambda f: f),
        wait_random_exponential=lambda **_kwargs: None,
        stop_after_attempt=lambda *_args, **_kwargs: None,
    ),
)

# Ensure module import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.base import TwitterAgent


@pytest.fixture(params=["--once"])
def once_mode(request):
    return request.param


def test_craft_post():
    agent = TwitterAgent(
        idx=1,
        name="AgentX",
        personality="playful",
        api_key="k",
        api_secret="s",
        access_token="t",
        access_secret="ts",
    )
    assert agent.craft_post() == "AgentX says hello in a playful manner."


def test_env_credentials(monkeypatch):
    monkeypatch.setenv("TWITTER_AGENT1_API_KEY", "key")
    monkeypatch.setenv("TWITTER_AGENT1_API_SECRET", "secret")
    monkeypatch.setenv("TWITTER_AGENT1_ACCESS_TOKEN", "token")
    monkeypatch.setenv("TWITTER_AGENT1_ACCESS_SECRET", "toksecret")
    agent = TwitterAgent(idx=1, name="Agent1", personality="test")
    assert agent.api_key == "key"
    assert agent.api_secret == "secret"
    assert agent.access_token == "token"
    assert agent.access_secret == "toksecret"


def test_post_returns_int(monkeypatch, once_mode):
    agent = TwitterAgent(
        idx=1,
        name="AgentP",
        personality="demo",
        api_key="k",
        api_secret="s",
        access_token="t",
        access_secret="ts",
    )

    class DummyResponse:
        def __init__(self, id):
            self.data = {"id": id}

    class DummyClient:
        def create_tweet(self, **_kwargs):
            return DummyResponse(123)

    agent.client = DummyClient()
    tweet_id = agent.post("hi")
    assert isinstance(tweet_id, int) and tweet_id > 0


def test_dry_run_skips_post_and_reply(monkeypatch):
    agent = TwitterAgent(
        idx=2,
        name="AgentDR",
        personality="demo",
        dry_run=True,
    )

    class DummyClient:
        def __init__(self):
            self.called = False

        def create_tweet(self, **_kwargs):
            self.called = True

    agent.client = DummyClient()
    post_id = agent.post("hi")
    reply_id = agent.reply("reply", 123)

    assert post_id == -1
    assert reply_id == -1
    assert agent.client.called is False
