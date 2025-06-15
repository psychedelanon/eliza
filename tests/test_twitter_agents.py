import os
import importlib

import pytest

# Ensure the module is importable when tests run
MODULE_PATH = os.path.join(os.path.dirname(__file__), '..', 'scripts')
import sys
sys.path.insert(0, MODULE_PATH)

import twitter_agents


def test_generate_content():
    agent = twitter_agents.TwitterAgent('AgentX', None, None, None, None, 'playful')
    assert 'AgentX says hello in a playful manner.' == agent.generate_content()


def test_create_agents_uses_env(monkeypatch):
    monkeypatch.setenv('TWITTER_AGENT1_API_KEY', 'key')
    monkeypatch.setenv('TWITTER_AGENT1_API_SECRET', 'secret')
    monkeypatch.setenv('TWITTER_AGENT1_ACCESS_TOKEN', 'token')
    monkeypatch.setenv('TWITTER_AGENT1_ACCESS_SECRET', 'toksecret')
    agents = twitter_agents.create_agents(1)
    assert len(agents) == 1
    assert agents[0].api_key == 'key'
    assert agents[0].api_secret == 'secret'
    assert agents[0].access_token == 'token'
    assert agents[0].access_secret == 'toksecret'
