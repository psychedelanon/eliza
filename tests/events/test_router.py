import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from agents.EventSystem import EventRouter, Event, EventType, EventHandler, EventPriority

class TestEventRouter:
    """Test the event router's filtering and isolation capabilities."""
    
    @pytest.fixture
    def router(self):
        """Create a fresh event router for each test."""
        return EventRouter()
    
    @pytest.fixture
    def mock_handler(self):
        """Create a mock handler function."""
        return AsyncMock()
    
    def test_register_handler_for_specific_event_type(self, router, mock_handler):
        """Test that handlers are registered for specific event types."""
        handler = EventHandler(
            agent_name="test_agent",
            event_types={EventType.AGENT_POST, EventType.PRICE_POST},
            handler_func=mock_handler
        )
        
        router.register_handler(handler)
        
        # Check that handler is registered for both event types
        assert len(router._handlers[EventType.AGENT_POST]) == 1
        assert len(router._handlers[EventType.PRICE_POST]) == 1
        assert len(router._handlers[EventType.MARKET_SIGNAL]) == 0  # Not registered
    
    def test_unregister_handler(self, router, mock_handler):
        """Test that handlers can be unregistered."""
        handler = EventHandler(
            agent_name="test_agent",
            event_types={EventType.AGENT_POST, EventType.PRICE_POST},
            handler_func=mock_handler
        )
        
        router.register_handler(handler)
        assert len(router._handlers[EventType.AGENT_POST]) == 1
        
        router.unregister_handler("test_agent")
        assert len(router._handlers[EventType.AGENT_POST]) == 0
        assert len(router._handlers[EventType.PRICE_POST]) == 0
    
    def test_get_matching_handlers_filters_by_event_type(self, router, mock_handler):
        """Test that only handlers registered for the specific event type are returned."""
        # Register handler for AGENT_POST only
        agent_handler = EventHandler(
            agent_name="agent_handler",
            event_types={EventType.AGENT_POST},
            handler_func=mock_handler
        )
        
        # Register handler for PRICE_POST only
        price_handler = EventHandler(
            agent_name="price_handler",
            event_types={EventType.PRICE_POST},
            handler_func=mock_handler
        )
        
        router.register_handler(agent_handler)
        router.register_handler(price_handler)
        
        # Create an AGENT_POST event
        event = Event(
            type=EventType.AGENT_POST,
            source_agent="test_agent",
            data={"content": "test post"}
        )
        
        # Should only return the agent_handler
        matching = router._get_matching_handlers(event)
        assert len(matching) == 1
        assert matching[0].agent_name == "agent_handler"
    
    def test_get_matching_handlers_filters_by_target_agents(self, router, mock_handler):
        """Test that handlers are filtered by target_agents when specified."""
        handler = EventHandler(
            agent_name="target_agent",
            event_types={EventType.AGENT_POST},
            handler_func=mock_handler
        )
        
        router.register_handler(handler)
        
        # Event with specific target
        event = Event(
            type=EventType.AGENT_POST,
            source_agent="source_agent",
            target_agents=["target_agent"],
            data={"content": "test post"}
        )
        
        matching = router._get_matching_handlers(event)
        assert len(matching) == 1
        assert matching[0].agent_name == "target_agent"
        
        # Event with different target
        event2 = Event(
            type=EventType.AGENT_POST,
            source_agent="source_agent",
            target_agents=["other_agent"],
            data={"content": "test post"}
        )
        
        matching2 = router._get_matching_handlers(event2)
        assert len(matching2) == 0
    
    def test_get_matching_handlers_excludes_source_agent(self, router, mock_handler):
        """Test that the source agent is excluded from matching handlers."""
        handler = EventHandler(
            agent_name="source_agent",
            event_types={EventType.AGENT_POST},
            handler_func=mock_handler
        )
        
        router.register_handler(handler)
        
        event = Event(
            type=EventType.AGENT_POST,
            source_agent="source_agent",
            data={"content": "test post"}
        )
        
        matching = router._get_matching_handlers(event)
        assert len(matching) == 0  # Source agent should be excluded
    
    def test_get_matching_handlers_allows_source_for_swarm_commands(self, router, mock_handler):
        """Test that source agent is allowed for SWARM_COMMAND events."""
        handler = EventHandler(
            agent_name="source_agent",
            event_types={EventType.SWARM_COMMAND},
            handler_func=mock_handler
        )
        
        router.register_handler(handler)
        
        event = Event(
            type=EventType.SWARM_COMMAND,
            source_agent="source_agent",
            data={"command": "test"}
        )
        
        matching = router._get_matching_handlers(event)
        assert len(matching) == 1  # Source agent should be included for swarm commands
    
    def test_get_matching_handlers_respects_enabled_flag(self, router, mock_handler):
        """Test that disabled handlers are excluded."""
        handler = EventHandler(
            agent_name="test_agent",
            event_types={EventType.AGENT_POST},
            handler_func=mock_handler,
            enabled=False
        )
        
        router.register_handler(handler)
        
        event = Event(
            type=EventType.AGENT_POST,
            source_agent="other_agent",
            data={"content": "test post"}
        )
        
        matching = router._get_matching_handlers(event)
        assert len(matching) == 0  # Disabled handler should be excluded
    
    def test_get_matching_handlers_sorts_by_priority(self, router, mock_handler):
        """Test that handlers are sorted by priority (highest first)."""
        low_priority = EventHandler(
            agent_name="low_priority",
            event_types={EventType.AGENT_POST},
            handler_func=mock_handler,
            priority=EventPriority.LOW
        )
        
        high_priority = EventHandler(
            agent_name="high_priority",
            event_types={EventType.AGENT_POST},
            handler_func=mock_handler,
            priority=EventPriority.HIGH
        )
        
        router.register_handler(low_priority)
        router.register_handler(high_priority)
        
        event = Event(
            type=EventType.AGENT_POST,
            source_agent="other_agent",
            data={"content": "test post"}
        )
        
        matching = router._get_matching_handlers(event)
        assert len(matching) == 2
        assert matching[0].agent_name == "high_priority"  # Higher priority first
        assert matching[0].priority == EventPriority.HIGH
        assert matching[1].agent_name == "low_priority"
        assert matching[1].priority == EventPriority.LOW
    
    @pytest.mark.asyncio
    async def test_publish_event_queues_event(self, router):
        """Test that publish_event adds events to the queue."""
        event = Event(
            type=EventType.AGENT_POST,
            source_agent="test_agent",
            data={"content": "test post"}
        )
        
        await router.publish_event(event)
        
        # Check that event was added to queue
        queued_event = router._event_queue.get_nowait()
        assert queued_event.type == EventType.AGENT_POST
        assert queued_event.source_agent == "test_agent"
    
    def test_get_stats_returns_correct_counts(self, router, mock_handler):
        """Test that get_stats returns accurate statistics."""
        handler = EventHandler(
            agent_name="test_agent",
            event_types={EventType.AGENT_POST, EventType.PRICE_POST},
            handler_func=mock_handler
        )
        
        router.register_handler(handler)
        
        stats = router.get_stats()
        assert stats["handlers"] == 2  # One handler registered for 2 event types
        assert stats["queue_size"] == 0
        assert "test_agent" in stats["handler_details"] 