import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Callable, Any, Set
from collections import defaultdict
import random

log = logging.getLogger("event_system")

class EventType(Enum):
    """Types of events that can be published and consumed."""
    AGENT_POST = "agent_post"
    PRICE_POST = "price_post"
    NEW_HOT_TOKEN = "new_hot_token"
    MARKET_SIGNAL = "market_signal"
    ENGAGEMENT_REQUEST = "engagement_request"
    SWARM_COMMAND = "swarm_command"
    QUALITY_ALERT = "quality_alert"
    RATE_LIMIT_ALERT = "rate_limit_alert"

class EventPriority(Enum):
    """Event priority levels for routing and processing."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class Event:
    """Enhanced event structure with metadata and routing information."""
    type: EventType
    priority: EventPriority = EventPriority.NORMAL
    source_agent: str = ""
    target_agents: List[str] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=lambda: time.time())
    event_id: str = ""
    correlation_id: str = ""
    
    def __post_init__(self):
        if not self.event_id:
            self.event_id = f"{self.type.value}_{int(self.timestamp * 1000)}"
        if not self.correlation_id:
            self.correlation_id = self.event_id

@dataclass
class EventHandler:
    """Handler configuration for event processing."""
    agent_name: str
    event_types: Set[EventType]
    handler_func: Callable
    priority: EventPriority = EventPriority.NORMAL
    max_concurrent: int = 1
    delay_range: tuple = (0, 0)  # (min_delay, max_delay) in seconds
    enabled: bool = True

class EventRouter:
    """
    Advanced event router that handles event distribution, filtering, and coordination.
    """
    
    def __init__(self):
        self._handlers: Dict[EventType, List[EventHandler]] = defaultdict(list)
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._processing_tasks: Dict[str, List[asyncio.Task]] = defaultdict(list)
        self._running = False
        self._router_task: Optional[asyncio.Task] = None
        
    def register_handler(self, handler: EventHandler) -> None:
        """Register an event handler for specific event types."""
        for event_type in handler.event_types:
            self._handlers[event_type].append(handler)
        log.info(f"Registered handler for {handler.agent_name}: {[et.value for et in handler.event_types]}")
    
    def unregister_handler(self, agent_name: str) -> None:
        """Unregister an event handler."""
        for event_type in list(self._handlers.keys()):
            self._handlers[event_type] = [
                h for h in self._handlers[event_type] 
                if h.agent_name != agent_name
            ]
        log.info(f"Unregistered handler for {agent_name}")
    
    async def publish_event(self, event: Event) -> None:
        """Publish an event to the router."""
        await self._event_queue.put(event)
        log.debug(f"Published event: {event.type.value} from {event.source_agent}")
    
    def start(self) -> None:
        """Start the event router."""
        if not self._running:
            self._running = True
            self._router_task = asyncio.create_task(self._router_loop())
            log.info("Event router started")
    
    def stop(self) -> None:
        """Stop the event router."""
        self._running = False
        if self._router_task and not self._router_task.done():
            self._router_task.cancel()
        log.info("Event router stopped")
    
    async def _router_loop(self) -> None:
        """Main router loop that processes events and dispatches to handlers."""
        while self._running:
            try:
                # Get next event from queue
                event = await asyncio.wait_for(self._event_queue.get(), timeout=1.0)
                
                # Find matching handlers for this specific event type
                matching_handlers = self._get_matching_handlers(event)
                
                # Dispatch to handlers
                for handler in matching_handlers:
                    await self._dispatch_to_handler(handler, event)
                    
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                log.error(f"Error in router loop: {e}")
    
    def _get_matching_handlers(self, event: Event) -> List[EventHandler]:
        """Get handlers that should process this event type."""
        matching = []
        
        # Get handlers registered for this specific event type
        handlers_for_type = self._handlers.get(event.type, [])
        
        for handler in handlers_for_type:
            if not handler.enabled:
                continue
                
            # Check if this handler is registered for this specific event type
            if event.type not in handler.event_types:
                continue
                
            # Check if handler is in target list (if specified)
            if event.target_agents and handler.agent_name not in event.target_agents:
                continue
            
            # Check if handler is not the source (unless explicitly allowed)
            if event.source_agent == handler.agent_name and event.type != EventType.SWARM_COMMAND:
                continue
            
            matching.append(handler)
        
        # Sort by priority (highest first)
        matching.sort(key=lambda h: h.priority.value, reverse=True)
        return matching
    
    async def _dispatch_to_handler(self, handler: EventHandler, event: Event) -> None:
        """Dispatch an event to a specific handler."""
        # Check concurrent task limit
        active_tasks = [t for t in self._processing_tasks[handler.agent_name] if not t.done()]
        if len(active_tasks) >= handler.max_concurrent:
            log.debug(f"Skipping {handler.agent_name} - max concurrent tasks reached")
            return
        
        # Calculate delay
        delay = random.uniform(*handler.delay_range) if handler.delay_range != (0, 0) else 0
        
        # Create and track the task
        task = asyncio.create_task(self._execute_handler(handler, event, delay))
        self._processing_tasks[handler.agent_name].append(task)
        
        # Clean up completed tasks
        self._processing_tasks[handler.agent_name] = [
            t for t in self._processing_tasks[handler.agent_name] if not t.done()
        ]
    
    async def _execute_handler(self, handler: EventHandler, event: Event, delay: float) -> None:
        """Execute a handler with optional delay."""
        try:
            if delay > 0:
                await asyncio.sleep(delay)
            
            # Call the handler function
            if asyncio.iscoroutinefunction(handler.handler_func):
                await handler.handler_func(event)
            else:
                handler.handler_func(event)
            
            log.debug(f"Handler {handler.agent_name} processed {event.type.value}")
            
        except Exception as e:
            log.error(f"Handler {handler.agent_name} failed for {event.type.value}: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get router statistics."""
        stats = {
            "queue_size": self._event_queue.qsize(),
            "handlers": sum(len(handlers) for handlers in self._handlers.values()),
            "active_tasks": sum(len(tasks) for tasks in self._processing_tasks.values()),
            "handler_details": {}
        }
        
        for agent_name, tasks in self._processing_tasks.items():
            stats["handler_details"][agent_name] = {
                "active_tasks": len([t for t in tasks if not t.done()]),
                "total_tasks": len(tasks)
            }
        
        return stats

# Global event router instance
event_router = EventRouter()

# Convenience functions for backward compatibility
async def publish_event(event_type: EventType, source_agent: str, data: Dict[str, Any], 
                       target_agents: Optional[List[str]] = None, priority: EventPriority = EventPriority.NORMAL) -> None:
    """Publish an event with simplified interface."""
    event = Event(
        type=event_type,
        priority=priority,
        source_agent=source_agent,
        target_agents=target_agents or [],
        data=data
    )
    await event_router.publish_event(event)

def register_event_handler(agent_name: str, event_types: List[EventType], handler_func: Callable,
                          priority: EventPriority = EventPriority.NORMAL, delay_range: tuple = (0, 0)) -> None:
    """Register an event handler with simplified interface."""
    handler = EventHandler(
        agent_name=agent_name,
        event_types=set(event_types),
        handler_func=handler_func,
        priority=priority,
        delay_range=delay_range
    )
    event_router.register_handler(handler) 