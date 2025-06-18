import yaml
from pathlib import Path

import agents.agent4 as agent4
import agents.agent5 as agent5
import agents.agent6 as agent6


class DummyLLM:
    def __init__(self):
        self.prompt = None

    def complete(self, prompt: str, **_kw):
        self.prompt = prompt
        return "hi"


def _stub_agents():
    return [
        (agent4, agent4.Agent4, "Agent4"),
        (agent5, agent5.Agent5, "Agent5"),
        (agent6, agent6.Agent6, "Agent6"),
    ]


def test_create_post_and_tag(monkeypatch):
    llm = DummyLLM()
    for mod, cls, name in _stub_agents():
        monkeypatch.setattr(mod, "llm", llm)
        monkeypatch.setattr(mod.random, "random", lambda: 0.05)
        ag = cls(idx=0, name=name, personality=getattr(cls, "tag"), dry_run=True)
        text, *_ = ag.create_post()
        assert len(text) <= 240
        assert text.endswith("#HarryPotterObamaSonic10Inu")
        monkeypatch.setattr(mod.random, "random", lambda: 0.5)
        text2, *_ = ag.create_post()
        assert "#HarryPotterObamaSonic10Inu" not in text2


def test_scheduler_entries():
    sched = yaml.safe_load(Path("config/scheduler.yaml").read_text())
    ids = {job["id"] for job in sched.get("jobs", [])}
    assert {"gremlin_gm", "gremlin_meme", "gremlin_lore"}.issubset(ids)

