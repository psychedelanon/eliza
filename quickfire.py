import os
import logging
import random
from typing import Optional

log = logging.getLogger("quickfire")

# Hashtags used to spice up posts
HASH_TAGS = ["#Alpha", "#CryptoLife", "#OnChain", "#MemeMagic"]


def _get_openai() -> Optional[object]:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        return None
    try:
        import openai  # type: ignore
    except ImportError:
        log.warning("openai package not installed; using stub responses")
        return None
    openai.api_key = key
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
        text = resp.choices[0].message["content"].strip()
    # Add flavour with hashtags and emojis
    text += " " + random.choice(HASH_TAGS) + " " + random.choice(["🔥", "⚡", "🚀", "✨"])
    return text


def create_reply(persona: str, original: str) -> str:
    """Generate a persona flavoured reply to *original*."""
    openai = _get_openai()
    if not openai:
        return f"[stub] 🤝 {persona} agrees"
    prompt = (
        f"Reply to the following tweet in a {persona} voice, be witty, max 200 chars.\n\nORIGINAL: {original}"
    )
    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.choices[0].message["content"].strip()

