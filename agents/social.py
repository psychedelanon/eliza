import asyncio
import logging
import random
from typing import List, Optional

from agents.base import TwitterAgent
from eliza import llm
from metrics import AMPLIFICATIONS_TOTAL

log = logging.getLogger(__name__)


async def _get_last_tweet_id(peer: TwitterAgent) -> Optional[int]:
    try:
        if hasattr(peer.client, "user_timeline"):
            timeline = peer.client.user_timeline(count=1)
            if timeline:
                return getattr(timeline[0], "id", None)
        elif hasattr(peer.client, "get_users_tweets"):
            user_id = peer.client.get_me().data.id
            resp = peer.client.get_users_tweets(user_id, max_results=5)
            tweets = getattr(resp, "data", [])
            if tweets:
                return getattr(tweets[0], "id", None)
    except Exception as exc:  # pragma: no cover - network
        log.exception("failed to fetch peer tweet", exc_info=exc)
    return None


async def amplify(bot: TwitterAgent, peers: List[TwitterAgent], *, dry: bool) -> None:
    """Randomly like/RT/reply to a peer's last tweet with jitter and persona-aware text."""

    if not peers:
        return

    peer = random.choice(peers)
    tweet_id = await _get_last_tweet_id(peer)
    if not tweet_id:
        return

    actions = ["like", "retweet", "quote", "reply"]
    selected = random.sample(actions, k=random.randint(1, 2))

    for action in selected:
        try:
            if dry:
                log.info("%s would %s %s", bot.name, action, tweet_id)
            elif action == "like":
                bot.client.like(tweet_id)
            elif action == "retweet":
                bot.client.retweet(tweet_id)
            elif action == "quote":
                text = llm.complete(
                    f"{bot.personality} quick hype one-liner for {peer.personality}",
                    max_tokens=40,
                )
                bot.client.create_tweet(text=text, quote_tweet_id=tweet_id)
            elif action == "reply":
                text = llm.complete(
                    f"{bot.personality} short reply hyping bitcoin", max_tokens=40
                )
                await asyncio.sleep(random.uniform(120, 600))
                bot.client.create_tweet(text=text, in_reply_to_tweet_id=tweet_id)
            AMPLIFICATIONS_TOTAL.labels(agent=bot.name, action=action).inc()
        except Exception as exc:  # pragma: no cover - network
            log.exception("amplify %s failed", action, exc_info=exc)
