"""
Utilities for Agent2 (crypto market bot).

✓ Fetch prices at market‑close (or whenever run)
✓ Build a side‑by‑side green tile like the sample PNG
✓ Return (caption, image_path) for the Agent to post
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt
import requests
from tenacity import retry, wait_fixed, stop_after_attempt
import matplotlib.patches as patches


COIN_IDS = {
    "BTC": ["bitcoin"],
    "BITCOIN": [
        "harrypotterobamasonic10in",
        "harrypotterobamasonic10inu-eth",
        "harrypotterobamasonic10inu",
    ],
}

LOGO_DIR = Path("media") / "logos"
BRAND = {
    "BTC": {
        "logo": LOGO_DIR / "btc.png",
        "name_color": "#F7931A",          # bitcoin orange
        "price_color": "white",
        "pct_color": "white",
    },
    "BITCOIN": {
        "logo": LOGO_DIR / "hpobtc.png",
        "name_color": "#0059ff",          # blue
        "price_color": "#ffe600",         # yellow
        "pct_color": "#ff0000",           # red
    },
}

MEDIA_DIR = Path("media")
MEDIA_DIR.mkdir(exist_ok=True)

# --------------------------------------------------------------------------- #
# helpers                                                                     #
# --------------------------------------------------------------------------- #
@retry(stop=stop_after_attempt(3), wait=wait_fixed(10))
def _fetch_prices() -> dict[str, tuple[float, float]]:
    """Fetch current prices from CoinGecko."""
    id_list = ",".join({slug for slugs in COIN_IDS.values() for slug in slugs})
    url = (
        "https://api.coingecko.com/api/v3/simple/price"
        f"?ids={id_list}&vs_currencies=usd&include_24hr_change=true"
    )
    raw = requests.get(url, timeout=10).json()
    prices: dict[str, tuple[float, float]] = {}

    for symbol, slugs in COIN_IDS.items():
        for slug in slugs:
            if slug in raw:
                d = raw[slug]
                prices[symbol] = (d["usd"], d["usd_24h_change"])
                break
        else:
            prices[symbol] = (0.0, 0.0)
    return prices


def _shorten_btc_price(price: float) -> str:
    if price >= 1_000_000:
        return f"{price/1_000_000:.1f}M"
    elif price >= 100_000:
        return f"{price/1_000:.0f}k"
    else:
        return f"{price:,.0f}"

def create_post(personality: str) -> tuple[str, str]:
    prices = _fetch_prices()
    today = datetime.now(timezone.utc).strftime("%b %d, %Y")
    btc_price, btc_change = prices['BTC']
    hpo_price, hpo_change = prices['BITCOIN']

    # Emoji logic
    diverge = abs(btc_change - hpo_change)
    diverge_emoji = "🥊" if diverge >= 2 * min(abs(btc_change), abs(hpo_change)) else ""
    fire_emoji = "🔥" if abs(btc_change) >= 10 or abs(hpo_change) >= 10 else ""

    # Caption template
    caption = (
        f"📊  BTC vs $BITCOIN\n"
        f"    — Market close {today} —\n\n"
        f"BTC:   {_shorten_btc_price(btc_price)}  ({btc_change:+.2f}%)\n"
        f"$BITCOIN: {hpo_price:.2f}  ({hpo_change:+.2f}%)\n\n"
        f"Who won today? {diverge_emoji}{fire_emoji}\n"
        f"#BTC  #BITCOIN  #Crypto"
    )
    img_path = _render_tile(prices)
    return caption, str(img_path)


def _render_tile(prices: dict[str, tuple[float, float]]) -> Path:
    fig, ax = plt.subplots(figsize=(8, 3), dpi=100)
    fig.patch.set_facecolor("#101820")
    ax.axis("off")

    # Navy header strip
    ax.add_patch(patches.Rectangle((0, 0.92), 1, 0.08, transform=ax.transAxes, color="#001f3f", zorder=10))
    ax.text(0.5, 0.96, "BTC vs BITCOIN Price Comparison", ha="center", va="center", fontsize=18, color="white", weight="bold", transform=ax.transAxes, zorder=11)

    # Draw colored backgrounds for each half
    for i, symbol in enumerate(["BTC", "BITCOIN"]):
        _, pct = prices[symbol]
        center_x = 0.0 if i == 0 else 0.5
        color = "#004d1a" if symbol == "BTC" else "#3c1212"
        rect = patches.Rectangle(
            (center_x, 0), 0.5, 0.92,
            linewidth=0, facecolor=color, transform=ax.transAxes, zorder=1
        )
        ax.add_patch(rect)

    # Vertical divider
    ax.plot([0.5, 0.5], [0, 0.92], color="white", linewidth=1, zorder=2, transform=ax.transAxes)

    for i, symbol in enumerate(["BTC", "BITCOIN"]):
        side = BRAND[symbol]
        center_x = 0.25 if i == 0 else 0.75
        price, pct = prices[symbol]
        # name
        ax.text(center_x, 0.78, symbol,
                ha="center", va="center",
                color=side["name_color"], fontsize=18, weight="bold",
                transform=ax.transAxes, zorder=4)
        # price formatting
        if symbol == "BTC":
            price_str = f"${_shorten_btc_price(price)}"
            price_color = "white"
        else:
            price_str = f"${price:.2f}"
            price_color = "#FFD600"
        # price
        ax.text(center_x, 0.62, price_str,
                ha="center", va="center",
                color=price_color, fontsize=36, weight="bold",
                transform=ax.transAxes, zorder=4)
        # pct‑change
        pct_color = "#00D455" if pct >= 0 else "#FF453A"
        ax.text(center_x, 0.48, f"{pct:+.2f}%",
                ha="center", va="center",
                color=pct_color, fontsize=18,
                transform=ax.transAxes, zorder=4)

    out = Path("media") / f"btc_vs_bitcoin_{datetime.now():%Y%m%d}.png"
    fig.tight_layout(pad=0)
    fig.savefig(out, facecolor=fig.get_facecolor())
    plt.close(fig)
    return out 