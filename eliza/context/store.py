"""
Context Store Implementation

Provides in-memory ring buffer with Redis fallback for agent context memory.
"""

import json
import logging
import os
import time
from collections import deque, defaultdict
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

log = logging.getLogger("context_store")

@dataclass
class ContextEntry:
    """A single context entry."""
    agent_id: str
    tweet_id: int
    topic_tags: List[str]
    timestamp: float
    text: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContextEntry':
        return cls(**data)


class ContextStore:
    """
    Context memory store with ring buffer and Redis fallback.
    
    API:
    - push(agent_id, tweet_id, topic_tags, text=None)
    - pull_last(n=5) -> List[ContextEntry]
    - last_topic_by_agent(agent_id) -> Optional[str]
    """
    
    def __init__(self, max_size: int = 1000, redis_url: Optional[str] = None):
        self.max_size = max_size
        self.redis_url = redis_url or os.getenv("REDIS_URL")
        
        # In-memory storage
        self._ring_buffer: deque = deque(maxlen=max_size)
        self._agent_topics: Dict[str, List[str]] = defaultdict(list)
        
        # Redis client (optional)
        self._redis_client = None
        if self.redis_url:
            self._init_redis()
    
    def _init_redis(self) -> None:
        """Initialize Redis client if URL is provided."""
        try:
            import redis
            self._redis_client = redis.from_url(self.redis_url, decode_responses=True)
            # Test connection
            self._redis_client.ping()
            log.info("Redis context store initialized", extra={"redis_url": self.redis_url})
        except ImportError:
            log.warning("Redis not available, using in-memory store only")
            self._redis_client = None
        except Exception as e:
            log.warning(f"Redis connection failed, using in-memory store: {e}")
            self._redis_client = None
    
    def push(self, agent_id: str, tweet_id: int, topic_tags: List[str], text: Optional[str] = None) -> None:
        """Push a new context entry."""
        entry = ContextEntry(
            agent_id=agent_id,
            tweet_id=tweet_id,
            topic_tags=topic_tags,
            timestamp=time.time(),
            text=text
        )
        
        # Add to in-memory buffer
        self._ring_buffer.append(entry)
        
        # Update agent topics (keep last 10 per agent)
        self._agent_topics[agent_id].extend(topic_tags)
        if len(self._agent_topics[agent_id]) > 10:
            self._agent_topics[agent_id] = self._agent_topics[agent_id][-10:]
        
        # Store in Redis if available
        if self._redis_client:
            try:
                # Store individual entry
                key = f"context:entry:{tweet_id}"
                self._redis_client.setex(key, 3600 * 24, json.dumps(entry.to_dict()))  # 24h TTL
                
                # Add to global timeline
                self._redis_client.zadd("context:timeline", {tweet_id: entry.timestamp})
                
                # Keep only recent entries (last 1000)
                self._redis_client.zremrangebyrank("context:timeline", 0, -1001)
                
                # Update agent topics
                agent_key = f"context:agent:{agent_id}:topics"
                for tag in topic_tags:
                    self._redis_client.lpush(agent_key, tag)
                self._redis_client.ltrim(agent_key, 0, 9)  # Keep last 10
                
            except Exception as e:
                log.warning(f"Redis push failed: {e}")
        
        log.debug(
            f"Context pushed for {agent_id}: {len(topic_tags)} topics",
            extra={
                "agent": agent_id,
                "tweet_id": tweet_id,
                "topics": topic_tags,
                "buffer_size": len(self._ring_buffer)
            }
        )
    
    def pull_last(self, n: int = 5) -> List[ContextEntry]:
        """Pull the last n entries from context."""
        # Try Redis first if available
        if self._redis_client:
            try:
                # Get last n tweet IDs from timeline
                tweet_ids = self._redis_client.zrevrange("context:timeline", 0, n-1)
                entries = []
                
                for tweet_id in tweet_ids:
                    key = f"context:entry:{tweet_id}"
                    data = self._redis_client.get(key)
                    if data:
                        entry_dict = json.loads(data)
                        entries.append(ContextEntry.from_dict(entry_dict))
                
                if entries:
                    log.debug(f"Pulled {len(entries)} entries from Redis")
                    return entries
                    
            except Exception as e:
                log.warning(f"Redis pull failed, falling back to memory: {e}")
        
        # Fallback to in-memory buffer
        entries = list(self._ring_buffer)[-n:] if self._ring_buffer else []
        log.debug(f"Pulled {len(entries)} entries from memory buffer")
        return entries
    
    def last_topic_by_agent(self, agent_id: str) -> Optional[str]:
        """Get the most recent topic for a specific agent."""
        # Try Redis first if available
        if self._redis_client:
            try:
                agent_key = f"context:agent:{agent_id}:topics"
                topics = self._redis_client.lrange(agent_key, 0, 0)  # Get most recent
                if topics:
                    return topics[0]
            except Exception as e:
                log.warning(f"Redis topic lookup failed: {e}")
        
        # Fallback to in-memory
        agent_topics = self._agent_topics.get(agent_id, [])
        return agent_topics[-1] if agent_topics else None
    
    def get_recent_by_agent(self, agent_id: str, n: int = 3) -> List[ContextEntry]:
        """Get recent entries for a specific agent."""
        recent_entries = self.pull_last(n * 3)  # Get more to filter
        agent_entries = [entry for entry in recent_entries if entry.agent_id == agent_id]
        return agent_entries[-n:] if agent_entries else []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get context store statistics."""
        stats = {
            "buffer_size": len(self._ring_buffer),
            "max_size": self.max_size,
            "agent_count": len(self._agent_topics),
            "redis_enabled": self._redis_client is not None
        }
        
        if self._redis_client:
            try:
                stats["redis_timeline_size"] = self._redis_client.zcard("context:timeline")
            except Exception:
                stats["redis_timeline_size"] = "unknown"
        
        return stats


# Global context store instance
context_store = ContextStore()


def get_context_store() -> ContextStore:
    """Get the global context store instance."""
    return context_store 