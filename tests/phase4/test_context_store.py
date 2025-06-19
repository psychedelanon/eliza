#!/usr/bin/env python3
"""
Unit tests for Phase 4: Context Store
Run with: python -m pytest tests/phase4/test_context_store.py -v
"""

import pytest
import time
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from eliza.context.store import ContextStore, ContextEntry


class TestContextStore:
    """Test the context store functionality."""
    
    def setup_method(self):
        """Set up a fresh context store for each test."""
        self.store = ContextStore(max_size=10)  # Small size for testing
    
    def test_context_entry_creation(self):
        """Test creating context entries."""
        entry = ContextEntry(
            agent_id="TestAgent",
            tweet_id=123,
            topic_tags=["crypto_btc", "price_action"],
            timestamp=time.time()
        )
        
        assert entry.agent_id == "TestAgent"
        assert entry.tweet_id == 123
        assert entry.topic_tags == ["crypto_btc", "price_action"]
        assert entry.timestamp > 0
    
    def test_push_and_pull_basic(self):
        """Test basic push and pull functionality."""
        # Push some entries
        self.store.push("Agent1", 123, ["crypto_btc"])
        self.store.push("Agent2", 124, ["meme_culture"])
        self.store.push("Agent1", 125, ["price_action"])
        
        # Pull recent entries
        recent = self.store.pull_last(3)
        
        assert len(recent) == 3
        assert recent[-1].tweet_id == 125  # Most recent
        assert recent[0].tweet_id == 123   # Oldest
    
    def test_ring_buffer_overflow(self):
        """Test that buffer overwrites oldest when full."""
        # Fill buffer beyond capacity
        for i in range(15):  # Buffer size is 10
            self.store.push(f"Agent{i}", 100 + i, ["test"])
        
        recent = self.store.pull_last(15)
        
        # Should only have last 10 entries
        assert len(recent) == 10
        assert recent[0].tweet_id == 105  # Oldest remaining
        assert recent[-1].tweet_id == 114  # Most recent
    
    def test_last_topic_by_agent(self):
        """Test getting last topic for specific agent."""
        # Push entries for different agents
        self.store.push("Agent1", 123, ["crypto_btc", "price_action"])
        self.store.push("Agent2", 124, ["meme_culture"])
        self.store.push("Agent1", 125, ["market_sentiment"])
        
        # Check last topic for each agent
        assert self.store.last_topic_by_agent("Agent1") == "market_sentiment"
        assert self.store.last_topic_by_agent("Agent2") == "meme_culture"
        assert self.store.last_topic_by_agent("Agent3") is None  # No entries
    
    def test_get_recent_by_agent(self):
        """Test getting recent entries for specific agent."""
        # Push mixed entries
        self.store.push("Agent1", 123, ["crypto_btc"])
        self.store.push("Agent2", 124, ["meme_culture"])
        self.store.push("Agent1", 125, ["price_action"])
        self.store.push("Agent1", 126, ["market_sentiment"])
        
        # Get recent for Agent1
        agent1_recent = self.store.get_recent_by_agent("Agent1", 2)
        
        assert len(agent1_recent) == 2
        assert agent1_recent[0].tweet_id == 125
        assert agent1_recent[1].tweet_id == 126
    
    def test_get_stats(self):
        """Test getting store statistics."""
        # Add some entries
        self.store.push("Agent1", 123, ["crypto_btc"])
        self.store.push("Agent2", 124, ["meme_culture"])
        
        stats = self.store.get_stats()
        
        assert stats["buffer_size"] == 2
        assert stats["max_size"] == 10
        assert stats["agent_count"] == 2
        assert stats["redis_enabled"] is False
    
    def test_context_entry_serialization(self):
        """Test context entry to/from dict conversion."""
        entry = ContextEntry(
            agent_id="TestAgent",
            tweet_id=123,
            topic_tags=["crypto_btc", "price_action"],
            timestamp=time.time(),
            text="Test tweet text"
        )
        
        # Convert to dict and back
        entry_dict = entry.to_dict()
        reconstructed = ContextEntry.from_dict(entry_dict)
        
        assert reconstructed.agent_id == entry.agent_id
        assert reconstructed.tweet_id == entry.tweet_id
        assert reconstructed.topic_tags == entry.topic_tags
        assert reconstructed.timestamp == entry.timestamp
        assert reconstructed.text == entry.text
    
    @pytest.mark.skipif(not hasattr(pytest, 'importorskip'), reason="Redis not available")
    def test_redis_mode_init(self):
        """Test Redis mode initialization (requires Redis)."""
        try:
            import redis
            # Mock Redis URL
            with patch.dict('os.environ', {'REDIS_URL': 'redis://localhost:6379'}):
                with patch('redis.from_url') as mock_redis:
                    mock_client = Mock()
                    mock_redis.return_value = mock_client
                    
                    store = ContextStore()
                    
                    assert store._redis_client == mock_client
                    mock_redis.assert_called_once()
                    mock_client.ping.assert_called_once()
        except ImportError:
            pytest.skip("Redis not available for testing")
    
    def test_push_with_long_text(self):
        """Test pushing entries with long text (should be truncated)."""
        long_text = "A" * 500  # Very long text
        
        self.store.push("Agent1", 123, ["test"], text=long_text)
        
        recent = self.store.pull_last(1)
        assert len(recent[0].text) <= 200  # Should be truncated
    
    def test_agent_topics_limit(self):
        """Test that agent topics are limited to prevent memory bloat."""
        # Push many entries for same agent
        for i in range(15):
            self.store.push("Agent1", 100 + i, [f"topic_{i}"])
        
        # Should only keep last 10 topics
        agent_topics = self.store._agent_topics["Agent1"]
        assert len(agent_topics) <= 10
        assert f"topic_14" in agent_topics  # Most recent should be kept


class TestContextStoreWithMockRedis:
    """Test context store with mocked Redis."""
    
    def setup_method(self):
        """Set up context store with mocked Redis."""
        self.mock_redis = Mock()
        self.mock_redis.ping.return_value = True
        
        with patch('redis.from_url', return_value=self.mock_redis):
            with patch.dict('os.environ', {'REDIS_URL': 'redis://localhost:6379'}):
                self.store = ContextStore()
    
    def test_push_to_redis(self):
        """Test pushing entries to Redis."""
        self.store.push("Agent1", 123, ["crypto_btc"], text="Test")
        
        # Verify Redis calls
        self.mock_redis.setex.assert_called()
        self.mock_redis.zadd.assert_called()
        self.mock_redis.lpush.assert_called()
        self.mock_redis.ltrim.assert_called()
    
    def test_pull_from_redis(self):
        """Test pulling entries from Redis."""
        # Mock Redis responses
        self.mock_redis.zrevrange.return_value = ['123', '124']
        self.mock_redis.get.side_effect = [
            '{"agent_id": "Agent1", "tweet_id": 123, "topic_tags": ["crypto_btc"], "timestamp": 1234567890}',
            '{"agent_id": "Agent2", "tweet_id": 124, "topic_tags": ["meme_culture"], "timestamp": 1234567891}'
        ]
        
        entries = self.store.pull_last(2)
        
        assert len(entries) == 2
        assert entries[0].agent_id == "Agent1"
        assert entries[1].agent_id == "Agent2"
    
    def test_redis_fallback_on_error(self):
        """Test fallback to memory when Redis fails."""
        # Make Redis fail
        self.mock_redis.zrevrange.side_effect = Exception("Redis error")
        
        # Add entry to memory buffer directly
        self.store._ring_buffer.append(ContextEntry(
            agent_id="Agent1", 
            tweet_id=123, 
            topic_tags=["test"], 
            timestamp=time.time()
        ))
        
        # Should fallback to memory
        entries = self.store.pull_last(1)
        assert len(entries) == 1
        assert entries[0].agent_id == "Agent1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 