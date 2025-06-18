#!/usr/bin/env python3
"""
Quick test script for Swarm Quality Boost implementation.
"""

import asyncio
import os
from agents.generator import compose_post, get_engagement_weights
from agents.quality import validate, get_quality_score
from agents.personas import LoreMaster, MemeLord, AlphaScry, GremlinGM

# Set dry-run mode
os.environ["DRY_RUN"] = "true"

async def test_generator():
    """Test the smart post generator."""
    print("=== Testing Smart Post Generator ===")
    
    personas = ["LoreMaster", "MemeLord", "AlphaScry", "GremlinGM"]
    
    for persona in personas:
        # Test regular post
        post = compose_post(persona, dry_run=True)
        print(f"\n{persona} regular post:")
        print(f"  Text: {post}")
        print(f"  Length: {len(post)} chars")
        
        # Test with hot token event
        event = {"type": "new_hot_token", "symbol": "$PEPE", "pct": 420}
        event_post = compose_post(persona, event=event, dry_run=True)
        print(f"\n{persona} with hot token event:")
        print(f"  Text: {event_post}")
        print(f"  Length: {len(event_post)} chars")
        
        # Test quality validation
        is_valid, issues = validate(post)
        score = get_quality_score(post)
        print(f"  Quality: {'PASS' if is_valid else 'FAIL'} (score: {score:.2f})")
        if issues:
            print(f"  Issues: {issues}")

def test_engagement_weights():
    """Test engagement weight distribution."""
    print("\n=== Testing Engagement Weights ===")
    
    personas = ["LoreMaster", "MemeLord", "AlphaScry", "GremlinGM"]
    
    for persona in personas:
        weights = get_engagement_weights(persona)
        print(f"\n{persona}:")
        for action, weight in weights.items():
            print(f"  {action}: {weight:.1%}")

async def test_persona_agents():
    """Test persona agents with async craft_post."""
    print("\n=== Testing Persona Agents ===")
    
    # Create agents
    loremaster = LoreMaster(name="LoreMaster", personality="lore", dry_run=True)
    memelord = MemeLord(name="MemeLord", personality="meme", dry_run=True)
    alphascy = AlphaScry(name="AlphaScry", personality="alpha", dry_run=True)
    gremlin = GremlinGM(name="GremlinGM", personality="chaos", dry_run=True)
    
    agents = [loremaster, memelord, alphascy, gremlin]
    
    for agent in agents:
        try:
            post = await agent.craft_post()
            print(f"\n{agent.name}:")
            print(f"  Text: {post}")
            print(f"  Length: {len(post)} chars")
            
            # Test quality validation
            is_valid, issues = validate(post)
            score = get_quality_score(post)
            print(f"  Quality: {'PASS' if is_valid else 'FAIL'} (score: {score:.2f})")
            if issues:
                print(f"  Issues: {issues}")
        except Exception as e:
            print(f"\n{agent.name} ERROR: {e}")

async def main():
    """Run all tests."""
    print("🧪 Swarm Quality Boost Test Suite")
    print("=" * 50)
    
    # Test generator
    await test_generator()
    
    # Test engagement weights
    test_engagement_weights()
    
    # Test persona agents
    await test_persona_agents()
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")

if __name__ == "__main__":
    asyncio.run(main()) 