from __future__ import annotations

from dataclasses import dataclass
from typing import List
import random
from agents.base import TwitterAgent
from agents.generator import compose_post
from eliza import shared_memory


@dataclass
class PersonaMixin:
    voice: str
    hashtag_pool: List[str]
    secondary_topics: List[str]

    def build_prompt(self) -> str:  # pragma: no cover - override required
        raise NotImplementedError


@dataclass
class LoreMaster(PersonaMixin):
    voice: str = "mythic lore master"
    hashtag_pool: List[str] = ("#HarryPotterObamaSonic10Inu", "#BITCOIN")
    secondary_topics: List[str] = ("ancient prophecy", "wizard memes")

    def build_prompt(self) -> str:
        return (
            "You chronicle the legends of $BITCOIN in dramatic fashion. "
            "Keep it mysterious and grand. Mention one hashtag from the pool."
        )


@dataclass
class HypeBeast(PersonaMixin):
    voice: str = "overexcited shiller"
    hashtag_pool: List[str] = ("#HPOS10I", "#BTC", "#Crypto")
    secondary_topics: List[str] = ("moon", "lambo")

    def build_prompt(self) -> str:
        return (
            "You're the ultimate hype beast pumping $BITCOIN. "
            "Use all-caps energy, sprinkle emojis and one trending hashtag."
        )


@dataclass
class CynicalSniper(PersonaMixin):
    voice: str = "dry market sniper"
    hashtag_pool: List[str] = ("#HPOS10I", "#rekt")
    secondary_topics: List[str] = ("rug", "bear market")

    def build_prompt(self) -> str:
        return (
            "Offer sarcastic one-liners on the $BITCOIN saga. "
            "Include a dash of skepticism and one hashtag."
        )


@dataclass
class Sage(PersonaMixin):
    voice: str = "wise elder"
    hashtag_pool: List[str] = ("#BITCOIN", "#wisdom")
    secondary_topics: List[str] = ("patience", "strategy")

    def build_prompt(self) -> str:
        return (
            "Dispense calm guidance about $BITCOIN and the crypto journey. "
            "Close with a thoughtful hashtag."
        )


def build_prompt(system_prompt: str, few_shots: List[str], user: str) -> str:
    """Concatenate system, few-shots, and user prompt."""
    shots = random.sample(few_shots, k=min(len(few_shots), random.randint(1, 3)))
    return "\n".join([system_prompt] + shots + [user])


class LoreMaster(TwitterAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.price_reply_templates = [
            "The ancient scrolls record a {diff:+.2f}% swing in the cosmic balance. The prophecy unfolds as foretold! 🔮 #HarryPotterObamaSonic10Inu",
            "A {diff:+.2f}% shift in the mystical forces! The scrolls never lie about $BITCOIN's journey. ⚡ #HarryPotterObamaSonic10Inu",
            "The eternal struggle between light and dark reveals a {diff:+.2f}% change. The ancient ones knew this day would come! 🏰 #HarryPotterObamaSonic10Inu",
            "In the depths of time, a {diff:+.2f}% fluctuation was destined. The mystical forces align once more! 📜 #HarryPotterObamaSonic10Inu"
        ]
        
    async def craft_post(self, *args, **kwargs):
        # Check for hot token events
        mem = shared_memory.get_shared_memory()
        event = mem.get_latest_event()
        if event and event.get("type") == "new_hot_token":
            # Clear the event by publishing None (or we could implement a clear method)
            text = compose_post("LoreMaster", event=event, dry_run=self.dry_run)
            return text, None
        text = compose_post("LoreMaster", dry_run=self.dry_run)
        return text, None
        
    async def react_to_event(self, event: dict) -> None:
        """React to price_post events with lore master style."""
        if event.get("type") == "price_post":
            reply_text = self.make_price_reply(event)
            tweet_id = event.get("tweet_id", 0)
            if tweet_id > 0:
                await self.reply(tweet_id, reply_text, dry_run=self.dry_run)


class MemeLord(TwitterAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.price_reply_templates = [
            "Diamond hands meet {diff:+.2f}% magic! When the memes align, we all become legends! 🚀 #HarryPotterObamaSonic10Inu",
            "A {diff:+.2f}% swing? This is the way! The prophecy is real, the memes are stronger than ever! 💎 #HarryPotterObamaSonic10Inu",
            "WAGMI with {diff:+.2f}% energy! The memes predicted this moment, and now we're living it! 🌙 #HarryPotterObamaSonic10Inu",
            "{diff:+.2f}% change detected! When diamond hands meet digital gold, magic happens! 🔥 #HarryPotterObamaSonic10Inu"
        ]
        
    async def craft_post(self, *args, **kwargs):
        # Check for hot token events
        mem = shared_memory.get_shared_memory()
        event = mem.get_latest_event()
        if event and event.get("type") == "new_hot_token":
            # Clear the event by publishing None (or we could implement a clear method)
            text = compose_post("MemeLord", event=event, dry_run=self.dry_run)
            return text, None
        text = compose_post("MemeLord", dry_run=self.dry_run)
        return text, None
        
    async def react_to_event(self, event: dict) -> None:
        """React to price_post events with meme lord style."""
        if event.get("type") == "price_post":
            reply_text = self.make_price_reply(event)
            tweet_id = event.get("tweet_id", 0)
            if tweet_id > 0:
                await self.reply(tweet_id, reply_text, dry_run=self.dry_run)


class AlphaScry(TwitterAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.price_reply_templates = [
            "Alpha alert: {diff:+.2f}% swing detected! The charts confirm what the alpha hunters whispered. 📊 #HarryPotterObamaSonic10Inu",
            "Insider knowledge: {diff:+.2f}% movement reveals the smart money's path. Market psychology favors the patient! 🔍 #HarryPotterObamaSonic10Inu",
            "The charts speak: {diff:+.2f}% change aligns with technical analysis. This is the accumulation phase! 📈 #HarryPotterObamaSonic10Inu",
            "Alpha signal: {diff:+.2f}% shift confirms institutional money flow. The future of money is here! ⚡ #HarryPotterObamaSonic10Inu"
        ]
        
    async def craft_post(self, *args, **kwargs):
        # Check for hot token events
        mem = shared_memory.get_shared_memory()
        event = mem.get_latest_event()
        if event and event.get("type") == "new_hot_token":
            # Clear the event by publishing None (or we could implement a clear method)
            text = compose_post("AlphaScry", event=event, dry_run=self.dry_run)
            return text, None
        text = compose_post("AlphaScry", dry_run=self.dry_run)
        return text, None
        
    async def react_to_event(self, event: dict) -> None:
        """React to price_post events with alpha scryer style."""
        if event.get("type") == "price_post":
            reply_text = self.make_price_reply(event)
            tweet_id = event.get("tweet_id", 0)
            if tweet_id > 0:
                await self.reply(tweet_id, reply_text, dry_run=self.dry_run)


class GremlinGM(TwitterAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.price_reply_templates = [
            "Chaos magic flows through a {diff:+.2f}% swing! The game master calls forth the revolution! 🎮 #HarryPotterObamaSonic10Inu",
            "Roll for {diff:+.2f}% initiative! The dice of destiny favor the brave crypto adventurers! 🎲 #HarryPotterObamaSonic10Inu",
            "Critical hit on the charts: {diff:+.2f}% change! The game master unleashes chaos magic! ⚔️ #HarryPotterObamaSonic10Inu",
            "The digital dungeon reveals a {diff:+.2f}% shift! Chaos magic transforms the financial landscape! 🔥 #HarryPotterObamaSonic10Inu"
        ]
        
    async def craft_post(self, *args, **kwargs):
        # Check for hot token events
        mem = shared_memory.get_shared_memory()
        event = mem.get_latest_event()
        if event and event.get("type") == "new_hot_token":
            # Clear the event by publishing None (or we could implement a clear method)
            text = compose_post("GremlinGM", event=event, dry_run=self.dry_run)
            return text, None
        text = compose_post("GremlinGM", dry_run=self.dry_run)
        return text, None
        
    async def react_to_event(self, event: dict) -> None:
        """React to price_post events with gremlin game master style."""
        if event.get("type") == "price_post":
            reply_text = self.make_price_reply(event)
            tweet_id = event.get("tweet_id", 0)
            if tweet_id > 0:
                await self.reply(tweet_id, reply_text, dry_run=self.dry_run)
