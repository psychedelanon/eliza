import asyncio
import logging
import logging.config
import os
import argparse
import yaml
from dotenv import load_dotenv

from agents.base import TwitterAgent
from agents.personalities import PERSONALITIES
from scheduler.tasks import AgentRuntime, build_scheduler

print("\nDEBUG: Current working directory:", os.getcwd())
print("DEBUG: Checking if .env exists:", os.path.exists(".env"))
load_dotenv()
print("DEBUG: All environment variables after load_dotenv:")
for key in os.environ:
    if key.startswith("TWITTER_"):
        print(f"{key}: {'*' * 10 if 'SECRET' in key else os.getenv(key)}")

with open("config/logging.yaml") as f:
    logging.config.dictConfig(yaml.safe_load(f))

log = logging.getLogger("runner")

NUM_AGENTS = 18


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

    agent_runtimes = [AgentRuntime(a) for a in init_agents(dry_run=args.dry_run)]

    if args.demo:
        for rt in agent_runtimes:
            text = rt.agent.craft_post()
            tweet_id = rt.agent.post(text)
            reply_text = rt.agent.craft_post()
            rt.agent.reply(reply_text, tweet_id)
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
