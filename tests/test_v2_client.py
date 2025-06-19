#!/usr/bin/env python3
"""
Unit tests for TwitterClientV2
"""
import pytest
import tweepy
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from eliza.twitter.v2_client import TwitterClientV2

class TestTwitterClientV2:
    """Test the TwitterClientV2 class."""
    
    @patch.dict('os.environ', {
        'DUMMY_API_KEY': 'test_key',
        'DUMMY_API_SECRET': 'test_secret', 
        'DUMMY_ACCESS_TOKEN': 'test_token',
        'DUMMY_ACCESS_SECRET': 'test_token_secret'
    })
    def test_initialization(self):
        """Test that the client initializes correctly."""
        client = TwitterClientV2("DUMMY")
        assert client.agent_prefix == "DUMMY"
        assert client.client is not None
    
    @patch.dict('os.environ', {
        'DUMMY_API_KEY': 'test_key',
        'DUMMY_API_SECRET': 'test_secret',
        'DUMMY_ACCESS_TOKEN': 'test_token', 
        'DUMMY_ACCESS_SECRET': 'test_token_secret'
    })
    def test_post_tweet(self, monkeypatch):
        """Test posting a tweet."""
        # Mock the tweepy client response
        class DummyResp:
            data = {"id": "123456789"}
        
        def fake_create_tweet(*args, **kwargs):
            return DummyResp()
        
        # Mock the tweepy Client
        mock_client = Mock()
        mock_client.create_tweet = fake_create_tweet
        
        with patch('tweepy.Client', return_value=mock_client):
            client = TwitterClientV2("DUMMY")
            result = client.post_tweet("Hello world!")
            assert result == "123456789"
    
    @patch.dict('os.environ', {
        'DUMMY_API_KEY': 'test_key',
        'DUMMY_API_SECRET': 'test_secret',
        'DUMMY_ACCESS_TOKEN': 'test_token',
        'DUMMY_ACCESS_SECRET': 'test_token_secret'
    })
    def test_post_tweet_with_reply(self, monkeypatch):
        """Test posting a reply tweet."""
        class DummyResp:
            data = {"id": "987654321"}
        
        def fake_create_tweet(*args, **kwargs):
            # Verify reply_to_id is passed correctly
            assert kwargs.get('in_reply_to_tweet_id') == "123456789"
            return DummyResp()
        
        mock_client = Mock()
        mock_client.create_tweet = fake_create_tweet
        
        with patch('tweepy.Client', return_value=mock_client):
            client = TwitterClientV2("DUMMY")
            result = client.post_tweet("This is a reply", reply_to_id="123456789")
            assert result == "987654321"
    
    @patch.dict('os.environ', {
        'DUMMY_API_KEY': 'test_key',
        'DUMMY_API_SECRET': 'test_secret',
        'DUMMY_ACCESS_TOKEN': 'test_token',
        'DUMMY_ACCESS_SECRET': 'test_token_secret'
    })
    def test_like_tweet(self):
        """Test liking a tweet."""
        mock_client = Mock()
        mock_client.like = Mock()
        
        with patch('tweepy.Client', return_value=mock_client):
            client = TwitterClientV2("DUMMY")
            result = client.like_tweet("123456789")
            assert result is True
            mock_client.like.assert_called_once_with("123456789")
    
    @patch.dict('os.environ', {
        'DUMMY_API_KEY': 'test_key', 
        'DUMMY_API_SECRET': 'test_secret',
        'DUMMY_ACCESS_TOKEN': 'test_token',
        'DUMMY_ACCESS_SECRET': 'test_token_secret'
    })
    def test_retweet(self):
        """Test retweeting."""
        mock_client = Mock()
        mock_client.retweet = Mock()
        
        with patch('tweepy.Client', return_value=mock_client):
            client = TwitterClientV2("DUMMY")
            result = client.retweet("123456789")
            assert result is True
            mock_client.retweet.assert_called_once_with("123456789")

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 