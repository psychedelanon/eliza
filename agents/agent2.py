import logging
from datetime import datetime, timezone
from sys import path as sys_path
from pathlib import Path
import requests
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Ensure the vendor directory is preferred for imports
sys_path.insert(0, str(Path(__file__).parent.parent / "vendor"))
from blacksmith_forge.quickfire import generate_price_chart
from agents.base import TwitterAgent

# Color constants
BTC_COLOR    = "#F7931A"        # orange
HPO_BLUE     = "#0059ff"
HPO_YELLOW   = "#ffd600"
HPO_RED      = "#ff453a"
GREEN_GAIN   = "#00d455"
RED_LOSS     = "#ff453a"

HASHTAGS = ["#BTC", "#BITCOIN", "#Crypto", "#HarryPotterObamaSonic10Inu"]

# Text variations for the post
INTROS = [
    "📊  Bitcoin vs $BITCOIN",
    "💫  Daily Crypto Showdown",
    "🎯  Market Watch",
    "📈  Price Battle",
    "⚡  Crypto Clash"
]

QUESTIONS = [
    "Who won today?",
    "Who's leading?",
    "Who's on top?",
    "Who's winning?",
    "Who's ahead?"
]

log = logging.getLogger("btc_hpo")

def _format_price_for_display(price: float, is_btc: bool = False) -> str:
    """Format price for display in the image."""
    if is_btc:
        if price >= 1_000_000:
            return f"{price/1_000_000:.1f}M"
        elif price >= 1_000:
            return f"{price/1_000:.1f}K"
        else:
            return f"{price:,.0f}"
    else:
        if price < 0.000001:
            return f"{price:.8f}"
        elif price < 0.01:
            return f"{price:.6f}"
        else:
            return f"{price:.4f}"

def _render_tile(prices: dict[str, tuple[float, float]]) -> Path:
    """Generate a side-by-side price comparison tile."""
    fig, ax = plt.subplots(figsize=(8, 3), dpi=100)
    fig.patch.set_facecolor("#101820")
    ax.axis("off")

    # Navy header strip
    ax.add_patch(patches.Rectangle((0, 0.92), 1, 0.08, transform=ax.transAxes, color="#001f3f", zorder=10))
    ax.text(0.5, 0.96, "Bitcoin vs BITCOIN Price Comparison", ha="center", va="center", 
            fontsize=18, color="white", weight="bold", transform=ax.transAxes, zorder=11)

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
        center_x = 0.25 if i == 0 else 0.75
        price, pct = prices[symbol]
        
        # name
        name_color = BTC_COLOR if symbol == "BTC" else HPO_BLUE
        ax.text(center_x, 0.78, symbol,
                ha="center", va="center",
                color=name_color, fontsize=18, weight="bold",
                transform=ax.transAxes, zorder=4)
        
        # price formatting
        price_str = _format_price_for_display(price, symbol == "BTC")
        price_color = "white" if symbol == "BTC" else HPO_YELLOW
            
        # price
        ax.text(center_x, 0.62, price_str,
                ha="center", va="center",
                color=price_color, fontsize=36, weight="bold",
                transform=ax.transAxes, zorder=4)
        
        # pct‑change
        pct_color = GREEN_GAIN if pct >= 0 else RED_LOSS
        ax.text(center_x, 0.48, f"{pct:+.2f}%",
                ha="center", va="center",
                color=pct_color, fontsize=18,
                transform=ax.transAxes, zorder=4)

    out = Path("media") / f"btc_vs_bitcoin_{datetime.now():%Y%m%d}.png"
    fig.tight_layout(pad=0)
    fig.savefig(out, facecolor=fig.get_facecolor())
    plt.close(fig)
    return out

def _fetch_prices():
    """Fetch current prices for BTC and BITCOIN."""
    try:
        # Fetch both BTC and BITCOIN prices from CoinGecko
        resp = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={
                "ids": "bitcoin,harrypotterobamasonic10in",
                "vs_currencies": "usd",
                "include_24hr_change": "true"
            }
        )
        data = resp.json()
        
        btc_price = data["bitcoin"]["usd"]
        btc_change = data["bitcoin"]["usd_24h_change"]
        
        hpo_price = data["harrypotterobamasonic10in"]["usd"]
        hpo_change = data["harrypotterobamasonic10in"]["usd_24h_change"]

        return {
            'BTC': (btc_price, btc_change),
            'BITCOIN': (hpo_price, hpo_change)
        }
    except Exception as e:
        log.error(f"Failed to fetch prices: {e}")
        return {
            'BTC': (0, 0),
            'BITCOIN': (0, 0)
        }

def _shorten_btc_price(price: float) -> str:
    """Format BTC price in a readable way."""
    if price >= 1_000_000:
        return f"${price/1_000_000:.1f}M"
    elif price >= 1_000:
        return f"${price/1_000:.1f}K"
    else:
        return f"${price:.0f}"

def _format_hpo_price(price: float) -> str:
    """Format BITCOIN token price in a readable way."""
    if price < 0.000001:
        return f"${price:.8f}"
    elif price < 0.01:
        return f"${price:.6f}"
    else:
        return f"${price:.4f}"

class Agent2(TwitterAgent):
    def create_post(self) -> tuple[str, str, str]:
        prices = _fetch_prices()
        today = datetime.now(timezone.utc).strftime("%b %d, %Y")
        btc_price, btc_change = prices['BTC']
        hpo_price, hpo_change = prices['BITCOIN']

        # Zero-price guard
        if btc_price == 0 or hpo_price == 0:
            log.warning("data_gap", extra={"agent": "Agent2"})
            return None, None, None

        diverge = abs(btc_change - hpo_change)
        diverge_emoji = "🥊" if diverge >= 2 * min(abs(btc_change), abs(hpo_change)) else ""
        fire_emoji = "🔥" if abs(btc_change) >= 10 or abs(hpo_change) >= 10 else ""

        # Randomly select intro and question
        intro = random.choice(INTROS)
        question = random.choice(QUESTIONS)

        caption = (
            f"{intro}\n"
            f"    — Market close {today} —\n\n"
            f"Bitcoin:   {_shorten_btc_price(btc_price)}  ({btc_change:+.2f}%)\n"
            f"$BITCOIN: {_format_hpo_price(hpo_price)}  ({hpo_change:+.2f}%)\n\n"
            f"{question} {diverge_emoji}{fire_emoji}\n"
            + "  ".join(HASHTAGS)
        )
        
        # Generate the price chart using our local _render_tile function
        img_path = _render_tile(prices)
        
        alt_text = f"Side-by-side price chart. Bitcoin {btc_price:,.0f} {btc_change:+.2f}%, $BITCOIN {hpo_price:.8f} {hpo_change:+.2f}%."
        return caption, img_path, alt_text

# CLI for quick test
def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="run one cycle and exit")
    parser.add_argument("--dry-run", action="store_true", help="skip API calls and operate without credentials")
    args = parser.parse_args()
    if args.once:
        agent = Agent2(idx=2, name="Agent2", personality="crypto", dry_run=args.dry_run)
        text, img_path = agent.craft_post()
        print("Caption:\n", text)
        print("Image:", img_path)
        return

if __name__ == "__main__":
    main() 