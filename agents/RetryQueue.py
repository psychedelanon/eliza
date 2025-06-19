import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, List, Optional
from enum import Enum

log = logging.getLogger("retry_queue")

class ActionType(Enum):
    POST = "post"
    LIKE = "like"
    REPLY = "reply"
    RETWEET = "retweet"
    BOOKMARK = "bookmark"

@dataclass
class RetryItem:
    """Represents a failed action that should be retried."""
    action_type: ActionType
    agent: str
    func: Callable
    args: tuple
    kwargs: dict
    next_retry_at: datetime
    attempts: int = 0
    max_attempts: int = 3

class RetryQueue:
    """
    Handles retrying failed Twitter API actions with exponential backoff.
    """
    INITIAL_DELAY = 60  # 1 minute
    MAX_DELAY = 900     # 15 minutes
    MAX_ATTEMPTS = 3

    def __init__(self):
        self._queue: List[RetryItem] = []
        self._running = False
        self._task: Optional[asyncio.Task] = None

    def add_failed_action(
        self,
        action_type: ActionType,
        agent: str,
        func: Callable,
        *args,
        **kwargs
    ) -> None:
        """Add a failed action to the retry queue."""
        now = datetime.now(timezone.utc)
        next_retry = now + timedelta(seconds=self.INITIAL_DELAY)
        
        item = RetryItem(
            action_type=action_type,
            agent=agent,
            func=func,
            args=args,
            kwargs=kwargs,
            next_retry_at=next_retry,
            attempts=0,
            max_attempts=self.MAX_ATTEMPTS
        )
        
        self._queue.append(item)
        log.info(f"Added {action_type.value} action for {agent} to retry queue")
        
        # Start the worker if not already running
        if not self._running:
            self._start_worker()

    def _start_worker(self) -> None:
        """Start the background worker task."""
        if self._task is None or self._task.done():
            self._running = True
            # Only create task if we're in an event loop
            try:
                loop = asyncio.get_running_loop()
                self._task = loop.create_task(self._worker())
            except RuntimeError:
                # No event loop running, we'll start it when needed
                pass

    async def _worker(self) -> None:
        """Background worker that processes retry items."""
        while self._running:
            now = datetime.now(timezone.utc)
            ready_items = [
                item for item in self._queue 
                if item.next_retry_at <= now
            ]
            
            for item in ready_items:
                await self._retry_item(item)
            
            # Remove processed items
            self._queue = [item for item in self._queue if item.attempts < item.max_attempts]
            
            # Sleep for a short interval
            await asyncio.sleep(10)

    async def _retry_item(self, item: RetryItem) -> None:
        """Attempt to retry a single item."""
        item.attempts += 1
        
        try:
            log.info(f"Retrying {item.action_type.value} for {item.agent} (attempt {item.attempts})")
            
            # Execute the function
            if asyncio.iscoroutinefunction(item.func):
                await item.func(*item.args, **item.kwargs)
            else:
                item.func(*item.args, **item.kwargs)
            
            log.info(f"Successfully retried {item.action_type.value} for {item.agent}")
            
        except Exception as e:
            log.warning(f"Retry failed for {item.action_type.value} ({item.agent}): {e}")
            
            if item.attempts < item.max_attempts:
                # Calculate next retry time with exponential backoff
                delay = min(
                    self.INITIAL_DELAY * (2 ** (item.attempts - 1)),
                    self.MAX_DELAY
                )
                item.next_retry_at = datetime.now(timezone.utc) + timedelta(seconds=delay)
                log.info(f"Scheduling retry {item.attempts + 1} in {delay}s")
            else:
                log.error(f"Max retries exceeded for {item.action_type.value} ({item.agent})")

    def stop(self) -> None:
        """Stop the retry queue worker."""
        self._running = False
        if self._task and not self._task.done():
            try:
                self._task.cancel()
            except RuntimeError:
                # Event loop might be closed
                pass

    def get_queue_size(self) -> int:
        """Get the current size of the retry queue."""
        return len(self._queue)

# Global instance
retry_queue = RetryQueue() 