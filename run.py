import asyncio
import logging
import logging.config
import os
import argparse
import yaml
from dotenv import load_dotenv
import importlib.resources
import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict, List
import importlib

from agents.base import TwitterAgent

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
    "LoreMaster": "agents.personas:LoreMaster",
    "MemeLord": "agents.personas:MemeLord",
    "AlphaScry": "agents.personas:AlphaScry",
    "GremlinGM": "agents.personas:GremlinGM",
    "SwarmCoordinator": "agents.swarm:SwarmCoordinator",
}

def _has_creds(idx: int) -> bool:
    prefix = f"TWITTER_AGENT{idx}_"
    keys = ["API_KEY", "API_SECRET", "ACCESS_TOKEN", "ACCESS_SECRET"]
    return all(os.getenv(prefix + k) for k in keys)


def load_configs() -> Dict[str, Any]:
    """Load agent configurations from YAML."""
    config_path = Path("configs/agents.yaml")
    if not config_path.exists():
        print(f"Agent config {config_path} not found")
        return {}
    with open(config_path) as f:
        return yaml.safe_load(f) or {}


def init_agents(configs: Dict[str, Any], dry_run: bool = False) -> List[TwitterAgent]:
    agents: List[TwitterAgent] = []
    for idx, (name, cfg) in enumerate(configs.items(), 1):
        dotted = AGENT_CLASS_MAP.get(name)
        if not dotted:
            print(f"{name} not in registry")
            continue
        module_path, cls_name = dotted.split(":")
        cls = getattr(importlib.import_module(module_path), cls_name)
        agent = cls(idx=idx, name=name, personality=cfg.get("persona", ""), dry_run=dry_run)
        if "schedule_cron" in cfg:
            setattr(agent, "schedule_cron", cfg["schedule_cron"])
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
    parser.add_argument("--swarm", action="store_true", help="run SwarmCoordinator and all persona agents")
    parser.add_argument("--dry-run", action="store_true", help="skip API calls and operate without credentials")
    parser.add_argument("--agent", help="comma-separated agent names to run")
    return parser.parse_args()

async def main() -> None:
    """Main entry point."""
    args = parse_args()
    configs = load_configs()
    if args.dry_run:
        print("dry run mode")
    if args.swarm:
        agent_names = ["SwarmCoordinator", "LoreMaster", "MemeLord", "AlphaScry", "GremlinGM"]
        filtered_configs = {k: v for k, v in configs.items() if k in agent_names}
        agents = init_agents(filtered_configs, dry_run=args.dry_run)
        for agent in agents:
            print(f"{agent.name} running in {'dry run' if args.dry_run else 'live'} mode")
        tasks = [asyncio.create_task(agent.run()) for agent in agents]
        await asyncio.gather(*tasks)
        return
    if args.agent:
        agent_names = [a.strip() for a in args.agent.split(",") if a.strip()]
        filtered_configs = {k: v for k, v in configs.items() if k in agent_names}
    else:
        filtered_configs = configs
    agents = init_agents(filtered_configs, dry_run=args.dry_run)
    for agent in agents:
        print(f"{agent.name} running in {'dry run' if args.dry_run else 'live'} mode")
    if not agents:
        print(f"No agents found matching {args.agent}")
        return
    if args.once:
        for agent in agents:
            try:
                text, img = agent.craft_post() if hasattr(agent, 'craft_post') else agent.create_post()
                if text:
                    await agent.post(text, img)
            except Exception as exc:
                print(f"Error posting with {agent.name}: {exc}")
        return
    tasks = [asyncio.create_task(agent.run()) for agent in agents]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger("runner")
    asyncio.run(main())
