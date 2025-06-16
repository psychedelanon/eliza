import logging
import os
import random
from typing import List, Optional

log = logging.getLogger("quickfire")

# Default hashtags used to spice up posts
DEFAULT_HASH_TAGS = ["#Alpha", "#CryptoLife", "#OnChain", "#MemeMagic"]

# Environment variable for overriding hashtags
_HASHTAG_ENV = "AQUA_HASHTAGS"


def _get_hashtags() -> List[str]:
    """Return hashtags from the environment variable if provided."""
    env_val = os.getenv(_HASHTAG_ENV)
    if env_val:
        tags = [t.strip() for t in env_val.split(",") if t.strip()]
        if tags:
            return tags
    return DEFAULT_HASH_TAGS


def is_live() -> bool:
    """Return True if OPENAI_API_KEY is configured."""
    return bool(os.getenv("OPENAI_API_KEY"))


def _get_openai() -> Optional[object]:
    if not is_live():
        return None
    try:
        import openai  # type: ignore
    except ImportError:
        log.warning("openai package not installed; using stub responses")
        return None
    openai.api_key = os.getenv("OPENAI_API_KEY")
    return openai


def create_post(persona: str) -> str:
    """Generate a tweet text in the given persona."""
    openai = _get_openai()
    if not openai:
        text = f"A short post in a {persona} style."
    else:
        prompt = f"Write a short tweet in a {persona} style."
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
        )
        usage = resp.get("usage", {})
        log.info(
            "openai cost",
            extra={
                "event": "openai_cost",
                "completion_tokens": usage.get("completion_tokens", 0),
                "prompt_tokens": usage.get("prompt_tokens", 0),
            },
        )
        text = resp.choices[0].message["content"].strip()
    hashtags = _get_hashtags()
    # Add flavour with hashtags and emojis
    text += (
        " " + random.choice(hashtags) + " " + random.choice(["🔥", "⚡", "🚀", "✨"])
    )
    return text


def create_reply(persona: str, original: str) -> str:
    """Generate a persona flavoured reply to *original*."""
    openai = _get_openai()
    if not openai:
        return f"[stub] 🤝 {persona} agrees"
    prompt = f"Reply to the following tweet in a {persona} voice, be witty, max 200 chars.\n\nORIGINAL: {original}"
    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
    )
    usage = resp.get("usage", {})
    log.info(
        "openai cost",
        extra={
            "event": "openai_cost",
            "completion_tokens": usage.get("completion_tokens", 0),
            "prompt_tokens": usage.get("prompt_tokens", 0),
        },
    )
    return resp.choices[0].message["content"].strip()
