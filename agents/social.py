from __future__ import annotations
import asyncio
import logging
import random
from typing import List, Optional

from agents.base import TwitterAgent
try:
    from metrics import AMPLIFICATIONS_TOTAL
except ImportError:
    AMPLIFICATIONS_TOTAL = None

log = logging.getLogger("social")

ACTIONS = ("like", "retweet", "quote", "reply")


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
    """
    Randomly pick a peer's last tweet and perform 1‑2 engagement actions.
    Uses jitter so swarm traffic looks organic.
    """
    if not peers:
        return
    peer = random.choice([p for p in peers if p.name != bot.name])
    target_id = getattr(peer, "last_post_id", None)
    if not target_id:
        return
    for _ in range(random.randint(1, 2)):
        action = random.choice(ACTIONS)
        jitter = random.uniform(30, 300)
        await asyncio.sleep(jitter)
        if action == "like":
            if dry:
                log.info("%s would like %s", bot.name, target_id)
            else:
                bot.client.like(target_id)
        elif action == "retweet":
            if dry:
                log.info("%s would retweet %s", bot.name, target_id)
            else:
                bot.client.retweet(target_id)
        # TODO: implement quote & reply with LLM
        log.info(
            "amplify",
            extra={"agent": bot.name, "event": "amplify", "action": action},
        )
        if AMPLIFICATIONS_TOTAL:
            AMPLIFICATIONS_TOTAL.labels(agent=bot.name, action=action).inc()
