#!/usr/bin/env python3
"""
Unit tests for Phase 3: Event-Driven Engagement Swarm
Run with: python -m pytest test_phase3_events.py -v
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from agents.EventSystem import EventType, EventPriority, Event, event_router, publish_event, register_event_handler
from agents.EnhancedSwarmCoordinator import EnhancedSwarmCoordinator, EngagementConfig


class TestEventSystem:
    """Test the enhanced event system."""
    
    def setup_method(self):
        """Set up a fresh event router for each test."""
        # Reset the global event router
        event_router._handlers.clear()
        event_router._event_queue = asyncio.Queue()
        event_router._processing_tasks.clear()
        event_router._running = False
        event_router._router_task = None
    
    def teardown_method(self):
        """Clean up the event router."""
        event_router.stop()
    
    @pytest.mark.asyncio
    async def test_event_creation(self):
        """Test creating events with different types and priorities."""
        event = Event(
            type=EventType.AGENT_POST,
            priority=EventPriority.HIGH,
            source_agent="TestAgent",
            data={"tweet_id": 123, "text": "Test post"}
        )
        
        assert event.type == EventType.AGENT_POST
        assert event.priority == EventPriority.HIGH
        assert event.source_agent == "TestAgent"
        assert event.data["tweet_id"] == 123
        assert event.event_id != ""
        assert event.correlation_id != ""
    
    @pytest.mark.asyncio
    async def test_event_publishing(self):
        """Test publishing events to the router."""
        # Start the router
        event_router.start()
        
        # Publish an event
        event = Event(
            type=EventType.AGENT_POST,
            source_agent="TestAgent",
            data={"tweet_id": 123}
        )
        
        await event_router.publish_event(event)
        
        # Check queue size
        assert event_router._event_queue.qsize() == 1
        
        # Stop the router
        event_router.stop()
    
    @pytest.mark.asyncio
    async def test_event_handler_registration(self):
        """Test registering event handlers."""
        mock_handler = Mock()
        
        register_event_handler(
            agent_name="TestAgent",
            event_types=[EventType.AGENT_POST, EventType.PRICE_POST],
            handler_func=mock_handler,
            priority=EventPriority.HIGH
        )
        
        assert "TestAgent" in event_router._handlers
        handler = event_router._handlers["TestAgent"]
        assert EventType.AGENT_POST in handler.event_types
        assert EventType.PRICE_POST in handler.event_types
        assert handler.handler_func == mock_handler
        assert handler.priority == EventPriority.HIGH
    
    @pytest.mark.asyncio
    async def test_event_routing(self):
        """Test that events are routed to appropriate handlers."""
        # Register a handler
        handler_called = False
        
        async def test_handler(event):
            nonlocal handler_called
            handler_called = True
            assert event.type == EventType.AGENT_POST
        
        register_event_handler(
            agent_name="TestAgent",
            event_types=[EventType.AGENT_POST],
            handler_func=test_handler
        )
        
        # Start router
        event_router.start()
        
        # Publish event
        event = Event(
            type=EventType.AGENT_POST,
            source_agent="OtherAgent",
            data={"tweet_id": 123}
        )
        
        await event_router.publish_event(event)
        
        # Wait for processing
        await asyncio.sleep(0.1)
        
        assert handler_called
        
        # Stop router
        event_router.stop()
    
    @pytest.mark.asyncio
    async def test_event_filtering(self):
        """Test that events are filtered correctly."""
        # Register handlers for different event types
        agent_post_handler_called = False
        price_post_handler_called = False
        
        async def agent_post_handler(event):
            nonlocal agent_post_handler_called
            agent_post_handler_called = True
        
        async def price_post_handler(event):
            nonlocal price_post_handler_called
            price_post_handler_called = True
        
        register_event_handler(
            agent_name="Agent1",
            event_types=[EventType.AGENT_POST],
            handler_func=agent_post_handler
        )
        
        register_event_handler(
            agent_name="Agent2",
            event_types=[EventType.PRICE_POST],
            handler_func=price_post_handler
        )
        
        # Start router
        event_router.start()
        
        # Publish agent post event
        agent_event = Event(
            type=EventType.AGENT_POST,
            source_agent="TestAgent",
            data={"tweet_id": 123}
        )
        
        await event_router.publish_event(agent_event)
        
        # Wait for processing
        await asyncio.sleep(0.1)
        
        assert agent_post_handler_called
        assert not price_post_handler_called
        
        # Reset and test price post
        agent_post_handler_called = False
        price_post_handler_called = False
        
        price_event = Event(
            type=EventType.PRICE_POST,
            source_agent="Agent2",
            data={"tweet_id": 456, "btc": 50000, "hpo": 0.0005}
        )
        
        await event_router.publish_event(price_event)
        
        # Wait for processing
        await asyncio.sleep(0.1)
        
        assert not agent_post_handler_called
        assert price_post_handler_called
        
        # Stop router
        event_router.stop()


class TestEnhancedSwarmCoordinator:
    """Test the enhanced swarm coordinator."""
    
    def setup_method(self):
        """Set up a fresh coordinator for each test."""
        import random
        # Use seeded random for deterministic tests
        rng = random.Random(42)
        self.coordinator = EnhancedSwarmCoordinator(
            name="TestCoordinator",
            dry_run=True,
            rng=rng
        )
    
    def test_engagement_configs(self):
        """Test that engagement configurations are set up correctly."""
        configs = self.coordinator.engagement_configs
        
        # Check that all expected agents have configs
        expected_agents = ["LoreMaster", "MemeLord", "AlphaScry", "GremlinGM", "Agent2"]
        for agent in expected_agents:
            assert agent in configs
            assert isinstance(configs[agent], EngagementConfig)
        
        # Check specific configurations
        assert configs["LoreMaster"].priority == EventPriority.HIGH
        assert configs["Agent2"].priority == EventPriority.CRITICAL
        assert configs["Agent2"].delay_range == (0, 0)  # No delay for price posts
    
    @pytest.mark.asyncio
    async def test_agent_post_handling(self):
        """Test handling of agent posts."""
        # Mock the event router
        with patch('agents.EnhancedSwarmCoordinator.event_router') as mock_router:
            # Create a test event
            event = Event(
                type=EventType.AGENT_POST,
                source_agent="LoreMaster",
                data={
                    "tweet_id": 123,
                    "text": "Test post from LoreMaster"
                }
            )
            
            # Handle the event
            await self.coordinator._handle_agent_post(event)
            
            # Verify that engagement events were published
            assert mock_router.publish_event.called
            
            # Check that the right number of engagement events were created
            calls = mock_router.publish_event.call_args_list
            assert len(calls) >= 2  # Should schedule 2-3 agents to engage
    
    @pytest.mark.asyncio
    async def test_price_post_handling(self):
        """Test handling of price posts."""
        with patch('agents.EnhancedSwarmCoordinator.event_router') as mock_router:
            # Create a price post event
            event = Event(
                type=EventType.PRICE_POST,
                source_agent="Agent2",
                data={
                    "tweet_id": 456,
                    "btc_price": 50000.0,
                    "hpo_price": 0.0005
                }
            )
            
            # Handle the event
            await self.coordinator._handle_price_post(event)
            
            # Verify that all persona agents were scheduled
            calls = mock_router.publish_event.call_args_list
            assert len(calls) == 4  # All 4 persona agents should engage
            
            # Check that the events are price-specific
            for call in calls:
                event_data = call[0][0].data
                assert event_data["engagement_type"] == "price_reply"
                assert "btc_price" in event_data
                assert "hpo_price" in event_data
    
    def test_engaging_agents_selection(self):
        """Test that the right agents are selected for engagement."""
        # Test with LoreMaster as source
        event = Event(type=EventType.AGENT_POST, source_agent="LoreMaster")
        engaging_agents = self.coordinator._get_engaging_agents("LoreMaster", event)
        
        # Should not include the source agent
        assert "LoreMaster" not in engaging_agents
        
        # Should include other persona agents
        expected_agents = ["MemeLord", "AlphaScry", "GremlinGM"]
        for agent in engaging_agents:
            assert agent in expected_agents
        
        # Should have 2-3 agents
        assert 2 <= len(engaging_agents) <= 3
    
    def test_signal_responders(self):
        """Test that the right agents respond to different signal types."""
        # Technical signals
        technical_agents = self.coordinator._get_signal_responders("pump")
        assert "AlphaScry" in technical_agents
        assert "MemeLord" in technical_agents
        
        # Trend signals
        trend_agents = self.coordinator._get_signal_responders("trend")
        assert "LoreMaster" in trend_agents
        assert "GremlinGM" in trend_agents
        
        # Unknown signals
        all_agents = self.coordinator._get_signal_responders("unknown")
        expected = ["LoreMaster", "MemeLord", "AlphaScry", "GremlinGM"]
        assert all(agent in all_agents for agent in expected)
    
    @pytest.mark.asyncio
    async def test_market_signal_generation(self):
        """Test market signal generation in dry-run mode."""
        with patch('agents.EnhancedSwarmCoordinator.event_router') as mock_router:
            # Mock the coordinator's RNG to always generate a signal
            with patch.object(self.coordinator._rng, 'random', return_value=0.1):  # 10% < 20%
                await self.coordinator.generate_market_signals()
                
                # Should have published a market signal
                assert mock_router.publish_event.called
                
                # Check the event type
                call_args = mock_router.publish_event.call_args[0][0]
                assert call_args.type == EventType.MARKET_SIGNAL
    
    @pytest.mark.asyncio
    async def test_hot_token_generation(self):
        """Test hot token generation in dry-run mode."""
        with patch('agents.EnhancedSwarmCoordinator.event_router') as mock_router:
            # Mock the coordinator's RNG to always generate a hot token
            with patch.object(self.coordinator._rng, 'random', return_value=0.1):  # 10% < 30%
                await self.coordinator.generate_hot_tokens()
                
                # Should have published a hot token event
                assert mock_router.publish_event.called
                
                # Check the event type
                call_args = mock_router.publish_event.call_args[0][0]
                assert call_args.type == EventType.NEW_HOT_TOKEN


class TestIntegration:
    """Integration tests for the event-driven system."""
    
    @pytest.mark.asyncio
    async def test_full_event_flow(self):
        """Test a complete event flow from post to engagement."""
        # Set up the system
        import random
        rng = random.Random(42)
        coordinator = EnhancedSwarmCoordinator(dry_run=True, rng=rng)
        
        # Register a mock agent handler
        engagement_events = []
        
        async def mock_agent_handler(event):
            if event.type == EventType.ENGAGEMENT_REQUEST:
                engagement_events.append(event)
        
        register_event_handler(
            agent_name="LoreMaster",
            event_types=[EventType.ENGAGEMENT_REQUEST],
            handler_func=mock_agent_handler
        )
        
        # Start the event router
        event_router.start()
        
        # Publish an agent post event
        post_event = Event(
            type=EventType.AGENT_POST,
            source_agent="MemeLord",
            data={
                "tweet_id": 123,
                "text": "Test post from MemeLord"
            }
        )
        
        await event_router.publish_event(post_event)
        
        # Wait for processing
        await asyncio.sleep(0.2)
        
        # Check that engagement events were created
        assert len(engagement_events) > 0
        
        # Check that LoreMaster was scheduled to engage
        lore_master_events = [e for e in engagement_events if "LoreMaster" in e.target_agents]
        assert len(lore_master_events) > 0
        
        # Stop the router
        event_router.stop()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 