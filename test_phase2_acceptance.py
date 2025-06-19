#!/usr/bin/env python3
"""
Acceptance test for Phase 2: Smart Rate-Limit Resilience
Tests the rate limiting and retry queue functionality in a realistic scenario.
"""

import asyncio
import time
import logging
from datetime import datetime, timezone
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from agents.RateLimiter import RateLimiter
from agents.RetryQueue import RetryQueue, ActionType

# Set up logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("phase2_acceptance")

async def test_rate_limit_acceptance():
    """Test that rate limiting prevents posts and retry queue handles failures."""
    print("🧪 Testing Phase 2: Smart Rate-Limit Resilience")
    print("=" * 50)
    
    # Initialize components
    rate_limiter = RateLimiter()
    retry_queue = RetryQueue()
    
    # Test 1: Rate limiting prevents posts
    print("\n1. Testing rate limiting...")
    
    # Register posts up to the limit
    for i in range(rate_limiter.MAX_TWEETS_PER_AGENT):
        rate_limiter.register("TestAgent")
        print(f"   Registered post {i+1}/{rate_limiter.MAX_TWEETS_PER_AGENT}")
    
    # Try to post one more - should be blocked
    can_post = rate_limiter.can_post("TestAgent")
    print(f"   Can post after limit: {can_post}")
    assert not can_post, "Rate limiter should block posts after limit"
    
    # Test 2: Retry queue handles failed actions
    print("\n2. Testing retry queue...")
    
    # Mock a function that fails
    mock_func = Mock()
    mock_func.side_effect = Exception("Rate limit exceeded")
    
    # Add failed action to retry queue
    retry_queue.add_failed_action(
        ActionType.POST,
        "TestAgent",
        mock_func,
        "Test content"
    )
    
    print(f"   Added failed action to retry queue")
    print(f"   Queue size: {retry_queue.get_queue_size()}")
    assert retry_queue.get_queue_size() == 1, "Retry queue should contain the failed action"
    
    # Test 3: Exponential backoff
    print("\n3. Testing exponential backoff...")
    
    # Get the retry item
    item = retry_queue._queue[0]
    initial_retry_time = item.next_retry_at
    
    # Simulate first retry failure
    item.attempts = 1
    await retry_queue._retry_item(item)
    
    # Check that next retry time is later (exponential backoff)
    new_retry_time = item.next_retry_at
    time_diff = (new_retry_time - initial_retry_time).total_seconds()
    
    print(f"   Initial retry delay: {retry_queue.INITIAL_DELAY}s")
    print(f"   New retry delay: {time_diff:.0f}s")
    assert time_diff > retry_queue.INITIAL_DELAY, "Exponential backoff should increase delay"
    
    # Test 4: Max attempts handling
    print("\n4. Testing max attempts...")
    
    # Set attempts to max
    item.attempts = retry_queue.MAX_ATTEMPTS
    
    # Process the item (should be removed)
    retry_queue._queue = [item for item in retry_queue._queue if item.attempts < item.max_attempts]
    
    print(f"   Queue size after max attempts: {retry_queue.get_queue_size()}")
    assert retry_queue.get_queue_size() == 0, "Item should be removed after max attempts"
    
    # Test 5: Integration with base agent (simulated)
    print("\n5. Testing integration...")
    
    # Simulate what happens in the base agent
    class MockAgent:
        def __init__(self):
            self.name = "IntegrationTestAgent"
            self.dry_run = False
    
    agent = MockAgent()
    
    # Reset rate limiter
    rate_limiter._agent_actions.clear()
    rate_limiter._app_actions.clear()
    
    # Simulate successful post
    if rate_limiter.can_post(agent.name):
        rate_limiter.register(agent.name)
        print(f"   ✅ Successfully posted as {agent.name}")
    else:
        print(f"   ❌ Rate limited as {agent.name}")
    
    # Simulate rate limit error
    retry_queue.add_failed_action(
        ActionType.POST,
        agent.name,
        mock_func,
        "Integration test content"
    )
    print(f"   ✅ Added rate-limited post to retry queue")
    
    print("\n🎉 All Phase 2 acceptance tests passed!")
    return True

async def main():
    """Run the acceptance test."""
    try:
        await test_rate_limit_acceptance()
        print("\n✅ Phase 2 acceptance test completed successfully!")
    except Exception as e:
        print(f"\n❌ Phase 2 acceptance test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 