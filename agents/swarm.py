import asyncio
import random
import logging
from dataclasses import dataclass
from typing import List

from .base import TwitterAgent
from eliza import shared_memory

log = logging.getLogger("swarm")


@dataclass
class SwarmCoordinator:
    agents: List[TwitterAgent]
    interval: int = 300

    async def fetch_signals(self) -> None:
        # TODO: replace with real API calls
        await shared_memory.write("price_jump", random.random() > 0.8)

    async def instruct_quote(self, agent: TwitterAgent, tweet_id: int) -> None:
        await shared_memory.write("quote_target", {"agent": agent.name, "id": tweet_id})

    async def run(self) -> None:
        while True:
            await self.fetch_signals()
            await asyncio.sleep(self.interval)
