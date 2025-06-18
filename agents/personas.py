from __future__ import annotations

from dataclasses import dataclass
from typing import List
import random
from agents.base import TwitterAgent


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
    def craft_post(self, *args, **kwargs):
        return "LoreMaster's crafted post"


class MemeLord(TwitterAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def craft_post(self, *args, **kwargs):
        return "MemeLord's crafted post"


class AlphaScry(TwitterAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def craft_post(self, *args, **kwargs):
        return "AlphaScry's crafted post"


class GremlinGM(TwitterAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def craft_post(self, *args, **kwargs):
        return "GremlinGM's crafted post"
