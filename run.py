import asyncio
import logging
import logging.config
import os
import argparse
import random
import yaml
from dotenv import load_dotenv

from agents.base import TwitterAgent
from agents.personalities import PERSONALITIES
from scheduler.tasks import AgentRuntime, build_scheduler

load_dotenv()

with open("config/logging.yaml") as f:
    logging.config.dictConfig(yaml.safe_load(f))

log = logging.getLogger("runner")
log.debug("Environment loaded")

REPLY_DELAY_MIN = int(os.getenv("REPLY_DELAY_MIN", "5"))
REPLY_DELAY_MAX = int(os.getenv("REPLY_DELAY_MAX", "20"))

NUM_AGENTS = int(os.getenv("NUM_AGENTS", "18"))


def _has_creds(idx: int) -> bool:
    prefix = f"TWITTER_AGENT{idx}_"
    keys = ["API_KEY", "API_SECRET", "ACCESS_TOKEN", "ACCESS_SECRET"]
    return all(os.getenv(prefix + k) for k in keys)


def init_agents(dry_run: bool = False):
    agents = []
    for idx in range(1, NUM_AGENTS + 1):
        if not _has_creds(idx):
            if dry_run:
                log.info("Agent%d using dry run (no creds)", idx)
            else:
                log.info("Agent%d skipped - no creds", idx)
                continue
        agents.append(
            TwitterAgent(
                idx=idx,
                name=f"Agent{idx}",
                personality=PERSONALITIES[idx - 1],
                dry_run=dry_run,
            )
        )
    return agents


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="run one cycle and exit")
    parser.add_argument(
        "--demo",
        action="store_true",
        help="post once and self-reply for each agent then exit",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="skip API calls and operate without credentials",
    )
    args = parser.parse_args()

    if args.dry_run:
        log.info("dry run mode", extra={"event": "dry_run"})
    agent_runtimes = [
        AgentRuntime(a, dry_run=args.dry_run) for a in init_agents(dry_run=args.dry_run)
    ]

    if args.demo:
        for rt in agent_runtimes:
            text = rt.agent.craft_post()
            tweet_id = rt.agent.post(text, dry_run=args.dry_run)
            log.info(
                "demo post", 
                extra={
                    "agent": rt.agent.name,
                    "event": "demo_post",
                    "post_id": tweet_id,
                    "text": text,
                },
            )
            if tweet_id != -1:
                await asyncio.sleep(random.uniform(REPLY_DELAY_MIN, REPLY_DELAY_MAX))
                reply_text = rt.agent.craft_reply(text)
                reply_id = rt.agent.reply(
                    tweet_id=tweet_id, text=reply_text, dry_run=args.dry_run
                )
                log.info(
                    "demo reply",
                    extra={
                        "agent": rt.agent.name,
                        "event": "demo_reply",
                        "reply_id": reply_id,
                        "text": reply_text,
                    },
                )
        return

    if args.once:
        for rt in agent_runtimes:
            await rt.periodic_post()
            await rt.monitor_mentions()
        return

    sched = build_scheduler(agent_runtimes)
    sched.start()
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
