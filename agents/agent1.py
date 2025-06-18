"""Agent 1 – Sproto ramblings."""
from __future__ import annotations

import random
import re
from typing import Tuple

from agents.base import TwitterAgent
from eliza.llm import complete

log = __import__("logging").getLogger(__name__)

SYSTEM_PROMPT = """
You are **Sproto** – a crypto foodie who loves breakfast and $BITCOIN.
Voice & style:
• Calm, food-focused musings about crypto
• Share what you're having for breakfast, always with a $BITCOIN twist
• Use gentle food metaphors and cooking terms
• Keep it clean and wholesome
Hard constraints (MUST):
1. ≤ 240 Unicode characters total
2. Always mention $BITCOIN
3. Always mention what you're having for breakfast
4. Use one cooking term (e.g. simmer, sauté, whisk, fold)
5. Use one spice or herb (e.g. cinnamon, basil, thyme)
6. End with #HarryPotterObamaSonic10Inu
"""

FEWSHOT_ASSISTANT = [
    "Just whisking up some cinnamon pancakes while $BITCOIN simmers on low heat. Perfect morning vibes. #HarryPotterObamaSonic10Inu",
    "Folding fresh basil into my omelette as $BITCOIN gently rises. Breakfast of champions. #HarryPotterObamaSonic10Inu",
    "Sautéing mushrooms with thyme, watching $BITCOIN do its thing. Morning ritual. #HarryPotterObamaSonic10Inu"
]

USER_PROMPT = """
Morning briefing:
Generate ONE tweet about your breakfast, always mentioning $BITCOIN.
Do NOT output anything except the tweet text itself.
"""

BONUS_TAG = "#HarryPotterObamaSonic10Inu"
TICKER = "$BITCOIN"


def _build_prompt(topic: str) -> str:
    """Return a prompt for generating a tweet."""

    examples = "\n".join(FEWSHOT_ASSISTANT)
    return (
        "Sproto breakfast prompt (1-240 chars)\n"
        "Style examples:\n"
        f"{examples}\n"
        f"User topic: {topic}\n"
        "Tweet:"
    )


def _generate_tweet() -> str:
    """Generate a tweet using the LLM."""
    prompt = f"{SYSTEM_PROMPT}\n\n{FEWSHOT_ASSISTANT}\n\nUser: Generate a tweet."
    raw = complete(prompt, temperature=1.05, max_tokens=180)
    tweet = raw.strip()[:240]

    # Ensure $BITCOIN is mentioned
    if TICKER not in tweet:
        words = tweet.split()
        if len(words) < 2:
            tweet = f"{TICKER} {tweet}"
        else:
            idx = random.randint(1, len(words)-1)
            words.insert(idx, TICKER)
            tweet = " ".join(words)
        tweet = tweet.strip()[:240]

    # Always end with the bonus tag
    tweet = re.sub(re.escape(BONUS_TAG), "", tweet, flags=re.IGNORECASE)
    tweet = tweet.strip()
    tweet = f"{tweet} {BONUS_TAG}".strip()

    return tweet[:240]


# Public API --------------------------------------------------------------------

def create_post(persona: str = "Sproto") -> Tuple[str, None]:
    """Return ``(text, None)`` for posting."""
    text = _generate_tweet()
    return text, None


def run_once(*, dry_run: bool = False) -> None:
    """Generate and post one Sproto tweet."""
    agent = TwitterAgent(idx=1, name="Agent1", personality="Sproto", dry_run=dry_run)
    text, img = create_post()
    post_id = agent.post((text, img), dry_run=dry_run)
    if dry_run:
        print("DRY RUN TWEET:\n", text)
    log.info(
        "sproto_post",
        extra={"agent": "Agent1", "event": "posted", "post_id": post_id, "text": text},
    )


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.once:
        run_once(dry_run=args.dry_run)
