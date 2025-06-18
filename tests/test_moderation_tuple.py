"""Test tuple handling in moderation."""
from agents.base import TwitterAgent

def test_post_tuple_moderation():
    """Test that posting a tuple (text, None) doesn't crash."""
    agent = TwitterAgent("test_agent", dry_run=True)
    text = "Test tweet with $BITCOIN"
    img_path = None
    post = (text, img_path)
    
    # Should not raise AttributeError
    tweet_id = agent.post(post)
    assert tweet_id > 0  # In dry run, returns timestamp 