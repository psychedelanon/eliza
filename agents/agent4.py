from __future__ import annotations

import asyncio
import random
from pathlib import Path
from typing import Optional, Tuple

import yaml

from agents.base import TwitterAgent
from agents.social import amplify
from eliza import llm

PERSONAS = yaml.safe_load((Path(__file__).parent / "personas.yaml").read_text())
BONUS_TAG = "#HarryPotterObamaSonic10Inu"


def _maybe_tag(text: str) -> str:
    if random.random() < 0.1 and BONUS_TAG not in text:
        suffix = f" {BONUS_TAG}"
        if len(text) + len(suffix) > 240:
            text = text[: 240 - len(suffix)].rstrip()
        text += suffix
    return text[:240]


class Agent4(TwitterAgent):
    tag = "GremlinGM"

    def create_post(self) -> Tuple[str, Optional[str], Optional[str]]:
        persona = PERSONAS[self.tag]
        prompt = (
            f"{persona['system']}\n"
            f"Generate a single cheerful morning tweet about $BITCOIN in the style {persona['style']}.\n"
            "Limit to 240 characters."
        )
        text = llm.complete(prompt, max_tokens=100)
        text = text.strip()[:240]
        text = _maybe_tag(text)
        return text, None, None


def run_once(*, dry_run: bool = False) -> None:
    agent = Agent4(idx=4, name="Agent4", personality=Agent4.tag, dry_run=dry_run)
    text, img, _ = agent.create_post()
    tweet_id = agent.post((text, img), dry_run=dry_run)
    peers = [
        TwitterAgent(idx=5, name="Agent5", personality="GremlinMeme", dry_run=dry_run),
        TwitterAgent(idx=6, name="Agent6", personality="GremlinLore", dry_run=dry_run),
    ]
    if tweet_id != -1:
        asyncio.run(amplify(agent, peers, dry=dry_run))

