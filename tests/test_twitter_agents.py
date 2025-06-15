import os
import importlib

import pytest

# Ensure module import
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.base import TwitterAgent


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
