import asyncio
import random
import logging
from datetime import datetime, timezone, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

log = logging.getLogger("sched")

class AgentRuntime:
    def __init__(self, agent):
        self.agent = agent
        self.last_mention_id = None

    async def periodic_post(self):
        text = self.agent.craft_post()
        self.agent.post(text)
        await asyncio.sleep(0)

    async def monitor_mentions(self):
        self.last_mention_id = await self.agent.check_mentions(
            since_id=self.last_mention_id
        )
        await asyncio.sleep(0)

def build_scheduler(agent_runtimes):
    sched = AsyncIOScheduler(timezone=timezone.utc)

    for rt in agent_runtimes:
        initial_offset = random.randint(0, 300)
        next_run = datetime.utcnow() + timedelta(seconds=initial_offset)
        sched.add_job(
            rt.periodic_post,
            trigger=IntervalTrigger(minutes=30, start_date=datetime.utcnow(), jitter=120),
            next_run_time=next_run,
            id=f"{rt.agent.name}-post",
        )

        sched.add_job(
            rt.monitor_mentions,
            trigger=IntervalTrigger(minutes=10, jitter=60),
            next_run_time=datetime.utcnow(),
            id=f"{rt.agent.name}-mentions",
        )
    return sched
