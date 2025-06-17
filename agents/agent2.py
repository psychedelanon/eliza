import logging
from datetime import datetime, timezone
from sys import path as sys_path
from pathlib import Path

# Ensure the vendor directory is preferred for imports
sys_path.insert(0, str(Path(__file__).parent.parent / "vendor"))
from blacksmith_forge.quickfire import _fetch_prices, _render_tile, _shorten_btc_price

# Color constants
BTC_COLOR    = "#F7931A"        # orange
HPO_BLUE     = "#0059ff"
HPO_YELLOW   = "#ffd600"
HPO_RED      = "#ff453a"
GREEN_GAIN   = "#00d455"
RED_LOSS     = "#ff453a"

HASHTAGS = ["#BTC", "#BITCOIN", "#Crypto", "#HarryPotterObamaSonic10Inu"]

log = logging.getLogger("btc_hpo")

def create_post() -> tuple[str, str, str]:
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

    caption = (
        f"📊  BTC vs $BITCOIN\n"
        f"    — Market close {today} —\n\n"
        f"BTC:   {_shorten_btc_price(btc_price)}  ({btc_change:+.2f}%)\n"
        f"$BITCOIN: {hpo_price:.2f}  ({hpo_change:+.2f}%)\n\n"
        f"Who won today? {diverge_emoji}{fire_emoji}\n"
        + "  ".join(HASHTAGS)
    )
    img_path = _render_tile(prices)
    alt_text = f"Side-by-side price chart. BTC {btc_price:,.0f} {btc_change:+.2f}%, $BITCOIN {hpo_price:.2f} {hpo_change:+.2f}%."
    return caption, img_path, alt_text

# CLI for quick test
def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="run one cycle and exit")
    parser.add_argument("--dry-run", action="store_true", help="skip API calls and operate without credentials")
    args = parser.parse_args()
    if args.once:
        caption, img_path, alt_text = create_post()
        print("Caption:\n", caption)
        print("Image:", img_path)
        print("Alt-text:", alt_text)
        return

if __name__ == "__main__":
    main() 