import asyncio
import logging.config
from dotenv import load_dotenv

from agents.base import TwitterAgent
from agents.personalities import PERSONALITIES
from scheduler.tasks import AgentRuntime, build_scheduler

load_dotenv()
logging.config.fileConfig("config/logging.yaml", disable_existing_loggers=False)

NUM_AGENTS = 18


def init_agents():
    agents = []
    for idx in range(1, NUM_AGENTS + 1):
        agents.append(
            TwitterAgent(
                idx=idx,
                name=f"Agent{idx}",
                personality=PERSONALITIES[idx - 1],
            )
        )
    return agents


async def main():
    agent_runtimes = [AgentRuntime(a) for a in init_agents()]
    sched = build_scheduler(agent_runtimes)
    sched.start()
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
