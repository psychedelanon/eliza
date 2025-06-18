import os
import logging
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from typing import Optional
import time
import asyncio
from croniter import croniter

import sys
sys.path.append(str(Path(__file__).parent.parent / "vendor"))
sys.path.append(str(Path(__file__).parent.parent))  # Add project root for metrics.py
import blacksmith_forge.quickfire as quickfire
import openai
# import quickfire  # removed old import
# import blacksmith_forge.quickfire as qf  # keep as is if used elsewhere

from metrics import OPENAI_CALLS, CROSS_ENGAGE_TOTAL, CROSS_ENGAGE_LATENCY_SECONDS
from agents.quality import validate, get_quality_score
from agents.generator import get_engagement_weights

import tweepy
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
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
cutoff = datetime.now(timezone.utc) - timedelta(days=TWEET_DEDUP_WINDOW)
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
    
    # Skip moderation in dry-run mode to save costs
    if os.getenv("DRY_RUN", "true").lower() == "true":
        return True
        
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
    name: str
    personality: str
    idx: int = 0
    dry_run: bool = False
    api_key: Optional[str] = field(repr=False, default=None)
    api_secret: Optional[str] = field(repr=False, default=None)
    access_token: Optional[str] = field(repr=False, default=None)
    access_secret: Optional[str] = field(repr=False, default=None)
    client: Optional[tweepy.API] = field(init=False, default=None)
    last_media_path: Optional[str] = field(init=False, default=None)
    last_post_id: Optional[int] = field(init=False, default=None)
    llm: Optional[str] = field(init=False, default=None)

    def __post_init__(self) -> None:
        self._load_creds_from_env()
        # Only authenticate if all credentials are present
        if not self.dry_run and all([self.api_key, self.api_secret, self.access_token, self.access_secret]):
            self.authenticate()

    def _load_creds_from_env(self) -> None:
        if not self.api_key:
            prefix = f"TWITTER_AGENT{self.idx}_"
            self.api_key = os.getenv(prefix + "API_KEY")
            self.api_secret = os.getenv(prefix + "API_SECRET")
            self.access_token = os.getenv(prefix + "ACCESS_TOKEN")
            self.access_secret = os.getenv(prefix + "ACCESS_SECRET")
        print(f"[DEBUG] {self.name} idx={self.idx} api_key={self.api_key} api_secret={self.api_secret} access_token={self.access_token} access_secret={self.access_secret}")

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

    def _generate_reply(self, original_text: str) -> str:
        """Generate a reply to the original text."""
        return self.craft_reply(original_text)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((tweepy.TweepyException, requests.RequestException)),
    )
    async def reply(self, tweet_id: int, text: str, *, dry_run: Optional[bool] = None) -> int:
        """Reply to a tweet."""
        if dry_run is None:
            dry_run = self.dry_run
            
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
            return 456  # Return dummy ID for dry run
            
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

    async def post(self, content):
        """Async post method for compatibility with tests."""
        if isinstance(content, tuple):
            text, img = content
        else:
            text, img = content, None
            
        # Quality validation
        is_valid, issues = validate(text, agent_name=self.name)
        if not is_valid:
            log.warning(
                "%s quality validation failed: %s",
                self.name,
                issues,
                extra={"agent": self.name, "event": "quality_fail", "issues": issues},
            )
            # Log quality failure metric
            if hasattr(self, 'quality_fail_total'):
                self.quality_fail_total += 1
            return -1
        
        # Log quality pass
        quality_score = get_quality_score(text)
        log.info(
            "%s quality validation passed (score: %.2f)",
            self.name,
            quality_score,
            extra={"agent": self.name, "event": "quality_pass", "score": quality_score},
        )
            
        if not _passes_moderation(text):
            reason = "moderation"
            log.warning(
                "%s blocked by moderation",
                self.name,
                extra={"agent": self.name, "event": "moderation_blocked"},
            )
            return -1
            
        # Check for duplicates
        if _is_duplicate(text):
            log.info(
                "%s duplicate avoided: %s",
                self.name,
                text,
                extra={"agent": self.name, "event": "duplicate"},
            )
            return -1
            
        if self.dry_run:
            log.info(
                "%s would post: %s",
                self.name,
                text,
                extra={"agent": self.name, "event": "posted", "dry": True},
            )
            return 123  # Return dummy ID for dry run
            
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
            self.last_post_id = tweet_id
            return tweet_id
        except Exception as exc:
            log.error(
                "%s post failed: %s",
                self.name,
                exc,
                extra={"agent": self.name, "event": "error", "error": str(exc)},
            )
            raise

    async def _maybe_cross_engage(self) -> None:
        """Smart cross-engagement with other agent's tweets based on persona style."""
        import random
        from eliza.shared_memory import get_shared_memory
        
        await asyncio.sleep(random.uniform(0, 30))
        
        # Get engagement weights for this persona
        engagement_weights = get_engagement_weights(self.name)
        
        # Decide whether to engage (30% base probability)
        if random.random() < 0.3:
            mem = get_shared_memory()
            recent = mem.get_recent_posts(exclude_agent=self.name)
            if not recent:
                return
                
            # Prefer newer posts (< 30 minutes old)
            recent_filtered = [
                post for post in recent 
                if (datetime.now(timezone.utc) - post.get("timestamp", datetime.now(timezone.utc))).total_seconds() < 1800
            ]
            target_posts = recent_filtered if recent_filtered else recent
            target = random.choice(target_posts)
            
            # Choose action based on persona weights
            actions = list(engagement_weights.keys())
            weights = list(engagement_weights.values())
            action = random.choices(actions, weights=weights)[0]
            
            with CROSS_ENGAGE_LATENCY_SECONDS.labels(agent=self.name, action=action).time():
                if action == "like":
                    if self.dry_run:
                        log.info(
                            "smart_cross_engage",
                            extra={
                                "agent": self.name, 
                                "event": "cross_engage", 
                                "target": target["id"], 
                                "action": "like",
                                "target_agent": target.get("agent", "unknown")
                            },
                        )
                    else:
                        self.api_v1.create_favorite(target["id"])
                    CROSS_ENGAGE_TOTAL.labels(agent=self.name, action="like", origin_agent=target.get("agent", "unknown")).inc()
                    
                elif action == "reply":
                    # Generate persona-specific reply
                    reply_text = self._generate_smart_reply(target["text"], target.get("agent", "unknown"))
                    if self.dry_run:
                        log.info(
                            "smart_cross_engage",
                            extra={
                                "agent": self.name, 
                                "event": "cross_engage", 
                                "target": target["id"], 
                                "action": "reply",
                                "target_agent": target.get("agent", "unknown"),
                                "reply": reply_text[:50] + "..." if len(reply_text) > 50 else reply_text
                            },
                        )
                    else:
                        self.client.create_tweet(text=reply_text, in_reply_to_tweet_id=target["id"])
                    CROSS_ENGAGE_TOTAL.labels(agent=self.name, action="reply", origin_agent=target.get("agent", "unknown")).inc()
                    
                elif action == "quote":
                    # Quote tweet with persona-specific commentary
                    quote_text = self._generate_quote_commentary(target["text"], target.get("agent", "unknown"))
                    if self.dry_run:
                        log.info(
                            "smart_cross_engage",
                            extra={
                                "agent": self.name, 
                                "event": "cross_engage", 
                                "target": target["id"], 
                                "action": "quote",
                                "target_agent": target.get("agent", "unknown"),
                                "quote": quote_text[:50] + "..." if len(quote_text) > 50 else quote_text
                            },
                        )
                    else:
                        self.client.create_tweet(text=quote_text, quoted_tweet_id=target["id"])
                    CROSS_ENGAGE_TOTAL.labels(agent=self.name, action="quote", origin_agent=target.get("agent", "unknown")).inc()
        return

    def _generate_smart_reply(self, original_text: str, target_agent: str) -> str:
        """Generate a smart reply based on persona and target."""
        # Base reply from persona
        base_reply = self.craft_reply(original_text)
        
        # Add mention if not already present
        if f"@{target_agent}" not in base_reply and len(base_reply) < 200:
            base_reply = f"@{target_agent} {base_reply}"
        
        # Ensure it fits within reply limits
        return base_reply[:150]

    def _generate_quote_commentary(self, original_text: str, target_agent: str) -> str:
        """Generate quote tweet commentary based on persona."""
        # Persona-specific commentary patterns
        commentary_patterns = {
            "LoreMaster": [
                "The ancient scrolls speak of this wisdom",
                "A prophecy foretold this moment",
                "The mystical forces align"
            ],
            "MemeLord": [
                "This is the way 🚀",
                "Diamond hands energy 💎",
                "WAGMI vibes detected"
            ],
            "AlphaScry": [
                "Alpha detected 📊",
                "The charts confirm this",
                "Insider knowledge revealed"
            ],
            "GremlinGM": [
                "Chaos magic flows through this",
                "The game master approves",
                "Critical hit on the truth"
            ]
        }
        
        patterns = commentary_patterns.get(self.name, ["This is the way"])
        commentary = random.choice(patterns)
        
        # Add mention if space allows
        if len(commentary) < 200:
            commentary = f"@{target_agent} {commentary}"
        
        return commentary[:240]

    async def run(self) -> None:
        """Default run loop for persona agents."""
        import random
        import asyncio
        schedule_cron = getattr(self, "schedule_cron", None)
        while True:
            # Handle both sync and async craft_post methods
            if asyncio.iscoroutinefunction(self.craft_post):
                text, img = await self.craft_post()
            else:
                text, img = self.craft_post()
                
            await self.post((text, img))
            if schedule_cron:
                now = datetime.now(timezone.utc)
                next_dt = croniter(schedule_cron, now).get_next(datetime)
                sleep_s = (next_dt - now).total_seconds()
                await asyncio.sleep(sleep_s)
            else:
                await asyncio.sleep(random.uniform(60, 180))

    async def like(self, tweet_id: int, *, dry_run: Optional[bool] = None) -> None:
        dry = self.dry_run if dry_run is None else dry_run
        if dry:
            log.info("%s would like %s", self.name, tweet_id, extra={"agent": self.name, "event": "liked", "dry": True})
            return
        try:
            self.client.like(tweet_id)
            log.info("%s liked %s", self.name, tweet_id, extra={"agent": self.name, "event": "liked"})
        except Exception as exc:
            log.warning("%s like failed: %s", self.name, exc, extra={"agent": self.name, "event": "error"})

    async def follow(self, username: str, *, dry_run: Optional[bool] = None) -> None:
        dry = self.dry_run if dry_run is None else dry_run
        if dry:
            log.info("%s would follow %s", self.name, username, extra={"agent": self.name, "event": "follow", "dry": True})
            return
        try:
            self.client.follow_user(username)
        except Exception as exc:
            log.warning("%s follow failed: %s", self.name, exc, extra={"agent": self.name, "event": "error"})

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

    async def react_to_event(self, event: dict) -> None:
        """React to events (default noop, override in subclasses)."""
        pass

    def make_price_reply(self, event: dict) -> str:
        """Generate a price reply based on event data."""
        btc = event.get("btc", 0)
        hpo = event.get("hpo", 0)
        
        if btc == 0 or hpo == 0:
            return f"The charts speak of $BITCOIN's journey #HarryPotterObamaSonic10Inu"
        
        diff_pct = ((hpo - btc) / btc) * 100
        
        # Use persona-specific templates if available
        if hasattr(self, 'price_reply_templates') and self.price_reply_templates:
            template = random.choice(self.price_reply_templates)
            return template.format(diff=diff_pct)[:150]
        
        # Default price reply template
        template = "The scrolls record a {diff:+.2f}% swing in the cosmic balance #HarryPotterObamaSonic10Inu"
        return template.format(diff=diff_pct)[:150]
