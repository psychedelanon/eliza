import threading
import os
from typing import List, Dict, Optional, Any

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
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        try:
            import redis
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
                    self._r.lpush("events", json.dumps(event))
                    self._r.ltrim("events", 0, 99)
                def get_latest_event(self) -> Optional[Dict[str, Any]]:
                    events = self._r.lrange("events", 0, 0)
                    if events:
                        return json.loads(events[0].decode())
                    return None
            _shared_mem = RedisSharedMemory(redis_url)
        except ImportError:
            _shared_mem = InProcSharedMemory()
    else:
        _shared_mem = InProcSharedMemory()
    return _shared_mem
