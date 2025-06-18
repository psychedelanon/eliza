import asyncio
import random
import logging
from dataclasses import dataclass
from typing import List, Dict
from datetime import datetime, timezone

from .base import TwitterAgent
from .generator import get_trending_tokens
from eliza import shared_memory
from eliza.shared_memory import subscribe

log = logging.getLogger("swarm")


class SwarmCoordinator:
    def __init__(self, idx=0, name=None, personality=None, dry_run=False, agents=None, interval=300, **kwargs):
        self.idx = idx
        self.name = name
        self.personality = personality
        self.dry_run = dry_run
        self.agents = agents if agents is not None else []
        self.interval = interval
        
        # Register as subscriber to events
        subscribe(self.dispatch_event)

    def craft_post(self):
        """Return a tuple of (text, img) for compatibility with base TwitterAgent.run()."""
        return ("SwarmCoordinator monitoring signals...", None)

    async def dispatch_event(self, event: dict) -> None:
        """Dispatch events to appropriate agents with random delays."""
        if event.get("type") == "price_post":
            # Schedule reactions for all persona agents
            for agent in self.agents:
                if hasattr(agent, 'react_to_event') and agent.name in ["LoreMaster", "MemeLord", "AlphaScry", "GremlinGM"]:
                    # Random delay between 30-120 seconds
                    delay = random.uniform(30, 120)
                    asyncio.create_task(self._delayed_reaction(agent, event, delay))
                    
                    log.info(
                        "Scheduled %s reaction to price_post in %.1fs",
                        agent.name,
                        delay,
                        extra={
                            "agent": self.name,
                            "event": "reaction_scheduled",
                            "target_agent": agent.name,
                            "delay": delay
                        }
                    )

    async def _delayed_reaction(self, agent, event: dict, delay: float) -> None:
        """Execute delayed reaction for an agent."""
        await asyncio.sleep(delay)
        
        try:
            await agent.react_to_event(event)
            
            # Increment cross-engagement metrics
            from metrics import CROSS_ENGAGE_TOTAL
            CROSS_ENGAGE_TOTAL.labels(agent=agent.name, action="reply", origin_agent="Agent2").inc()
            
            log.info(
                "%s reacted to price_post from %s",
                agent.name,
                event.get("agent", "unknown"),
                extra={
                    "agent": agent.name,
                    "event": "price_reaction_completed",
                    "origin_agent": event.get("agent", "unknown"),
                    "tweet_id": event.get("tweet_id", 0)
                }
            )
            
        except Exception as e:
            log.error(
                "%s reaction failed: %s",
                agent.name,
                e,
                extra={
                    "agent": agent.name,
                    "event": "reaction_failed",
                    "error": str(e)
                }
            )

    async def fetch_signals(self) -> None:
        """Fetch market signals and trending tokens."""
        # TODO: replace with real API calls
        mem = shared_memory.get_shared_memory()
        mem.publish_event({"type": "price_jump", "value": random.random() > 0.8})
        
        # Generate hot token events
        await self._generate_hot_token_events()

    async def _generate_hot_token_events(self) -> None:
        """Generate fake hot token events for dry-run mode."""
        if not self.dry_run:
            # TODO: Integrate with real DexScreener API
            return
            
        # Generate random hot token events
        if random.random() < 0.3:  # 30% chance of hot token event
            trending_tokens = get_trending_tokens()
            symbol = random.choice(trending_tokens)
            pct_change = random.randint(50, 1000)  # 50% to 1000% pump
            
            event = {
                "type": "new_hot_token",
                "symbol": symbol,
                "pct": pct_change,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "SwarmCoordinator"
            }
            
            # Publish to shared memory
            mem = shared_memory.get_shared_memory()
            mem.publish_event(event)
            
            log.info(
                "Generated hot token event: %s up %d%%",
                symbol,
                pct_change,
                extra={
                    "agent": self.name,
                    "event": "hot_token_generated",
                    "symbol": symbol,
                    "pct_change": pct_change
                }
            )

    async def instruct_quote(self, agent, tweet_id: int) -> None:
        mem = shared_memory.get_shared_memory()
        mem.publish_event({"type": "quote_target", "agent": agent.name, "id": tweet_id})

    async def run(self) -> None:
        """SwarmCoordinator does not post like a persona agent; just runs its own loop."""
        log.info(f"SwarmCoordinator.run() called for {self.name}")
        while True:
            await self.fetch_signals()
            await asyncio.sleep(self.interval)
