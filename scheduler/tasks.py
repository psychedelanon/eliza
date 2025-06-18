import asyncio
import random
import logging
import os
from datetime import datetime, timezone, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from eliza import shared_memory

from agents import prices
import blacksmith_forge.quickfire as qf

log = logging.getLogger("sched")

REPLY_DELAY_MIN = int(os.getenv("REPLY_DELAY_MIN", "5"))
REPLY_DELAY_MAX = int(os.getenv("REPLY_DELAY_MAX", "20"))


class AgentRuntime:
    def __init__(self, agent, dry_run: bool = False, schedule_cron: str | None = None, daily_job: bool = False):
        self.agent = agent
        self.dry_run = dry_run
        self.last_mention_id = None
        self.daily_job = daily_job
        self.schedule_cron = schedule_cron

    async def periodic_post(self) -> None:
        """Post a tweet periodically."""
        if not self.agent:
            return

        try:
            text, img = self.agent.create_post()
            if not text:
                return
            tweet_id = await self.agent.post(text, img)
            if tweet_id and not self.dry_run:
                await shared_memory.append_list(
                    "recent_tweets",
                    {"id": tweet_id, "agent": self.agent.name, "text": text},
                )
                await self.agent.reply(
                    tweet_id=tweet_id,
                    original_text=text,
                    dry_run=self.dry_run,
                )
                await self._cross_engage()
        except Exception as exc:
            log.error(
                "Periodic post failed: %s",
                exc,
                extra={"agent": self.agent.name, "event": "error", "error": str(exc)},
            )

    async def _cross_engage(self) -> None:
        recent = await shared_memory.read("recent_tweets") or []
        others = [t for t in recent if t.get("agent") != self.agent.name]
        if not others or random.random() > 0.3:
            return
        target = random.choice(others)
        await asyncio.sleep(random.uniform(1, 90))
        if random.random() < 0.5:
            await self.agent.like(target["id"], dry_run=self.dry_run)
        else:
            await self.agent.reply(
                tweet_id=target["id"],
                original_text=target.get("text", ""),
                dry_run=self.dry_run,
            )
        log.info(
            "cross engage",
            extra={"agent": self.agent.name, "event": "cross_engage"},
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
        if rt.schedule_cron:
            trigger = CronTrigger.from_crontab(rt.schedule_cron)
        else:
            trigger = IntervalTrigger(minutes=30, start_date=datetime.utcnow(), jitter=120)
        sched.add_job(
            rt.periodic_post,
            trigger=trigger,
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
