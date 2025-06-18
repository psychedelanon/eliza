"""
Test price reaction functionality.
Tests coordinated engagement on Agent2's price posts.
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock
from agents.agent2 import Agent2
from agents.personas import LoreMaster, MemeLord, AlphaScry, GremlinGM
from agents.swarm import SwarmCoordinator
from eliza.shared_memory import get_shared_memory


@pytest.mark.asyncio
async def test_agent2_publishes_price_post_event():
    """Test that Agent2 publishes price_post event after successful post."""
    # Create Agent2 with dry_run
    agent2 = Agent2(name="Agent2", personality="price_analyst", dry_run=True)
    
    # Mock the shared memory
    mock_mem = Mock()
    mock_mem.publish_event = Mock()
    
    with patch('agents.agent2.get_shared_memory', return_value=mock_mem):
        # Craft and post
        text, img = agent2.craft_post()
        tweet_id = await agent2.post((text, img))
        
        # Verify event was published
        assert tweet_id > 0
        mock_mem.publish_event.assert_called_once()
        
        # Verify event structure
        call_args = mock_mem.publish_event.call_args[0][0]
        assert call_args["type"] == "price_post"
        assert "tweet_id" in call_args
        assert "btc" in call_args
        assert "hpo" in call_args
        assert call_args["agent"] == "Agent2"
        assert "ts" in call_args


@pytest.mark.asyncio
async def test_persona_agents_react_to_price_post():
    """Test that persona agents react to price_post events."""
    # Create persona agents
    lore_master = LoreMaster(name="LoreMaster", personality="lore", dry_run=True)
    meme_lord = MemeLord(name="MemeLord", personality="meme", dry_run=True)
    alpha_scry = AlphaScry(name="AlphaScry", personality="alpha", dry_run=True)
    gremlin_gm = GremlinGM(name="GremlinGM", personality="gremlin", dry_run=True)
    
    # Mock reply method
    for agent in [lore_master, meme_lord, alpha_scry, gremlin_gm]:
        agent.reply = AsyncMock(return_value=123)
    
    # Create price_post event
    event = {
        "type": "price_post",
        "tweet_id": 42,
        "btc": 50000.0,
        "hpo": 0.0005,
        "agent": "Agent2",
        "ts": time.time(),
        "text": "📊 $BITCOIN: $50,000.00 | $HPOS10I: $0.000500 | HPO up 100.00% vs BTC #HarryPotterObamaSonic10Inu"
    }
    
    # Test each persona's reaction
    for agent in [lore_master, meme_lord, alpha_scry, gremlin_gm]:
        await agent.react_to_event(event)
        
        # Verify reply was called
        agent.reply.assert_called_once()
        
        # Verify reply text contains required elements
        reply_text = agent.reply.call_args[0][1]  # Second argument is the reply text
        assert "$BITCOIN" in reply_text
        assert "#HarryPotterObamaSonic10Inu" in reply_text or "#HPOS10I" in reply_text
        assert len(reply_text) <= 150  # Reply length limit
        
        # Reset mock for next iteration
        agent.reply.reset_mock()


@pytest.mark.asyncio
async def test_swarm_coordinator_dispatches_events():
    """Test that SwarmCoordinator dispatches events to persona agents."""
    # Create persona agents
    lore_master = LoreMaster(name="LoreMaster", personality="lore", dry_run=True)
    meme_lord = MemeLord(name="MemeLord", personality="meme", dry_run=True)
    
    # Mock their react_to_event methods
    lore_master.react_to_event = AsyncMock()
    meme_lord.react_to_event = AsyncMock()
    
    # Create SwarmCoordinator with persona agents
    coordinator = SwarmCoordinator(
        name="SwarmCoordinator",
        personality="coordinator",
        dry_run=True,
        agents=[lore_master, meme_lord]
    )
    
    # Create price_post event
    event = {
        "type": "price_post",
        "tweet_id": 42,
        "btc": 50000.0,
        "hpo": 0.0005,
        "agent": "Agent2",
        "ts": time.time()
    }
    
    # Test immediate dispatch (no delay for testing)
    with patch('asyncio.create_task') as mock_create_task:
        await coordinator.dispatch_event(event)
        
        # Verify tasks were created for each persona
        assert mock_create_task.call_count == 2
        
        # Verify the delayed reaction function was called
        for call in mock_create_task.call_args_list:
            args, kwargs = call
            assert len(args) == 1
            # The first argument should be a coroutine (the _delayed_reaction task)
            assert asyncio.iscoroutine(args[0])


@pytest.mark.asyncio
async def test_price_reply_templates():
    """Test that persona agents have proper price reply templates."""
    # Create persona agents
    lore_master = LoreMaster(name="LoreMaster", personality="lore", dry_run=True)
    meme_lord = MemeLord(name="MemeLord", personality="meme", dry_run=True)
    alpha_scry = AlphaScry(name="AlphaScry", personality="alpha", dry_run=True)
    gremlin_gm = GremlinGM(name="GremlinGM", personality="gremlin", dry_run=True)
    
    # Test that each has price_reply_templates
    for agent in [lore_master, meme_lord, alpha_scry, gremlin_gm]:
        assert hasattr(agent, 'price_reply_templates')
        assert isinstance(agent.price_reply_templates, list)
        assert len(agent.price_reply_templates) > 0
        
        # Test template formatting
        event = {"btc": 50000.0, "hpo": 0.0005}
        reply = agent.make_price_reply(event)
        
        # Verify reply contains required elements
        assert "$BITCOIN" in reply
        assert "#HarryPotterObamaSonic10Inu" in reply or "#HPOS10I" in reply
        assert len(reply) <= 150


@pytest.mark.asyncio
async def test_alpha_scry_spam_filter_exception():
    """Test that AlphaScry can use 'alpha' and 'signal' keywords without spam filter."""
    from agents.quality import validate
    
    # Test AlphaScry content with allowed keywords
    alpha_content = "Alpha alert: $BITCOIN showing strength! The charts confirm what the alpha hunters whispered. 📊 #HarryPotterObamaSonic10Inu"
    
    # Should pass validation for AlphaScry
    is_valid, issues = validate(alpha_content, agent_name="AlphaScry")
    assert is_valid, f"AlphaScry content failed validation: {issues}"
    
    # Should fail validation for other agents
    is_valid, issues = validate(alpha_content, agent_name="LoreMaster")
    assert not is_valid
    assert "Contains spam indicators" in issues


@pytest.mark.asyncio
async def test_reply_validation():
    """Test reply validation with shorter length requirements."""
    from agents.quality import validate_reply
    
    # Valid reply
    valid_reply = "The ancient scrolls record a +100.00% swing in the cosmic balance! 🔮 #HarryPotterObamaSonic10Inu"
    is_valid, issues = validate_reply(valid_reply, agent_name="LoreMaster")
    assert is_valid, f"Valid reply failed validation: {issues}"
    
    # Too long reply
    long_reply = "A" * 200 + " The ancient scrolls record a +100.00% swing in the cosmic balance! 🔮 #HarryPotterObamaSonic10Inu"
    is_valid, issues = validate_reply(long_reply, agent_name="LoreMaster")
    assert not is_valid
    assert "Reply too long" in issues


@pytest.mark.asyncio
async def test_shared_memory_event_broadcast():
    """Test that shared memory broadcasts events to subscribers."""
    from eliza.shared_memory import subscribe, start_broadcast_loop, stop_broadcast_loop
    
    # Start broadcast loop
    broadcast_task = start_broadcast_loop()
    
    # Create mock subscriber
    mock_subscriber = AsyncMock()
    subscribe(mock_subscriber)
    
    # Publish event
    mem = get_shared_memory()
    event = {
        "type": "price_post",
        "tweet_id": 42,
        "btc": 50000.0,
        "hpo": 0.0005,
        "agent": "Agent2",
        "ts": time.time()
    }
    mem.publish_event(event)
    
    # Wait a bit for broadcast
    await asyncio.sleep(0.2)
    
    # Verify subscriber was called
    mock_subscriber.assert_called_once()
    received_event = mock_subscriber.call_args[0][0]
    assert received_event["type"] == "price_post"
    assert received_event["tweet_id"] == 42
    
    # Stop broadcast loop
    stop_broadcast_loop()
    if not broadcast_task.done():
        broadcast_task.cancel()
        try:
            await broadcast_task
        except asyncio.CancelledError:
            pass 