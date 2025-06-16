import os
import logging
from typing import Optional

log = logging.getLogger("quickfire")


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
        return f"A short post in a {persona} style."
    prompt = f"Write a short tweet in a {persona} style."
    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.choices[0].message["content"].strip()


def create_reply(persona: str, original: str) -> str:
    """Generate a reply to *original* in the given persona."""
    openai = _get_openai()
    if not openai:
        return f"Replying in a {persona} way to: {original}"
    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"You reply in a {persona} manner."},
            {"role": "user", "content": original},
        ],
    )
    return resp.choices[0].message["content"].strip()

