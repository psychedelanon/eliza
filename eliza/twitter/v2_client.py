from __future__ import annotations
import tweepy
import os
import logging

logger = logging.getLogger(__name__)

class TwitterClientV2:
    """Twitter API v2 client wrapper for free tier posting."""
    
    def __init__(self, agent_env_prefix: str):
        """Initialize v2 client with agent-specific environment variables."""
        self.client = tweepy.Client(
            consumer_key=os.getenv(f"{agent_env_prefix}_API_KEY"),
            consumer_secret=os.getenv(f"{agent_env_prefix}_API_SECRET"),
            access_token=os.getenv(f"{agent_env_prefix}_ACCESS_TOKEN"),
            access_token_secret=os.getenv(f"{agent_env_prefix}_ACCESS_SECRET"),
            wait_on_rate_limit=True,
        )
        self.agent_prefix = agent_env_prefix

    def post_tweet(self, text: str, reply_to_id: str | None = None, media_ids: list | None = None) -> str:
        """Post a tweet using v2 API."""
        if media_ids:
            # Media upload requires Basic tier - skip for now
            logger.warning(f"Media upload requested but not supported on free tier (agent: {self.agent_prefix})")
            media_ids = None
        
        try:
            resp = self.client.create_tweet(
                text=text, 
                in_reply_to_tweet_id=reply_to_id
            )
            tweet_id = resp.data["id"]
            logger.info(f"🎯 {self.agent_prefix} posted v2 tweet {tweet_id}")
            return tweet_id
        except Exception as e:
            logger.error(f"❌ {self.agent_prefix} v2 posting failed: {e}")
            raise

    def like_tweet(self, tweet_id: str) -> bool:
        """Like a tweet using v2 API."""
        try:
            self.client.like(tweet_id)
            logger.info(f"👍 {self.agent_prefix} liked tweet {tweet_id}")
            return True
        except Exception as e:
            logger.error(f"❌ {self.agent_prefix} like failed: {e}")
            return False

    def retweet(self, tweet_id: str) -> bool:
        """Retweet using v2 API."""
        try:
            self.client.retweet(tweet_id)
            logger.info(f"🔄 {self.agent_prefix} retweeted {tweet_id}")
            return True
        except Exception as e:
            logger.error(f"❌ {self.agent_prefix} retweet failed: {e}")
            return False 