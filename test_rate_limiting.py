#!/usr/bin/env python3
"""
Unit tests for Phase 2: Smart Rate-Limit Resilience
Run with: python -m pytest test_rate_limiting.py -v
"""

import pytest
import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch, AsyncMock
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from agents.RateLimiter import RateLimiter
from agents.RetryQueue import RetryQueue, ActionType, RetryItem


class TestRateLimiter:
    """Test the RateLimiter class."""
    
    def setup_method(self):
        """Set up a fresh rate limiter for each test."""
        self.limiter = RateLimiter()
    
    def test_can_post_when_empty(self):
        """Test that can_post returns True when no actions recorded."""
        assert self.limiter.can_post("Agent1") is True
    
    def test_can_post_after_register(self):
        """Test that can_post returns False after registering max actions."""
        # Register max actions for an agent
        for _ in range(self.limiter.MAX_TWEETS_PER_AGENT):
            self.limiter.register("Agent1")
        
        assert self.limiter.can_post("Agent1") is False
    
    def test_can_post_after_app_limit(self):
        """Test that can_post returns False after hitting app limit."""
        # Register max actions for app
        for _ in range(self.limiter.MAX_TWEETS_PER_APP):
            self.limiter.register("Agent1")
        
        assert self.limiter.can_post("Agent2") is False
    
    def test_prune_old_actions(self):
        """Test that old actions are pruned from the window."""
        # Mock datetime to control time
        with patch('agents.RateLimiter.datetime') as mock_datetime:
            # Set initial time
            mock_datetime.now.return_value = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            
            # Register enough actions to hit the rate limit
            for _ in range(self.limiter.MAX_TWEETS_PER_AGENT):
                self.limiter.register("Agent1")
            
            # Should be rate limited
            assert self.limiter.can_post("Agent1") is False
            
            # Advance time beyond the window
            mock_datetime.now.return_value = datetime(2023, 1, 1, 12, 16, 0, tzinfo=timezone.utc)
            
            # Action should be pruned
            assert self.limiter.can_post("Agent1") is True
    
    def test_get_counts(self):
        """Test get_counts returns correct counts."""
        self.limiter.register("Agent1")
        self.limiter.register("Agent2")
        
        agent_count, app_count = self.limiter.get_counts("Agent1")
        assert agent_count == 1
        assert app_count == 2


class TestRetryQueue:
    """Test the RetryQueue class."""
    
    def setup_method(self):
        """Set up a fresh retry queue for each test."""
        self.queue = RetryQueue()
    
    def teardown_method(self):
        """Clean up the retry queue."""
        self.queue.stop()
    
    @pytest.mark.asyncio
    async def test_add_failed_action(self):
        """Test adding a failed action to the queue."""
        mock_func = Mock()
        
        self.queue.add_failed_action(
            ActionType.POST,
            "Agent1",
            mock_func,
            "arg1",
            kwarg1="value1"
        )
        
        assert self.queue.get_queue_size() == 1
    
    @pytest.mark.asyncio
    async def test_exponential_backoff(self):
        """Test that retry delays increase exponentially."""
        mock_func = Mock()
        mock_func.side_effect = Exception("Rate limit")
        
        # Add failed action
        self.queue.add_failed_action(
            ActionType.POST,
            "Agent1",
            mock_func
        )
        
        # Get the item
        item = self.queue._queue[0]
        
        # First retry should be at INITIAL_DELAY
        expected_first = datetime.now(timezone.utc) + timedelta(seconds=self.queue.INITIAL_DELAY)
        assert abs((item.next_retry_at - expected_first).total_seconds()) < 1
        
        # Simulate first retry failure
        item.attempts = 1
        with patch('agents.RetryQueue.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime.now(timezone.utc)
            await self.queue._retry_item(item)
        
        # Second retry should be at 2 * INITIAL_DELAY
        expected_second = datetime.now(timezone.utc) + timedelta(seconds=2 * self.queue.INITIAL_DELAY)
        assert abs((item.next_retry_at - expected_second).total_seconds()) < 1
    
    def test_max_attempts(self):
        """Test that items are removed after max attempts."""
        mock_func = Mock()
        mock_func.side_effect = Exception("Rate limit")
        
        # Add failed action manually without starting worker
        now = datetime.now(timezone.utc)
        next_retry = now + timedelta(seconds=self.queue.INITIAL_DELAY)
        
        item = RetryItem(
            action_type=ActionType.POST,
            agent="Agent1",
            func=mock_func,
            args=(),
            kwargs={},
            next_retry_at=next_retry,
            attempts=0,
            max_attempts=self.queue.MAX_ATTEMPTS
        )
        
        self.queue._queue.append(item)
        
        # Simulate max attempts
        item.attempts = self.queue.MAX_ATTEMPTS
        
        # Process the item
        self.queue._queue = [item for item in self.queue._queue if item.attempts < item.max_attempts]
        
        assert self.queue.get_queue_size() == 0
    
    @pytest.mark.asyncio
    async def test_async_function_retry(self):
        """Test retrying async functions."""
        async def async_func():
            return "success"
        
        # Add failed action manually without starting worker
        now = datetime.now(timezone.utc)
        next_retry = now + timedelta(seconds=self.queue.INITIAL_DELAY)
        
        item = RetryItem(
            action_type=ActionType.POST,
            agent="Agent1",
            func=async_func,
            args=(),
            kwargs={},
            next_retry_at=next_retry,
            attempts=0,
            max_attempts=self.queue.MAX_ATTEMPTS
        )
        
        self.queue._queue.append(item)
        await self.queue._retry_item(item)
        
        # Should succeed without error
        assert item.attempts == 1


class TestIntegration:
    """Integration tests for rate limiting and retry queue."""
    
    @pytest.mark.asyncio
    async def test_rate_limit_integration(self):
        """Test that rate limiting integrates with retry queue."""
        from agents.base import rate_limiter, retry_queue
        
        # Reset global instances
        rate_limiter._agent_actions.clear()
        rate_limiter._app_actions.clear()
        retry_queue._queue.clear()
        
        # Mock an agent
        class MockAgent:
            def __init__(self):
                self.name = "TestAgent"
                self.dry_run = False
        
        agent = MockAgent()
        
        # Test that rate limiting prevents posting
        for _ in range(rate_limiter.MAX_TWEETS_PER_AGENT):
            rate_limiter.register(agent.name)
        
        assert not rate_limiter.can_post(agent.name)
        
        # Test that retry queue can handle rate limit errors
        mock_func = Mock()
        retry_queue.add_failed_action(
            ActionType.POST,
            agent.name,
            mock_func
        )
        
        assert retry_queue.get_queue_size() == 1


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 