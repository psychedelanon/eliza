#!/usr/bin/env python3
"""
Test script to verify startup delay and cron scheduling.
Run with: python test_startup_delay.py
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from agents.base import TwitterAgent
from agents.agent1 import Agent1
from agents.agent2 import Agent2
from agents.agent3 import Agent3
from agents.agent4 import Agent4

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class MockTwitterClient:
    """Mock Twitter client that logs instead of posting."""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.post_count = 0
    
    def create_tweet(self, text: str, **kwargs):
        self.post_count += 1
        logging.info(f"[MOCK] {self.agent_name} would post: {text[:50]}...")
        return type('MockResponse', (), {'data': {'id': 12345 + self.post_count}})()
    
    def like(self, tweet_id: int):
        logging.info(f"[MOCK] {self.agent_name} would like tweet {tweet_id}")
    
    def retweet(self, tweet_id: int):
        logging.info(f"[MOCK] {self.agent_name} would retweet {tweet_id}")
    
    def bookmark(self, tweet_id: int):
        logging.info(f"[MOCK] {self.agent_name} would bookmark {tweet_id}")

class MockAgent(TwitterAgent):
    """Mock agent that uses mock Twitter client."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = MockTwitterClient(self.name)
        self.api_v1 = self.client  # For compatibility
    
    def craft_post(self):
        """Simple mock post."""
        return f"Mock post from {self.name} at {datetime.now().strftime('%H:%M:%S')}", None

async def test_startup_delay():
    """Test that agents respect startup delay."""
    logging.info("=== Testing Startup Delay ===")
    
    # Create mock agents with different schedules
    agents = [
        Agent1(idx=1, name="Agent1", personality="test", dry_run=True),
        Agent2(idx=2, name="Agent2", personality="test", dry_run=True),
        Agent3(idx=3, name="Agent3", personality="test", dry_run=True),
        Agent4(idx=4, name="Agent4", personality="test", dry_run=True),
    ]
    
    # Set schedule_cron after initialization
    agents[0].schedule_cron = "*/20 * * * *"  # Agent1
    agents[1].schedule_cron = "0,30 * * * *"  # Agent2
    agents[2].schedule_cron = "*/45 * * * *"  # Agent3
    agents[3].schedule_cron = "*/60 * * * *"  # Agent4
    
    # Start all agents
    tasks = []
    for agent in agents:
        logging.info(f"Starting {agent.name}")
        task = asyncio.create_task(agent.run())
        tasks.append(task)
    
    # Let them run for 2 minutes
    logging.info("Running agents for 2 minutes...")
    await asyncio.sleep(120)
    
    # Cancel all tasks
    for task in tasks:
        task.cancel()
    
    # Wait for cancellation
    await asyncio.gather(*tasks, return_exceptions=True)
    
    logging.info("=== Test Complete ===")

if __name__ == "__main__":
    asyncio.run(test_startup_delay()) 