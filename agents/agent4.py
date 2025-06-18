from __future__ import annotations

import asyncio
import random
import logging
from pathlib import Path
from typing import Optional, Tuple, List

import yaml

from agents.base import TwitterAgent
from agents.social import amplify
from eliza.llm import complete

log = logging.getLogger("agent")

PERSONAS_PATH = Path(__file__).parent / "personas.yaml"


class GremlinGM(TwitterAgent):
    """Gremlin GM: Morning hype bot with social amplification."""
    def __init__(self, *, idx: int, name: str, personality: str, dry_run: bool = False) -> None:
        super().__init__(idx=idx, name=name, personality=personality, dry_run=dry_run)
        self.prompt = self._load_prompt()

    def _load_prompt(self) -> dict:
        if not PERSONAS_PATH.exists():
            return {"system": "You are GremlinGM, a crypto hype gremlin."}
        with open(PERSONAS_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data.get("GremlinGM", {"system": "You are GremlinGM, a crypto hype gremlin."})

    def _random_hashtag(self) -> str:
        return random.choice(["#HarryPotterObamaSonic10Inu", "#BTC"])

    def _maybe_vibe_check(self) -> Optional[str]:
        if random.random() < 0.2:
            return random.choice([
                "Vibe check: How are we feeling today?",
                "Energy check! Drop your mood in the replies.",
                "Who's got the best breakfast energy?",
                "Stay hydrated, gremlins!",
            ])
        return None

    def craft_post(self) -> Tuple[str, None]:
        system = self.prompt.get("system", "You are GremlinGM, a crypto hype gremlin.")
        style = self.prompt.get("style", "")
        user = (
            "Morning hype time! Tweet ≤ 240 chars, mention $BITCOIN, end with "
            f"{self._random_hashtag()} at random.  Sprinkle 1‑2 emojis."
        )
        messages = [
            {"role": "system", "content": [{"type": "text", "text": system + (f"\nStyle: {style}" if style else "")}]},
            {"role": "user", "content": [{"type": "text", "text": user}]},
        ]
        try:
            text = complete(messages, temperature=1.1, max_tokens=180).strip()
        except Exception as exc:
            log.warning("llm.complete failed: %s", exc)
            text = "Good morning $BITCOIN believers! ☕✨ #HarryPotterObamaSonic10Inu"
        # Remove leading/trailing quotes
        text = text.strip('"').strip("'")
        # Ensure $BITCOIN is mentioned
        if "$BITCOIN" not in text:
            text = f"$BITCOIN {text}"
        # Ensure hashtag at end
        if not text.endswith("#HarryPotterObamaSonic10Inu") and not text.endswith("#BTC"):
            text = f"{text} {self._random_hashtag()}"
        # Sprinkle 1-2 emojis if not present
        if sum(1 for c in text if c in "😀😃😄😁😆😅😂🤣😊😇🙂🙃😉😌😍🥰😘😗😙😚😋😛😝😜🤪🤨🧐🤓😎🥳🤩🥺🥲🥹🥸🤠🥶🥵🥴🤢🤮🤧😷🤒🤕🤑🤠🥳🥸😈👿\u001f47f👹👺💀👻👽👾🤖💩") < 1:
            text += random.choice([" ☀️", " ☕", " ✨", " 🚀", " 😈", " 😎"])
        # 20% chance to add a vibe check
        vibe = self._maybe_vibe_check()
        if vibe:
            text = f"{text}\n{vibe}"
        # Trim to 240 chars
        text = text[:240]
        return text, None

    async def after_post(self, peers: List[TwitterAgent]) -> None:
        await amplify(self, peers, dry=self.dry_run)


def run_once(*, dry_run: bool = False) -> None:
    agent = GremlinGM(idx=4, name="Agent4", personality="GremlinGM", dry_run=dry_run)
    text, img = agent.craft_post()
    tweet_id = agent.post((text, img), dry_run=dry_run)
    peers = [
        TwitterAgent(idx=5, name="Agent5", personality="GremlinMeme", dry_run=dry_run),
        TwitterAgent(idx=6, name="Agent6", personality="GremlinLore", dry_run=dry_run),
    ]
    if tweet_id != -1:
        asyncio.run(agent.after_post(peers))

