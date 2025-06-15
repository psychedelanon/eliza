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
                "update_status": lambda *a, **k: None,
                "mentions_timeline": lambda *a, **k: [],
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

    class DummyStatus:
        def __init__(self, id):
            self.id = id

    class DummyClient:
        def update_status(self, **kwargs):
            return DummyStatus(123)

    agent.client = DummyClient()
    tweet_id = agent.post("hi")
    assert isinstance(tweet_id, int) and tweet_id > 0
