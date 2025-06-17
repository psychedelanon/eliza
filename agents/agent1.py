"""Agent 1 – Sproto ramblings."""
from __future__ import annotations

import datetime as dt
import pathlib
import random
import textwrap
from typing import Tuple

from .base import TwitterAgent
from eliza.llm import complete

log = __import__("logging").getLogger(__name__)

THIS_DIR = pathlib.Path(__file__).parent
DIALOGUE_YAML = THIS_DIR / "sproto_corpus.yaml"

with DIALOGUE_YAML.open("r", encoding="utf-8") as fh:
    CORPUS: list[str] = __import__("yaml").safe_load(fh)

_SPICE_WORDS = ["onions", "macro", "laser", "fren", "pump"]
_HASHTAGS = ["#BTC", "#ETH", "#Macro"]
_OPTIONAL_TAG = "#HarryPotterObamaSonic10Inu"


def _build_prompt(spice: str) -> str:
    """Construct the prompt for Sproto LLM completion."""

    shots = random.sample(CORPUS, k=5)
    shots_txt = "\n".join(f"- {s}" for s in shots)
    today = dt.datetime.now(dt.timezone.utc).strftime("%b %d %Y")
    return textwrap.dedent(
        f"""
        You are Sproto, a chaotic but witty crypto commentator on X.
        Today is {today}. One tweet only:
        • 1-240 characters using crypto slang.
        • Include the word '{spice}'.
        • Must contain #SPROTO and may add one of {_HASHTAGS}.
        • Keep it clean.

        Style examples:
        {shots_txt}

        Tweet:
        """
    ).strip()


def _generate_tweet() -> str:
    spice = random.choice(_SPICE_WORDS)
    prompt = _build_prompt(spice)
    tweet = complete(prompt, temperature=1.05, model="gpt-4o-mini", max_tokens=80)
    if random.random() < 0.1 and _OPTIONAL_TAG not in tweet:
        tweet = f"{tweet.strip()} {_OPTIONAL_TAG}"
    if "#SPROTO" not in tweet.upper():
        tweet = f"{tweet.strip()} #SPROTO"
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
