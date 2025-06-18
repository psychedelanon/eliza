from __future__ import annotations

import logging
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import requests

from blacksmith_forge.quickfire import generate_price_chart
from agents.base import TwitterAgent
from agents.personas import HypeBeast

log = logging.getLogger("hype_beast")

BTC_COLOR = "#F7931A"
HPO_BLUE = "#0059ff"
HPO_YELLOW = "#ffd600"
GREEN_GAIN = "#00d455"
RED_LOSS = "#ff453a"

INTROS = ["📊 Bitcoin vs $BITCOIN", "💫 Daily Crypto Showdown", "🎯 Market Watch"]
QUESTIONS = ["Who won today?", "Who's ahead?"]


def _fetch_prices() -> dict[str, Tuple[float, float]]:
    try:
        resp = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={
                "ids": "bitcoin,harrypotterobamasonic10in",
                "vs_currencies": "usd",
                "include_24hr_change": "true",
            },
            timeout=5,
        )
        data = resp.json()
        return {
            "BTC": (data["bitcoin"]["usd"], data["bitcoin"]["usd_24h_change"]),
            "BITCOIN": (
                data["harrypotterobamasonic10in"]["usd"],
                data["harrypotterobamasonic10in"]["usd_24h_change"],
            ),
        }
    except Exception as exc:  # pragma: no cover - network failure
        log.warning("price_fetch_failed %s", exc)
        return {"BTC": (0, 0), "BITCOIN": (0, 0)}


def _render_tile(prices: dict[str, Tuple[float, float]]) -> Path:
    fig, ax = plt.subplots(figsize=(8, 3), dpi=100)
    fig.patch.set_facecolor("#101820")
    ax.axis("off")
    ax.add_patch(patches.Rectangle((0, 0.92), 1, 0.08, transform=ax.transAxes, color="#001f3f", zorder=10))
    ax.text(0.5, 0.96, "Bitcoin vs BITCOIN", ha="center", va="center", color="white", fontsize=18, weight="bold", transform=ax.transAxes, zorder=11)

    for i, symbol in enumerate(["BTC", "BITCOIN"]):
        center_x = 0.0 if i == 0 else 0.5
        color = "#004d1a" if symbol == "BTC" else "#3c1212"
        ax.add_patch(patches.Rectangle((center_x, 0), 0.5, 0.92, linewidth=0, facecolor=color, transform=ax.transAxes, zorder=1))

    ax.plot([0.5, 0.5], [0, 0.92], color="white", linewidth=1, zorder=2, transform=ax.transAxes)

    for i, symbol in enumerate(["BTC", "BITCOIN"]):
        center_x = 0.25 if i == 0 else 0.75
        price, pct = prices[symbol]
        name_color = BTC_COLOR if symbol == "BTC" else HPO_BLUE
        ax.text(center_x, 0.78, symbol, ha="center", va="center", color=name_color, fontsize=18, weight="bold", transform=ax.transAxes, zorder=4)
        ax.text(center_x, 0.62, f"{price:.4f}", ha="center", va="center", color="white", fontsize=36, weight="bold", transform=ax.transAxes, zorder=4)
        pct_color = GREEN_GAIN if pct >= 0 else RED_LOSS
        ax.text(center_x, 0.48, f"{pct:+.2f}%", ha="center", va="center", color=pct_color, fontsize=18, transform=ax.transAxes, zorder=4)

    out = Path("media") / f"price_{datetime.now():%Y%m%d}.png"
    fig.tight_layout(pad=0)
    fig.savefig(out, facecolor=fig.get_facecolor())
    plt.close(fig)
    return out


class AgentHypeBeast(TwitterAgent, HypeBeast):
    def __init__(self, *, idx: int, name: str, personality: str, dry_run: bool = False) -> None:
        TwitterAgent.__init__(self, idx=idx, name=name, personality=personality, dry_run=dry_run)
        HypeBeast.__init__(self)

    def create_post(self) -> Tuple[str, Optional[str], Optional[str]]:
        prices = _fetch_prices()
        btc_price, btc_change = prices["BTC"]
        hpo_price, hpo_change = prices["BITCOIN"]
        if btc_price == 0 or hpo_price == 0:
            return None, None, None
        intro = random.choice(INTROS)
        question = random.choice(QUESTIONS)
        caption = (
            f"{intro} — {datetime.now(timezone.utc):%b %d} — \n"
            f"BTC {btc_price:.0f} ({btc_change:+.2f}%) vs $BITCOIN {hpo_price:.6f} ({hpo_change:+.2f}%)\n"
            f"{question}"
        )
        if random.random() < 0.5:
            caption += f" {random.choice(self.hashtag_pool)}"
        img = _render_tile(prices)
        alt = "Price comparison chart"
        return caption[:240], img, alt
