"""Agent 1: Breakfast-themed tweets about $BITCOIN."""
import random
from typing import Optional, Tuple
from agents.base import TwitterAgent
from eliza.llm import complete

class Agent1(TwitterAgent):
    """Sproto‑style gremlin tweeter (morning ramblings)."""
    
    def __init__(self, *, idx: int, name: str, personality: str, dry_run: bool = False) -> None:
        """Initialize the agent.
        
        Args:
            idx: The index of the agent
            name: The name of the agent
            personality: The personality description
            dry_run: Whether to run in dry run mode
        """
        super().__init__(idx=idx, name=name, personality=personality, dry_run=dry_run)
        
    def _generate_tweet(self) -> str:
        """Generate a tweet about breakfast and $BITCOIN."""
        prompt = """You are a Twitter bot that posts about breakfast and $BITCOIN.
        Your tweets should:
        1. Always mention $BITCOIN
        2. Include breakfast food/coffee
        3. Be friendly and upbeat
        4. Be under 280 characters
        5. Include #HarryPotterObamaSonic10Inu
        
        Example tweets:
        - "Starting my day with a stack of pancakes and a side of $BITCOIN gains! 🥞📈 #HarryPotterObamaSonic10Inu"
        - "Nothing beats morning coffee and watching $BITCOIN wake up the market! ☕️📊 #HarryPotterObamaSonic10Inu"
        - "Breakfast of champions: avocado toast and $BITCOIN charts! 🥑📈 #HarryPotterObamaSonic10Inu"
        
        Generate a new tweet:"""
        
        raw = complete(prompt, temperature=1.05, max_tokens=180)
        text = raw.strip()
        # Remove leading/trailing quotes (single or double)
        text = text.strip('"').strip("'")
        
        # Ensure $BITCOIN is mentioned
        if "$BITCOIN" not in text:
            text = f"Enjoying breakfast while $BITCOIN {text}"
            
        # Ensure hashtag is present
        if "#HarryPotterObamaSonic10Inu" not in text:
            text = f"{text} #HarryPotterObamaSonic10Inu"
            
        return text
        
    def create_post(self) -> Tuple[str, Optional[str]]:
        """Create a breakfast-themed tweet about $BITCOIN."""
        text = self._generate_tweet()
        return text, None

def run_once(*, dry_run: bool = False) -> None:
    """Generate and post one Sproto tweet."""
    agent = Agent1(idx=1, name="Agent1", personality="Sproto", dry_run=dry_run)
    text, img = agent.create_post()
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
