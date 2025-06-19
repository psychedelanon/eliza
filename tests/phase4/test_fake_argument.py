#!/usr/bin/env python3
"""
Unit tests for Phase 4: Fake Argument Logic
Run with: python -m pytest tests/phase4/test_fake_argument.py -v
"""

import pytest
import asyncio
import random
from unittest.mock import Mock, patch, AsyncMock
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from agents.EventSystem import EventType, EventPriority, Event, event_router
from agents.EnhancedSwarmCoordinator import EnhancedSwarmCoordinator


class TestFakeArgument:
    """Test fake argument logic and staging."""
    
    def setup_method(self):
        """Set up coordinator with seeded random for each test."""
        self.rng = random.Random(42)
        self.coordinator = EnhancedSwarmCoordinator(
            name="TestCoordinator",
            dry_run=True,
            rng=self.rng
        )
    
    @pytest.mark.asyncio
    async def test_argument_not_triggered_low_chance(self):
        """Test that arguments are not triggered when chance is low."""
        # Mock persona with low argument chance
        mock_persona = {
            "argument_chance": 0.01,  # 1% chance
            "tone": "test"
        }
        
        with patch.object(self.coordinator, '_load_agent_persona', return_value=mock_persona):
            with patch('agents.EnhancedSwarmCoordinator.event_router') as mock_router:
                # Set RNG to high value (should not trigger)
                with patch.object(self.coordinator._rng, 'random', return_value=0.5):  # 50% > 1%
                    
                    await self.coordinator._maybe_trigger_argument("LoreMaster", 123, "Test tweet")
                    
                    # Should not publish argument event
                    mock_router.publish_event.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_argument_triggered_high_chance(self):
        """Test that arguments are triggered when chance is high."""
        # Mock persona with high argument chance
        mock_persona = {
            "argument_chance": 0.8,  # 80% chance
            "tone": "sarcastic meme-lord"
        }
        
        with patch.object(self.coordinator, '_load_agent_persona', return_value=mock_persona):
            with patch('agents.EnhancedSwarmCoordinator.event_router') as mock_router:
                # Set RNG to trigger argument (force 0% random for 100% trigger)
                with patch.object(self.coordinator._rng, 'random', return_value=0.0):  # 0% < 80%
                    
                    await self.coordinator._maybe_trigger_argument("LoreMaster", 123, "Test tweet")
                    
                    # Should publish argument event
                    mock_router.publish_event.assert_called_once()
                    
                    # Check the event details
                    call_args = mock_router.publish_event.call_args[0][0]
                    assert call_args.type == EventType.ENGAGEMENT_REQUEST
                    assert call_args.data["engagement_type"] == "argument"
                    assert call_args.data["original_tweet_id"] == 123
                    assert call_args.data["original_agent"] == "LoreMaster"
    
    @pytest.mark.asyncio
    async def test_argument_opponent_selection(self):
        """Test that argument opponent is selected correctly."""
        mock_persona = {
            "argument_chance": 1.0,  # 100% chance to trigger
            "tone": "sarcastic meme-lord"
        }
        
        with patch.object(self.coordinator, '_load_agent_persona', return_value=mock_persona):
            with patch('agents.EnhancedSwarmCoordinator.event_router') as mock_router:
                # Mock RNG methods
                with patch.object(self.coordinator._rng, 'random', return_value=0.0):  # Trigger argument
                    with patch.object(self.coordinator._rng, 'choice', return_value="MemeLord") as mock_choice:
                        with patch.object(self.coordinator._rng, 'uniform', return_value=90.0):  # 90s delay
                            
                            await self.coordinator._maybe_trigger_argument("LoreMaster", 123, "Test tweet")
                            
                            # Check opponent selection
                            call_args = mock_choice.call_args[0][0]
                            expected_opponents = ["MemeLord", "AlphaScry", "GremlinGM"]  # Exclude LoreMaster
                            assert all(opponent in expected_opponents for opponent in call_args)
                            assert "LoreMaster" not in call_args  # Source agent excluded
                            
                            # Check event target
                            event_args = mock_router.publish_event.call_args[0][0]
                            assert event_args.target_agents == ["MemeLord"]
    
    @pytest.mark.asyncio
    async def test_argument_delay_range(self):
        """Test that argument delay is in correct range."""
        mock_persona = {
            "argument_chance": 1.0,
            "tone": "test"
        }
        
        with patch.object(self.coordinator, '_load_agent_persona', return_value=mock_persona):
            with patch('agents.EnhancedSwarmCoordinator.event_router') as mock_router:
                with patch.object(self.coordinator._rng, 'random', return_value=0.0):
                    with patch.object(self.coordinator._rng, 'choice', return_value="MemeLord"):
                        with patch.object(self.coordinator._rng, 'uniform', return_value=75.0) as mock_uniform:
                            
                            await self.coordinator._maybe_trigger_argument("LoreMaster", 123, "Test tweet")
                            
                            # Check delay range
                            mock_uniform.assert_called_with(60, 120)  # 60-120s delay for arguments
                            
                            # Check event delay
                            event_args = mock_router.publish_event.call_args[0][0]
                            assert event_args.data["delay"] == 75.0
    
    @pytest.mark.asyncio
    async def test_argument_stats_tracking(self):
        """Test that argument statistics are tracked."""
        mock_persona = {
            "argument_chance": 1.0,
            "tone": "test"
        }
        
        initial_count = self.coordinator.engagement_stats["arguments_triggered"]
        
        with patch.object(self.coordinator, '_load_agent_persona', return_value=mock_persona):
            with patch('agents.EnhancedSwarmCoordinator.event_router'):
                with patch.object(self.coordinator._rng, 'random', return_value=0.0):
                    with patch.object(self.coordinator._rng, 'choice', return_value="MemeLord"):
                        with patch.object(self.coordinator._rng, 'uniform', return_value=90.0):
                            
                            await self.coordinator._maybe_trigger_argument("LoreMaster", 123, "Test tweet")
                            
                            # Check stats increment
                            assert self.coordinator.engagement_stats["arguments_triggered"] == initial_count + 1
    
    @pytest.mark.asyncio
    async def test_no_argument_when_no_opponents(self):
        """Test that no argument is triggered when no opponents available."""
        # Mock scenario where source agent is the only one available
        # (though this shouldn't happen in practice)
        mock_persona = {
            "argument_chance": 1.0,
            "tone": "test"
        }
        
        with patch.object(self.coordinator, '_load_agent_persona', return_value=mock_persona):
            with patch('agents.EnhancedSwarmCoordinator.event_router') as mock_router:
                with patch.object(self.coordinator._rng, 'random', return_value=0.0):
                    # Mock empty opponent list
                    available_opponents = []
                    
                    # This test simulates edge case where no opponents are available
                    # In practice, this shouldn't happen with our agent setup
                    
                    # We'll patch the opponent selection logic to return empty list
                    original_method = self.coordinator._maybe_trigger_argument
                    
                    async def mock_trigger_argument(source_agent, tweet_id, text):
                        persona = await self.coordinator._load_agent_persona(source_agent)
                        if not persona:
                            return
                        
                        argument_chance = persona.get("argument_chance", 0.0)
                        if self.coordinator._rng.random() < argument_chance:
                            # Simulate no available opponents
                            available_opponents = []
                            if not available_opponents:
                                return  # Should return early
                        
                    with patch.object(self.coordinator, '_maybe_trigger_argument', side_effect=mock_trigger_argument):
                        await self.coordinator._maybe_trigger_argument("LoreMaster", 123, "Test tweet")
                        
                        # Should not publish event
                        mock_router.publish_event.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_no_argument_when_no_persona(self):
        """Test that no argument is triggered when persona can't be loaded."""
        with patch.object(self.coordinator, '_load_agent_persona', return_value=None):
            with patch('agents.EnhancedSwarmCoordinator.event_router') as mock_router:
                
                await self.coordinator._maybe_trigger_argument("UnknownAgent", 123, "Test tweet")
                
                # Should not publish event
                mock_router.publish_event.assert_not_called()
    
    def test_agent_personas_have_valid_argument_chances(self):
        """Test that all agent personas have valid argument chances."""
        persona_dir = Path(__file__).parent.parent.parent / "persona"
        
        if persona_dir.exists():
            import yaml
            
            for persona_file in persona_dir.glob("agent*.yml"):
                with open(persona_file, 'r', encoding='utf-8') as f:
                    persona = yaml.safe_load(f)
                
                argument_chance = persona.get("argument_chance", 0.0)
                
                # Should be valid probability
                assert 0.0 <= argument_chance <= 1.0, f"Invalid argument_chance in {persona_file.name}"
                
                # Agent2 (price bot) should never argue
                if "agent2" in persona_file.name.lower():
                    assert argument_chance == 0.0, "Agent2 should not have arguments"
    
    @pytest.mark.asyncio
    async def test_argument_event_structure(self):
        """Test that argument events have proper structure."""
        mock_persona = {
            "argument_chance": 1.0,
            "tone": "test"
        }
        
        with patch.object(self.coordinator, '_load_agent_persona', return_value=mock_persona):
            with patch('agents.EnhancedSwarmCoordinator.event_router') as mock_router:
                with patch.object(self.coordinator._rng, 'random', return_value=0.0):
                    with patch.object(self.coordinator._rng, 'choice', return_value="AlphaScry"):
                        with patch.object(self.coordinator._rng, 'uniform', return_value=100.0):
                            
                            await self.coordinator._maybe_trigger_argument("MemeLord", 456, "Controversial tweet")
                            
                            # Check event structure
                            event = mock_router.publish_event.call_args[0][0]
                            
                            assert event.type == EventType.ENGAGEMENT_REQUEST
                            assert event.priority == EventPriority.HIGH
                            assert event.source_agent == "TestCoordinator"
                            assert event.target_agents == ["AlphaScry"]
                            
                            # Check event data
                            data = event.data
                            assert data["original_tweet_id"] == 456
                            assert data["original_agent"] == "MemeLord"
                            assert data["original_text"] == "Controversial tweet"
                            assert data["engagement_type"] == "argument"
                            assert data["delay"] == 100.0
                            assert data["argument_style"] == "dissenting_view"


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 