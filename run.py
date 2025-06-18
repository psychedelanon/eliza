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
from typing import Optional, Tuple
import importlib

from agents.base import TwitterAgent
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

AGENT_CLASS_MAP: dict[str, str] = {
    "AgentLoreMaster": "agents.agent_lore_master:AgentLoreMaster",
    "AgentHypeBeast": "agents.agent_hype_beast:AgentHypeBeast",
    "AgentCynical": "agents.agent_cynical:AgentCynical",
    "AgentSage": "agents.agent_sage:AgentSage",
}

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


def init_agents(configs, dry_run=False):
    agents = []
    for idx, (name, cfg) in enumerate(configs.items(), 1):
        dotted = AGENT_CLASS_MAP.get(name)
        if not dotted:
            log.warning("%s not in registry", name)
            continue
        module_path, cls_name = dotted.split(":")
        cls = getattr(importlib.import_module(module_path), cls_name)
        agent = cls(idx=idx, name=name,
                    personality=cfg.get("persona", ""),
                    dry_run=dry_run)
        agents.append(agent)
    return agents


async def job_crypto_post():
    """Daily job to post BTC vs BITCOIN comparison."""
    agent2 = next(a for a in agent_runtimes if a.agent.name == "AgentHypeBeast")
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

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
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
    return parser.parse_args()

def load_configs() -> dict:
    """Load agent configurations from YAML."""
    config_path = Path("configs/agents.yaml")
    if not config_path.exists():
        log.warning("Agent config %s not found", config_path)
        return {}
    with open(config_path) as f:
        return yaml.safe_load(f) or {}

async def main() -> None:
    """Main entry point."""
    args = parse_args()
    configs = load_configs()
    
    if args.dry_run:
        print("dry run mode")
    
    if args.agent:
        agent_names = [a.strip() for a in args.agent.split(",") if a.strip()]
        filtered_configs = {k: v for k, v in configs.items() if k in agent_names}
    else:
        filtered_configs = configs

    agents = init_agents(filtered_configs, dry_run=args.dry_run)
    for agent in agents:
        print(f"{agent.name} running in {'dry run' if args.dry_run else 'live'} mode")
    for agent in agents:
        for peer in agents:
            if peer is not agent:
                await agent.follow(peer.name, dry_run=args.dry_run)
    
    if not agents:
        print(f"No agents found matching {args.agent}")
        return
        
    runtimes = [
        AgentRuntime(
            agent,
            dry_run=args.dry_run,
            schedule_cron=filtered_configs.get(agent.name, {}).get("schedule_cron"),
        )
        for agent in agents
    ]

    if args.once:
        await asyncio.gather(*(rt.periodic_post() for rt in runtimes))
        return

    sched = build_scheduler(runtimes)
    sched.start()
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())
