#!/usr/bin/env python3
"""
Trigger immediate posts from all live agents for testing purposes.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.base import TwitterAgent
from agents.agent1 import Agent1
from agents.agent2 import Agent2
from agents.agent3 import Agent3
from agents.agent4 import Agent4

async def trigger_immediate_posts():
    """Trigger immediate posts from all configured agents."""
    
    # Initialize agents
    agents = []
    
    # Agent1 - LoreMaster
    if all([
        os.getenv("TWITTER_AGENT1_API_KEY"),
        os.getenv("TWITTER_AGENT1_API_SECRET"),
        os.getenv("TWITTER_AGENT1_ACCESS_TOKEN"),
        os.getenv("TWITTER_AGENT1_ACCESS_SECRET")
    ]):
        agent1 = Agent1("Agent1", "mystical bitcoin sage", idx=1)
        agents.append(agent1)
        print(f"✅ Agent1 configured")
    else:
        print("❌ Agent1 missing credentials")
    
    # Agent2 - HypeBeast
    if all([
        os.getenv("TWITTER_AGENT2_API_KEY"),
        os.getenv("TWITTER_AGENT2_API_SECRET"),
        os.getenv("TWITTER_AGENT2_ACCESS_TOKEN"),
        os.getenv("TWITTER_AGENT2_ACCESS_SECRET")
    ]):
        agent2 = Agent2("Agent2", "price tracking bot", idx=2)
        agents.append(agent2)
        print(f"✅ Agent2 configured")
    else:
        print("❌ Agent2 missing credentials")
    
    # Agent3 - MemeLord
    if all([
        os.getenv("TWITTER_AGENT3_API_KEY"),
        os.getenv("TWITTER_AGENT3_API_SECRET"),
        os.getenv("TWITTER_AGENT3_ACCESS_TOKEN"),
        os.getenv("TWITTER_AGENT3_ACCESS_SECRET")
    ]):
        agent3 = Agent3("Agent3", "meme master", idx=3)
        agents.append(agent3)
        print(f"✅ Agent3 configured")
    else:
        print("❌ Agent3 missing credentials")
    
    # Agent4 - AlphaScry
    if all([
        os.getenv("TWITTER_AGENT4_API_KEY"),
        os.getenv("TWITTER_AGENT4_API_SECRET"),
        os.getenv("TWITTER_AGENT4_ACCESS_TOKEN"),
        os.getenv("TWITTER_AGENT4_ACCESS_SECRET")
    ]):
        agent4 = Agent4("Agent4", "market analyst", idx=4)
        agents.append(agent4)
        print(f"✅ Agent4 configured")
    else:
        print("❌ Agent4 missing credentials")
    
    if not agents:
        print("❌ No agents configured with valid credentials")
        return
    
    print(f"\n🚀 Triggering immediate posts from {len(agents)} agents...")
    
    # Trigger posts from all agents
    tasks = []
    for agent in agents:
        print(f"📝 Triggering post from {agent.name}...")
        task = asyncio.create_task(trigger_agent_post(agent))
        tasks.append(task)
    
    # Wait for all posts to complete
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Report results
    print(f"\n📊 Results:")
    for i, result in enumerate(results):
        agent_name = agents[i].name
        if isinstance(result, Exception):
            print(f"❌ {agent_name}: {result}")
        else:
            print(f"✅ {agent_name}: Tweet ID {result}")

async def trigger_agent_post(agent):
    """Trigger a single post from an agent."""
    try:
        # Generate content
        if asyncio.iscoroutinefunction(agent.craft_post):
            text, img = await agent.craft_post()
        else:
            text, img = agent.craft_post()
        
        # Post it
        tweet_id = await agent.post((text, img))
        return tweet_id
    except Exception as e:
        raise Exception(f"Failed to post: {e}")

if __name__ == "__main__":
    asyncio.run(trigger_immediate_posts()) 