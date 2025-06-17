"""Template for new Twitter agent."""
from __future__ import annotations

from typing import Optional, Tuple

from agents.base import TwitterAgent


def create_post(persona: str) -> Tuple[str, Optional[str]]:
    """Return a placeholder post text."""
    return f"Hello from {persona}!", None


def run_once(*, dry_run: bool = False) -> None:
    """Scaffold run_once for new agent."""
    agent = TwitterAgent(idx=0, name="TemplateAgent", personality="template", dry_run=dry_run)
    text, img = create_post(agent.personality)
    agent.post((text, img), dry_run=dry_run)
