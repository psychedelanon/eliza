from __future__ import annotations

from typing import Optional, Tuple

from agents.base import TwitterAgent
from agents.personas import Sage
from eliza.llm import complete


class AgentSage(TwitterAgent, Sage):
    def __init__(self, *, idx: int, name: str, personality: str, dry_run: bool = False) -> None:
        TwitterAgent.__init__(self, idx=idx, name=name, personality=personality, dry_run=dry_run)
        Sage.__init__(self)

    def create_post(self) -> Tuple[str, Optional[str]]:
        text = complete(self.build_prompt(), temperature=0.7, max_tokens=80).strip()
        if "$BITCOIN" not in text:
            text = f"$BITCOIN {text}"
        if not any(tag in text for tag in self.hashtag_pool):
            text = f"{text} {self.hashtag_pool[0]}"
        return text[:240], None
