import os
import logging
import asyncio
import random
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional

import quickfire

import tweepy
from tenacity import retry, wait_random_exponential, stop_after_attempt

log = logging.getLogger("agent")

DB_PATH = Path("data/eliza.sqlite")
TWEET_DEDUP_WINDOW = int(os.getenv("TWEET_DEDUP_WINDOW", "7"))

DB_PATH.parent.mkdir(parents=True, exist_ok=True)
_db = sqlite3.connect(DB_PATH)
_db.execute(
    "CREATE TABLE IF NOT EXISTS tweets(id INTEGER PRIMARY KEY, text TEXT UNIQUE, ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
)
cutoff = datetime.utcnow() - timedelta(days=TWEET_DEDUP_WINDOW)
_db.execute("DELETE FROM tweets WHERE ts < ?", (cutoff.isoformat(),))
_db.commit()


def _tweet_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _is_duplicate(text: str) -> bool:
    h = _tweet_hash(text)
    cur = _db.execute("SELECT 1 FROM tweets WHERE text=?", (h,))
    return cur.fetchone() is not None


def _record_tweet(text: str) -> None:
    h = _tweet_hash(text)
    _db.execute("INSERT OR IGNORE INTO tweets(text) VALUES(?)", (h,))
    _db.commit()

@dataclass
class TwitterAgent:
    idx: int
    name: str
    personality: str
    dry_run: bool = False
    api_key: Optional[str] = field(repr=False, default=None)
    api_secret: Optional[str] = field(repr=False, default=None)
    access_token: Optional[str] = field(repr=False, default=None)
    access_secret: Optional[str] = field(repr=False, default=None)
    client: Optional[tweepy.API] = field(init=False, default=None)

    def __post_init__(self) -> None:
        self._load_creds_from_env()
        if not self.dry_run:
            self.authenticate()
        else:
            log.info("%s running in dry run mode", self.name)

    def _load_creds_from_env(self) -> None:
        if not self.api_key:
            prefix = f"TWITTER_AGENT{self.idx}_"
            self.api_key = os.getenv(prefix + "API_KEY")
            self.api_secret = os.getenv(prefix + "API_SECRET")
            self.access_token = os.getenv(prefix + "ACCESS_TOKEN")
            self.access_secret = os.getenv(prefix + "ACCESS_SECRET")

    def authenticate(self) -> None:
        if self.dry_run:
            log.info("%s authenticate skipped (dry run)", self.name)
            return
        # ---------- OAuth 1.0a (needed for user-context writes) ----------
        self._auth = tweepy.OAuth1UserHandler(
            self.api_key,
            self.api_secret,
            self.access_token,
            self.access_secret,
        )

        # v1.1 client (read-only for free tier)
        self.api_v1 = tweepy.API(self._auth, wait_on_rate_limit=True)

        # v2 client (write + read, same creds)
        self.client = tweepy.Client(
            consumer_key=self.api_key,
            consumer_secret=self.api_secret,
            access_token=self.access_token,
            access_token_secret=self.access_secret,
            wait_on_rate_limit=True,
        )

        log.info("%s authenticated (v1 read, v2 write)", self.name)

    def craft_post(self) -> str:
        greetings = [
            "Hello",
            "Hi there",
            "Hey",
            "Greetings",
            "Howdy",
            "Yo",
            "Sup",
            "What's up",
            "Good day",
            "Salutations"
        ]
        actions = [
            "says",
            "exclaims",
            "whispers",
            "shouts",
            "murmurs",
            "announces",
            "proclaims",
            "states",
            "declares",
            "expresses"
        ]
        greeting = random.choice(greetings)
        action = random.choice(actions)
        return f"{greeting}! {self.name} {action} this in a {self.personality} manner."

    def craft_reply(self, original_text: str) -> str:
        return quickfire.create_reply(self.personality, original_text)

    @retry(wait=wait_random_exponential(multiplier=2, max=60), stop=stop_after_attempt(5), reraise=True)
    def post(self, text: str) -> int:
        if _is_duplicate(text):
            log.info("duplicate avoided")
            return -1
        if self.dry_run:
            log.info("%s post skipped (dry run): %s", self.name, text)
            return -1
        resp = self.client.create_tweet(text=text)
        tweet_id = resp.data["id"]
        log.info("%s posted tweet %s", self.name, tweet_id)
        _record_tweet(text)
        return tweet_id

    @retry(wait=wait_random_exponential(multiplier=2, max=60), stop=stop_after_attempt(5), reraise=True)
    def reply(
        self,
        tweet_id: int,
        text: Optional[str] = None,
        original_text: Optional[str] = None,
    ) -> int:
        if text is None:
            text = self.craft_reply(original_text or "")
        if self.dry_run:
            log.info("%s reply skipped (dry run) to %s: %s", self.name, tweet_id, text)
            return -1
        resp = self.client.create_tweet(text=text, in_reply_to_tweet_id=tweet_id)
        reply_id = resp.data["id"]
        log.info("%s replied with %s", self.name, reply_id)
        return reply_id

    async def check_mentions(self, since_id: Optional[int] = None) -> int:
        if self.dry_run:
            log.info("%s check_mentions skipped (dry run)", self.name)
            return since_id or 1
        timeline = self.api_v1.mentions_timeline(
            since_id=since_id, tweet_mode="extended", count=20
        )
        new_since = since_id or 1
        for status in reversed(timeline):
            new_since = max(status.id, new_since)
            text = f"@{status.user.screen_name} {self.name} replies in a {self.personality} style."
            try:
                self.client.create_tweet(
                    text=text,
                    in_reply_to_tweet_id=status.id,
                )
                log.info("%s replied to %s", self.name, status.id)
            except tweepy.TweepyException as exc:
                log.warning("%s reply failed: %s", self.name, exc)
        return new_since
