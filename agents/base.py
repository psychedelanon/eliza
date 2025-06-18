import os
import logging
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional, Union, Tuple
import time

import sys
sys.path.append(str(Path(__file__).parent.parent / "vendor"))
sys.path.append(str(Path(__file__).parent.parent))  # Add project root for metrics.py
import blacksmith_forge.quickfire as quickfire
import openai
# import quickfire  # removed old import
# import blacksmith_forge.quickfire as qf  # keep as is if used elsewhere

from metrics import TWEETS_POSTED, REPLIES_POSTED, OPENAI_CALLS

import tweepy
from tenacity import retry, wait_random_exponential, stop_after_attempt, wait_exponential, retry_if_exception_type
import requests

log = logging.getLogger("agent")

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
openai_client = openai.OpenAI(api_key=OPENAI_KEY) if OPENAI_KEY else None
BANNED_WORDS = {"spam", "scam"}

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


def _passes_moderation(text: str) -> bool:
    """Check if text passes moderation."""
    # Safety guard against tuple input
    if isinstance(text, tuple):
        text = text[0]
        
    if not text:
        return False
    lower = text.lower()
    if any(word in lower for word in BANNED_WORDS):
        return False
    try:
        import openai
    except Exception as exc:  # pragma: no cover - import error
        print(f"openai moderation failed: {exc}")
        return True
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY not set")
        return True
    client = openai.OpenAI(api_key=api_key)
    try:
        resp = client.moderations.create(input=text)
        return not any(category for category in resp.results[0].categories.__dict__.values() if category)
    except Exception as exc:  # pragma: no cover - moderation error
        print(f"openai moderation failed: {exc}")
        return True


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
    last_media_path: Optional[str] = field(init=False, default=None)

    def __post_init__(self) -> None:
        self._load_creds_from_env()
        if not self.dry_run:
            self.authenticate()

    def _load_creds_from_env(self) -> None:
        if not self.api_key:
            prefix = f"TWITTER_AGENT{self.idx}_"
            self.api_key = os.getenv(prefix + "API_KEY")
            self.api_secret = os.getenv(prefix + "API_SECRET")
            self.access_token = os.getenv(prefix + "ACCESS_TOKEN")
            self.access_secret = os.getenv(prefix + "ACCESS_SECRET")

    def authenticate(self) -> None:
        if self.dry_run:
            log.info(
                "%s authenticate skipped (dry run)",
                self.name,
                extra={"agent": self.name, "event": "auth_skip"},
            )
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

        log.info(
            "%s authenticated (v1 read, v2 write)",
            self.name,
            extra={"agent": self.name, "event": "auth"},
        )

    def craft_post(self):
        OPENAI_CALLS.inc()
        # Check if agent has its own create_post implementation
        if hasattr(self, 'create_post'):
            result = self.create_post()
            if isinstance(result, tuple) and len(result) == 3:
                text, img_path, alt_text = result
                if img_path:
                    self.last_media_path = str(img_path)
                    log.info(
                        "media generated",
                        extra={
                            "agent": self.name,
                            "event": "media_ready",
                            "path": self.last_media_path,
                        },
                    )
                return text, img_path
            return result, None
        
        # Fall back to quickfire implementation
        text = quickfire.create_post(self.personality)
        if os.getenv("MEDIA_ENABLE", "false").lower() == "true":
            img_path = quickfire.generate_image(self.personality, text)
            self.last_media_path = str(img_path)
            log.info(
                "media generated",
                extra={
                    "agent": self.name,
                    "event": "media_ready",
                    "path": self.last_media_path,
                },
            )
            return text, self.last_media_path
        self.last_media_path = None
        return text, None

    def craft_reply(self, original_text: str) -> str:
        return quickfire.create_reply(self.personality, original_text)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((tweepy.TweepyException, requests.RequestException)),
        reraise=True,
    )
    async def reply(self, tweet_id: int, original_text: str, *, dry_run: Optional[bool] = None) -> int:
        """Reply to a tweet."""
        if dry_run is None:
            dry_run = self.dry_run
            
        text = self._generate_reply(original_text)
        if not _passes_moderation(text):
            reason = "moderation"
            log.debug("%s skip=%s text=%r", self.name, reason, text, extra={"agent": self.name, "event": "skip", "reason": reason})
            log.warning(
                "%s blocked by moderation",
                self.name,
                extra={"agent": self.name, "event": "moderation_blocked"},
            )
            return -1
            
        if dry_run:
            log.info(
                "%s would reply: %s",
                self.name,
                text,
                extra={"agent": self.name, "event": "replied", "dry": True},
            )
            return int(time.time() * 1000)
            
        try:
            resp = self.client.create_tweet(
                text=text,
                in_reply_to_tweet_id=tweet_id,
            )
            tweet_id = resp.data["id"]
            log.info(
                "%s replied: %s",
                self.name,
                text,
                extra={"agent": self.name, "event": "replied"},
            )
            return tweet_id
        except Exception as exc:
            log.error(
                "%s reply failed: %s",
                self.name,
                exc,
                extra={"agent": self.name, "event": "error", "error": str(exc)},
            )
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((tweepy.TweepyException, requests.RequestException)),
        reraise=True,
    )
    async def post(self, text: str, img: Optional[str] = None) -> bool:
        """Post a tweet with optional image."""
        if not _passes_moderation(text):
            reason = "moderation"
            log.warning(f"Post rejected: {reason}")
            return False
            
        if not self.dry_run:
            try:
                if img and Path(img).exists():
                    media = self.api_v1.media_upload(img)
                    media_id = media.media_id
                    resp = self.client.create_tweet(text=text, media_ids=[media_id])
                else:
                    resp = self.client.create_tweet(text=text)
                    
                tweet_id = resp.data["id"]
                log.info(
                    "%s posted: %s",
                    self.name,
                    text,
                    extra={"agent": self.name, "event": "posted"},
                )
                _record_tweet(text)
                return True
            except Exception as exc:
                log.error(
                    "%s post failed: %s",
                    self.name,
                    exc,
                    extra={"agent": self.name, "event": "error", "error": str(exc)},
                )
                raise
        return False

    async def check_mentions(self, since_id: Optional[int] = None) -> int:
        if self.dry_run:
            log.info(
                "%s check_mentions skipped (dry run)",
                self.name,
                extra={"agent": self.name, "event": "mentions_skip"},
            )
            return since_id or 1
        try:
            user_id = self.client.get_me().data.id
            resp = self.client.get_users_mentions(user_id, since_id=since_id, max_results=20)
        except Exception as exc:
            log.warning(
                "%s mentions_unavailable: %s",
                self.name,
                exc,
                extra={"agent": self.name, "event": "mentions_unavailable"},
            )
            return since_id or 1
        timeline = resp.data or []
        new_since = since_id or 1
        for status in reversed(timeline):
            new_since = max(status.id, new_since)
            text = f"@{getattr(status, 'author_id', 'user')} {self.name} replies in a {self.personality} style."
            try:
                self.client.create_tweet(
                    text=text,
                    in_reply_to_tweet_id=status.id,
                )
                log.info(
                    "%s replied to %s",
                    self.name,
                    status.id,
                    extra={"agent": self.name, "event": "reply"},
                )
            except Exception as exc:
                log.warning(
                    "%s reply failed: %s",
                    self.name,
                    exc,
                    extra={"agent": self.name, "event": "error"},
                )
        return new_since
