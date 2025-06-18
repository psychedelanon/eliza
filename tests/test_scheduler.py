import os
import sys
import types
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import scheduler.tasks as tasks

class DummyRuntime:
    def __init__(self, name="TestAgent"):
        self.schedule_cron = "*/5 * * * *"
        self.agent = types.SimpleNamespace(name=name)
    async def periodic_post(self):
        pass
    async def monitor_mentions(self):
        pass

def test_build_scheduler_uses_initial_offset(monkeypatch):
    fixed_now = datetime(2024, 1, 1, 0, 0, 0)

    class DummyDateTime(datetime):
        @classmethod
        def utcnow(cls):
            return fixed_now

    monkeypatch.setattr(tasks, "datetime", DummyDateTime)
    monkeypatch.setattr(tasks.random, "randint", lambda a, b: 42)

    rt = DummyRuntime()
    sched = tasks.build_scheduler([rt])
    job = sched.get_job(f"{rt.agent.name}-post")
    expected = (fixed_now + timedelta(seconds=42)).replace(tzinfo=tasks.timezone.utc)
    assert job.next_run_time == expected
