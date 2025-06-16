import os
import sys
import asyncio
import subprocess
import pytest
import types
import sqlite3
from pathlib import Path

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
                "create_tweet": lambda self, **_k: types.SimpleNamespace(
                    data={"id": 123}
                ),
                "upload_media": lambda self, _path: 456,
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
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.base import TwitterAgent
import quickfire
import blacksmith_forge.quickfire as qf


@pytest.fixture(params=["--once"])
def once_mode(request):
    return request.param


@pytest.fixture(autouse=True)
def stub_quickfire(monkeypatch):
    monkeypatch.setattr(qf, "create_post", lambda persona: "hello world")
    monkeypatch.setattr(
        quickfire,
        "create_reply",
        lambda persona, original: f"reply to {original} in {persona}",
    )


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    import agents.base as base

    monkeypatch.setattr(base, "DB_PATH", tmp_path / "db.sqlite", raising=False)
    base._db = sqlite3.connect(base.DB_PATH)
    base._db.execute(
        "CREATE TABLE IF NOT EXISTS tweets(id INTEGER PRIMARY KEY, text TEXT UNIQUE, ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
    )
    yield
    base._db.close()


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
    text, img = agent.craft_post()
    assert text == "hello world"
    assert img is None


def test_craft_reply():
    agent = TwitterAgent(
        idx=1,
        name="AgentX",
        personality="playful",
        api_key="k",
        api_secret="s",
        access_token="t",
        access_secret="ts",
    )
    assert agent.craft_reply("hi") == "reply to hi in playful"


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
    tweet_id = agent.post(("hi", None))
    assert isinstance(tweet_id, int) and tweet_id > 0


def test_duplicate_guard(monkeypatch, caplog):
    agent = TwitterAgent(
        idx=1,
        name="DupAgent",
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
        def __init__(self):
            self.count = 0

        def create_tweet(self, **_kwargs):
            self.count += 1
            return DummyResponse(200 + self.count)

    agent.client = DummyClient()
    with caplog.at_level("INFO"):
        first = agent.post(("hello", None))
        second = agent.post(("hello", None))
    assert first != -1
    assert second == -1
    events = [getattr(r, "event", None) for r in caplog.records]
    post_count = events.count("post")
    dup_count = events.count("duplicate")
    if post_count != 1 or dup_count != 1:
        for r in caplog.records:
            print(r.__dict__)
    assert post_count == 1
    assert dup_count == 1


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
            self.uploaded = False

        def create_tweet(self, **_kwargs):
            self.called = True

        def upload_media(self, _path):
            self.uploaded = True
            return 789

    agent.client = DummyClient()
    post_id = agent.post(("hi", "img.png"))
    reply_id = agent.reply(tweet_id=123, text="reply")

    assert post_id > 0
    assert reply_id > 0
    assert agent.client.called is False
    assert agent.client.uploaded is False


def test_cli_dry_run_event(tmp_path):
    env = os.environ.copy()
    env.update({"REPLY_DELAY_MIN": "0", "REPLY_DELAY_MAX": "0"})
    env["AGENT_CONFIG"] = str(Path("configs/agents.yaml"))
    result = subprocess.run(
        [sys.executable, "run.py", "--demo", "--dry-run"],
        capture_output=True,
        text=True,
        env=env,
    )
    assert '"event": "dry_run"' in result.stdout + result.stderr


def test_cli_demo_logging(tmp_path):
    env = os.environ.copy()
    env.update({"REPLY_DELAY_MIN": "0", "REPLY_DELAY_MAX": "0"})
    env["AGENT_CONFIG"] = str(Path("configs/agents.yaml"))
    result = subprocess.run(
        [sys.executable, "run.py", "--demo", "--dry-run"],
        capture_output=True,
        text=True,
        env=env,
    )
    out = result.stdout + result.stderr
    assert '"event": "demo_post"' in out
    assert '"event": "demo_reply"' in out
