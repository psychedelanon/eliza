"""Test tuple handling in moderation."""
import pytest
from agents.base import TwitterAgent

@pytest.mark.asyncio
async def test_post_tuple_moderation():
    """Test that posting a tuple (text, None) doesn't crash."""
    agent = TwitterAgent(name="test_agent", personality="test", dry_run=True)
    text = "Test tweet with $BITCOIN"
    img_path = None
    post = (text, img_path)
    
    # Should not raise AttributeError
    tweet_id = await agent.post(post)
    assert tweet_id > 0  # In dry run, returns dummy ID
    # Test that constructor works with required arguments
    assert agent.name == "test_agent"
    assert agent.personality == "test" 