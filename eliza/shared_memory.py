import threading
import os
import asyncio
from typing import List, Dict, Optional, Any, Callable
import time

try:
    import redis
except ImportError:
    redis = None

# Determine if a Redis backend is configured
REDIS_URL = os.getenv("REDIS_URL", None)
_redis_client = redis.Redis.from_url(REDIS_URL) if (redis and REDIS_URL) else None

# In-process memory fallback (used if no Redis)
_memory_store = {}  # dict to store key-value pairs in memory
_memory_lists = {}  # dict to store lists in memory

# Global subscribers for pub-sub
_subscribers: List[Callable] = []
_broadcast_running = False
_broadcast_task = None

async def write(key: str, item: Any):
    """Write an item to shared memory (overwrite or append)."""
    if _redis_client:
        # Using Redis for key-value storage
        _redis_client.set(f"eliza:{key}", str(item))
    else:
        # In-memory storage
        _memory_store[key] = item

async def append_list(key: str, item: Any):
    """Append an item to the memory log."""
    if _redis_client:
        # Using a Redis list for memory log
        _redis_client.rpush(f"eliza:list:{key}", str(item))
    else:
        # In-memory list storage
        if key not in _memory_lists:
            _memory_lists[key] = []
        _memory_lists[key].append(item)

# Overload for backward compatibility - single item parameter
async def append_list_single(item: str):
    """Append an item to the default memory log (backward compatibility)."""
    await append_list("memory", item)

# Legacy compatibility - append_list without key defaults to "memory"
async def append_list_legacy(item: str):
    """Legacy function for backward compatibility."""
    await append_list("memory", item)

async def latest(key: str = "memory", default: Any = None):
    """Retrieve the latest item from shared memory."""
    if _redis_client:
        # Get the last element of the Redis list
        result = _redis_client.lrange(f"eliza:list:{key}", -1, -1)
        return result[0].decode('utf-8') if result else default
    else:
        # In-memory list retrieval
        if key in _memory_lists and _memory_lists[key]:
            return _memory_lists[key][-1]
        return default

# Legacy compatibility - latest without key defaults to "memory"
async def latest_legacy(default: Any = None):
    """Legacy function for backward compatibility."""
    return await latest("memory", default)

def subscribe(callback: Callable[[Dict], None]):
    """Subscribe to events. Callback will be called with event dict."""
    global _subscribers
    _subscribers.append(callback)

def unsubscribe(callback: Callable[[Dict], None]):
    """Unsubscribe from events."""
    global _subscribers
    if callback in _subscribers:
        _subscribers.remove(callback)

async def broadcast_loop():
    """Background loop that broadcasts events to subscribers."""
    global _broadcast_running, _subscribers
    
    _broadcast_running = True
    mem = get_shared_memory()
    last_event_ts = 0
    
    while _broadcast_running:
        try:
            # Check for new events
            latest_event = mem.get_latest_event()
            if latest_event and latest_event.get("ts", 0) > last_event_ts:
                last_event_ts = latest_event.get("ts", 0)
                
                # Broadcast to all subscribers
                for callback in _subscribers:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(latest_event)
                        else:
                            callback(latest_event)
                    except Exception as e:
                        print(f"Error in subscriber callback: {e}")
            
            await asyncio.sleep(0.1)  # Check every 100ms
            
        except Exception as e:
            print(f"Error in broadcast loop: {e}")
            await asyncio.sleep(1)

def start_broadcast_loop():
    """Start the broadcast loop in background."""
    global _broadcast_task
    if _broadcast_task is None or _broadcast_task.done():
        _broadcast_task = asyncio.create_task(broadcast_loop())
    return _broadcast_task

def stop_broadcast_loop():
    """Stop the broadcast loop."""
    global _broadcast_running, _broadcast_task
    _broadcast_running = False
    if _broadcast_task and not _broadcast_task.done():
        _broadcast_task.cancel()

# Export the legacy functions for backward compatibility
__all__ = ["write", "append_list", "latest", "append_list_legacy", "latest_legacy", 
           "subscribe", "unsubscribe", "broadcast_loop", "start_broadcast_loop", "stop_broadcast_loop"]

_shared_mem = None

class InProcSharedMemory:
    def __init__(self):
        self._lock = threading.Lock()
        self._posts: List[Dict[str, Any]] = []
        self._events: List[Dict[str, Any]] = []

    def add_post(self, agent: str, tweet_id: str, text: str):
        with self._lock:
            self._posts.append({"agent": agent, "id": tweet_id, "text": text})
            if len(self._posts) > 100:
                self._posts = self._posts[-100:]

    def get_recent_posts(self, exclude_agent: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._lock:
            return [p for p in self._posts if p["agent"] != exclude_agent]

    def publish_event(self, event: dict):
        with self._lock:
            # Add timestamp if not present
            if "ts" not in event:
                event["ts"] = time.time()
            self._events.append(event)
            if len(self._events) > 100:
                self._events = self._events[-100:]

    def get_latest_event(self) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self._events[-1] if self._events else None

def get_shared_memory():
    global _shared_mem
    if _shared_mem is not None:
        return _shared_mem
    if REDIS_URL:
        try:
            import json
            class RedisSharedMemory:
                def __init__(self, url: str):
                    self._r = redis.Redis.from_url(url)
                def add_post(self, agent: str, tweet_id: str, text: str):
                    d = {"agent": agent, "id": tweet_id, "text": text}
                    self._r.lpush("posts", json.dumps(d))
                    self._r.ltrim("posts", 0, 99)
                def get_recent_posts(self, exclude_agent: Optional[str] = None) -> List[Dict[str, Any]]:
                    posts = [json.loads(p.decode()) for p in self._r.lrange("posts", 0, 99)]
                    return [p for p in posts if p.get("agent") != exclude_agent]
                def publish_event(self, event: dict):
                    # Add timestamp if not present
                    if "ts" not in event:
                        event["ts"] = time.time()
                    self._r.lpush("events", json.dumps(event))
                    self._r.ltrim("events", 0, 99)
                def get_latest_event(self) -> Optional[Dict[str, Any]]:
                    events = self._r.lrange("events", 0, 0)
                    if events:
                        return json.loads(events[0].decode())
                    return None
            _shared_mem = RedisSharedMemory(REDIS_URL)
        except ImportError:
            _shared_mem = InProcSharedMemory()
    else:
        _shared_mem = InProcSharedMemory()
    return _shared_mem
