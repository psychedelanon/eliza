import asyncio
import random
import logging
import os
from datetime import datetime, timezone, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from agents import prices
import blacksmith_forge.quickfire as qf

log = logging.getLogger("sched")

REPLY_DELAY_MIN = int(os.getenv("REPLY_DELAY_MIN", "5"))
REPLY_DELAY_MAX = int(os.getenv("REPLY_DELAY_MAX", "20"))


class AgentRuntime:
    def __init__(self, agent, dry_run: bool = False, daily_job: bool = False):
        self.agent = agent
        self.dry_run = dry_run
        self.last_mention_id = None
        self.daily_job = daily_job

    async def periodic_post(self):
        text, img_path = self.agent.craft_post()
        tweet_id = self.agent.post((text, img_path), dry_run=self.dry_run)
        if img_path and not self.dry_run:
            log.info(
                "media ready",
                extra={
                    "agent": self.agent.name,
                    "event": "media_ready",
                    "path": img_path,
                },
            )
        if tweet_id != -1:
            await asyncio.sleep(random.uniform(REPLY_DELAY_MIN, REPLY_DELAY_MAX))
            self.agent.reply(
                tweet_id=tweet_id, original_text=text, dry_run=self.dry_run
            )

    async def monitor_mentions(self):
        self.last_mention_id = await self.agent.check_mentions(
            since_id=self.last_mention_id
        )
        await asyncio.sleep(0)


async def daily_price_post(runtime: "AgentRuntime"):
    btc, hpos = prices.get_prices()
    text = (
        f"Market close snapshot: 1 BTC=${btc:,.0f} — "
        f"1 BITCOIN (HPOS10I)=${hpos:,.6f} 🚀📉"
    )
    img = None
    if os.getenv("MEDIA_ENABLE", "false").lower() == "true":
        try:
            img = qf.generate_price_chart(btc, hpos)
        except Exception as exc:
            log.warning("chart generation failed: %s", exc)
            img = None
    runtime.agent.post((text, img), dry_run=runtime.dry_run)


def build_scheduler(agent_runtimes):
    sched = AsyncIOScheduler(timezone=timezone.utc)

    for rt in agent_runtimes:
        initial_offset = random.randint(0, 300)
        next_run = datetime.utcnow() + timedelta(seconds=initial_offset)
        sched.add_job(
            rt.periodic_post,
            trigger=IntervalTrigger(
                minutes=30, start_date=datetime.utcnow(), jitter=120
            ),
            next_run_time=next_run,
            id=f"{rt.agent.name}-post",
        )

        sched.add_job(
            rt.monitor_mentions,
            trigger=IntervalTrigger(minutes=10, jitter=60),
            next_run_time=datetime.utcnow(),
            id=f"{rt.agent.name}-mentions",
        )
        if getattr(rt, "daily_job", False):
            sched.add_job(
                daily_price_post,
                trigger=CronTrigger.from_crontab("0 21 * * *"),
                args=[rt],
                id=f"{rt.agent.name}-daily",
            )
    return sched
