import asyncio
import logging
import logging.config
import os
import argparse
import random
import yaml
from dotenv import load_dotenv
import importlib.resources
import importlib.util
import sys
import json
from pathlib import Path
from datetime import time as dtime, timezone

from agents.base import TwitterAgent
from agents.agent2 import Agent2
from scheduler.tasks import AgentRuntime, build_scheduler
from metrics import init_metrics
from apscheduler.schedulers.asyncio import AsyncIOScheduler

class SafeJsonFormatter(logging.Formatter):
    """JSON formatter that safely handles missing agent/event fields."""
    def format(self, record):
        # Ensure these fields exist in the record
        if not hasattr(record, "agent"):
            record.agent = None
        if not hasattr(record, "event"):
            record.event = None
        return super().format(record)

load_dotenv()

ROOT = Path(__file__).resolve().parent
vendor_qf = ROOT / "vendor" / "blacksmith_forge" / "quickfire.py"
if vendor_qf.exists():
    spec = importlib.util.spec_from_file_location("blacksmith_forge.quickfire", vendor_qf)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    sys.modules["blacksmith_forge.quickfire"] = module
with open(ROOT / "config" / "logging.yaml") as f:
    config = yaml.safe_load(f)
    # Replace the default formatter with our safe one
    for handler in config.get("handlers", {}).values():
        if "formatter" in handler:
            formatter_config = config["formatters"][handler["formatter"]]
            handler["class"] = "logging.StreamHandler"
            handler["formatter"] = "safe_json"
    config["formatters"]["safe_json"] = {
        "()": SafeJsonFormatter,
        "format": config["formatters"].get("default", {}).get("format", "%(message)s")
    }

logging.config.dictConfig(config)

# Silence noisy third-party libraries
logging.getLogger("httpcore").setLevel(logging.INFO)
logging.getLogger("httpx").setLevel(logging.INFO)
logging.getLogger("openai").setLevel(logging.INFO)
logging.getLogger("matplotlib").setLevel(logging.WARNING)
logging.getLogger("fontTools").setLevel(logging.WARNING)

# Now it's safe to emit the first log line
log = logging.getLogger("runner")
log.debug("Environment loaded")

REPLY_DELAY_MIN = int(os.getenv("REPLY_DELAY_MIN", "5"))
REPLY_DELAY_MAX = int(os.getenv("REPLY_DELAY_MAX", "20"))

AGENT_CONFIG_PATH = os.getenv("AGENT_CONFIG", "configs/agents.yaml")


def _has_creds(idx: int) -> bool:
    prefix = f"TWITTER_AGENT{idx}_"
    keys = ["API_KEY", "API_SECRET", "ACCESS_TOKEN", "ACCESS_SECRET"]
    return all(os.getenv(prefix + k) for k in keys)


def load_agent_configs(path: str = AGENT_CONFIG_PATH) -> dict:
    if not os.path.exists(path):
        log.warning("Agent config %s not found", path)
        return {}
    with open(path) as f:
        return yaml.safe_load(f) or {}


def init_agents(configs: dict, dry_run: bool = False):
    agents = []
    for name, cfg in configs.items():
        try:
            idx = int(name.replace("Agent", ""))
        except ValueError:
            log.warning("Invalid agent name %s", name)
            continue
        if not _has_creds(idx):
            if dry_run:
                log.info("%s using dry run (no creds)", name)
            else:
                log.info("%s skipped - no creds", name)
                continue
        
        # Use custom agent classes when available
        if name == "Agent1":
            from agents.agent1 import Agent1
            agent = Agent1(idx=idx, name=name, personality=cfg.get("persona", ""), dry_run=dry_run)
        elif name == "Agent2":
            from agents.agent2 import Agent2
            agent = Agent2(idx=idx, name=name, personality=cfg.get("persona", ""), dry_run=dry_run)
        else:
            agent = TwitterAgent(idx=idx, name=name, personality=cfg.get("persona", ""), dry_run=dry_run)
        
        agents.append(agent)
    return agents


async def job_crypto_post():
    """Daily job to post BTC vs BITCOIN comparison."""
    agent2 = next(a for a in agent_runtimes if a.agent.name == "Agent2")
    text, img_path = agent2.agent.craft_post()
    tweet_id = agent2.agent.post((text, img_path), dry_run=args.dry_run)
    if tweet_id != -1:
        log.info(
            "crypto post",
            extra={
                "agent": agent2.agent.name,
                "event": "crypto_post",
                "post_id": tweet_id,
                "text": text,
            },
        )

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="run scheduled jobs once then exit")
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
    parser.add_argument(
        "--agent",
        help="comma-separated agent names to run",
    )
    args = parser.parse_args()

    if os.getenv("METRICS_ENABLE", "false").lower() == "true":
        init_metrics(int(os.getenv("METRICS_PORT", "8000")))

    configs = load_agent_configs()
    if args.dry_run:
        log.info("dry run mode", extra={"event": "dry_run"})

    agent_filter = None
    if args.agent:
        agent_filter = {name.strip() for name in args.agent.split(',') if name.strip()}

    agent_runtimes = [
        AgentRuntime(
            a,
            dry_run=args.dry_run,
            daily_job=a.name == "Agent2",
        )
        for a in init_agents(configs, dry_run=args.dry_run)
        if not agent_filter or a.name in agent_filter
    ]

    if args.demo or args.agent and "Agent2" in (agent_filter or {}):
        for rt in agent_runtimes:
            text, img_path = rt.agent.craft_post()
            tweet_id = rt.agent.post((text, img_path), dry_run=args.dry_run)
            log.info(
                "demo post",
                extra={
                    "agent": rt.agent.name,
                    "event": "demo_post",
                    "post_id": tweet_id,
                    "text": text,
                },
            )
            print(json.dumps({"event": "demo_post", "agent": rt.agent.name}))
            if tweet_id != -1 and not args.agent:  # Only do replies if not testing specific agent
                await asyncio.sleep(random.uniform(REPLY_DELAY_MIN, REPLY_DELAY_MAX))
                reply_text = rt.agent.craft_reply(text)
                reply_id = rt.agent.reply(
                    tweet_id=tweet_id, text=reply_text, dry_run=args.dry_run
                )
                log.info(
                    "demo reply",
                    extra={"agent": rt.agent.name, "event": "demo_reply", "post_id": reply_id},
                )
                print(json.dumps({"event": "demo_reply", "agent": rt.agent.name}))
        return

    if args.once:
        for rt in agent_runtimes:
            await rt.periodic_post()
        return

    # Set up daily crypto post scheduler
    sched = AsyncIOScheduler(timezone=timezone.utc)
    # Post every day at 21:30 UTC
    sched.add_job(job_crypto_post, trigger="cron", hour=21, minute=30, id="daily_crypto")
    sched.start()

    # Main loop for other agents
    while True:
        for rt in agent_runtimes:
            if rt.agent.name != "Agent2":  # Agent2 is handled by scheduler
                await rt.periodic_post()
        await asyncio.sleep(60)  # Check every minute


if __name__ == "__main__":
    asyncio.run(main())
