import logging
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from threading import Lock
from typing import Dict, Tuple, Optional, List

log = logging.getLogger("rate_limiter")

class RateLimiter:
    """
    Tracks tweet and action counts per agent and globally in a rolling 15-minute window.
    Thread-safe for use in async or threaded environments.
    """
    WINDOW = timedelta(minutes=15)
    MAX_TWEETS_PER_AGENT = 25  # Per 15-minute window
    MAX_TWEETS_PER_APP = 300   # Per 15-minute window (Twitter's limit)

    def __init__(self):
        self._lock = Lock()
        self._agent_actions: Dict[str, List[datetime]] = defaultdict(list)
        self._app_actions: List[datetime] = []

    def _prune(self, now: datetime):
        cutoff = now - self.WINDOW
        for agent in list(self._agent_actions.keys()):
            self._agent_actions[agent] = [
                action for action in self._agent_actions[agent]
                if action > cutoff
            ]
            # Remove empty agent entries
            if not self._agent_actions[agent]:
                del self._agent_actions[agent]
        
        self._app_actions = [
            action for action in self._app_actions
            if action > cutoff
        ]

    def can_post(self, agent: str) -> bool:
        """
        Check if an agent can post without hitting rate limits.
        """
        with self._lock:
            self._prune(datetime.now(timezone.utc))
            
            agent_count = len(self._agent_actions[agent])
            app_count = len(self._app_actions)
            
            return agent_count < self.MAX_TWEETS_PER_AGENT and app_count < self.MAX_TWEETS_PER_APP

    def register(self, agent: str):
        """
        Register a successful post action.
        """
        now = datetime.now(timezone.utc)
        with self._lock:
            self._prune(now)
            self._agent_actions[agent].append(now)
            self._app_actions.append(now)
        
        log.debug(f"Registered post for {agent} (agent: {len(self._agent_actions[agent])}, app: {len(self._app_actions)})")

    def get_counts(self, agent: Optional[str] = None) -> Tuple[int, int]:
        """
        Get current counts for an agent and the app.
        """
        with self._lock:
            self._prune(datetime.now(timezone.utc))
            if agent:
                return len(self._agent_actions[agent]), len(self._app_actions)
            return 0, len(self._app_actions) 