"""Lore Master persona posting $BITCOIN lore."""
from __future__ import annotations

import random
from typing import Optional, Tuple

from agents.base import TwitterAgent
from agents.personas import LoreMaster
from eliza.llm import complete


class AgentLoreMaster(TwitterAgent, LoreMaster):
    """Sproto-style lore dropper."""

    def __init__(self, *, idx: int, name: str, personality: str, dry_run: bool = False) -> None:
        TwitterAgent.__init__(self, idx=idx, name=name, personality=personality, dry_run=dry_run)
        LoreMaster.__init__(self)

    def create_post(self) -> Tuple[str, Optional[str]]:
        prompt = self.build_prompt()
        text = complete(prompt, temperature=1.0, max_tokens=180).strip().strip('"').strip("'")
        if "$BITCOIN" not in text:
            text = f"$BITCOIN {text}"
        if not any(tag in text for tag in self.hashtag_pool):
            text = f"{text} {random.choice(self.hashtag_pool)}"
        return text[:240], None
