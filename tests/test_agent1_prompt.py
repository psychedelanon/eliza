import pytest
import random
from agents import agent1

@pytest.mark.asyncio
async def test_build_prompt(monkeypatch):
    monkeypatch.setattr(random, "sample", lambda corpus, k: corpus[:k])
    
    # Create agent instance and monkeypatch llm
    agent = agent1.Agent1(name="test", personality="test", dry_run=True)
    monkeypatch.setattr(agent, "llm", lambda prompt: "Test response")
    
    prompt = await agent._build_prompt("onions")
    assert "onions" in prompt
    assert "chaotic hype gremlin" in prompt.lower()
