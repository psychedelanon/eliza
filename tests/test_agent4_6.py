import yaml
from pathlib import Path
import pytest
from agents import agent4

import agents.agent5 as agent5
import agents.agent6 as agent6


class DummyLLM:
    def __init__(self, response):
        self.response = response
        self.prompt = ""

    async def __call__(self, prompt):
        self.prompt = prompt
        return self.response


def _stub_agents():
    return [
        (agent4, agent4.Agent4, "Agent4"),
        (agent5, agent5.Agent5, "Agent5"),
        (agent6, agent6.Agent6, "Agent6"),
    ]


@pytest.mark.asyncio
async def test_create_post_and_tag(monkeypatch):
    llm = DummyLLM("meme response")
    
    # Create agent instance and monkeypatch llm
    agent = agent4.Agent4(name="test", personality="test", dry_run=True)
    monkeypatch.setattr(agent, "llm", llm)
    
    result = await agent.craft_post()
    assert "meme response" in result
    assert "meme" in llm.prompt.lower()


def test_scheduler_entries():
    sched = yaml.safe_load(Path("config/scheduler.yaml").read_text())
    ids = {job["id"] for job in sched.get("jobs", [])}
    assert {"gremlin_gm", "gremlin_meme", "gremlin_lore"}.issubset(ids)

