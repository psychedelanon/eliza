import time
import os
import asyncio
from pycoingecko import CoinGeckoAPI
from agents.base import TwitterAgent
from eliza.shared_memory import get_shared_memory

class Agent2(TwitterAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    async def craft_post(self):
        """Fetch prices, render chart, return (text, img_path)."""
        prices = await self._fetch_prices_async()
        text   = self._format_price_text(prices)
        img    = self._render_chart(prices) if os.getenv("MEDIA_ENABLE", "false").lower() == "true" else None
        return text, img
        
    async def post(self, content):
        """Override post to publish price_post event after successful post."""
        tweet_id = await super().post(content)
        
        # Check if post was successful (tweet_id can be string or int)
        if tweet_id and str(tweet_id) != "-1" and str(tweet_id) != "123":  # Successful post
            # Extract price data from content
            text = content[0] if isinstance(content, tuple) else content
            
            # Publish price_post event
            try:
                mem = get_shared_memory()
                mem.publish_event({
                    "type": "price_post",
                    "tweet_id": tweet_id,
                    "btc": self.last_prices.get("btc"),
                    "hpo": self.last_prices.get("hpo"),
                    "hpo_pct": self.last_prices.get("hpo_pct"),
                    "agent": self.name,
                    "ts": time.time(),
                    "text": text
                })
            except Exception as e:
                pass
        
        return tweet_id 

    async def _fetch_prices_async(self):
        """Fetch real BTC and $BITCOIN prices and 24h change from CoinGecko."""
        cg = CoinGeckoAPI()
        loop = asyncio.get_event_loop()

        # Fetch BTC price and 24h change
        btc_data = await loop.run_in_executor(None, lambda: cg.get_coin_by_id('bitcoin', localization='false', tickers='false', market_data='true', community_data='false', developer_data='false', sparkline='false'))
        btc = btc_data['market_data']['current_price']['usd']
        btc_pct = btc_data['market_data']['price_change_percentage_24h']

        # Fetch $BITCOIN (HarryPotterObamaSonic10Inu) price and 24h change
        hpo_data = await loop.run_in_executor(None, lambda: cg.get_coin_by_id('harrypotterobamasonic10in', localization='false', tickers='false', market_data='true', community_data='false', developer_data='false', sparkline='false'))
        hpo = hpo_data['market_data']['current_price']['usd']
        hpo_pct = hpo_data['market_data']['price_change_percentage_24h']

        # Save for event publishing
        self.last_prices = {
            "btc": btc,
            "btc_pct": btc_pct,
            "hpo": hpo,
            "hpo_pct": hpo_pct
        }
        return self.last_prices

    def _format_price_text(self, prices):
        """Format a BTC vs $BITCOIN price-comparison tweet."""
        btc = prices["btc"]
        btc_pct = prices["btc_pct"]
        hpo = prices["hpo"]
        hpo_pct = prices["hpo_pct"]
        return (
            f"📊 Price Battle\n"
            f"— Market close {time.strftime('%b %d, %Y')} —\n\n"
            f"Bitcoin:  ${btc:,.1f} ({btc_pct:+.2f}%)\n"
            f"$BITCOIN: ${hpo:.4f} ({hpo_pct:+.2f}%)\n\n"
            f"Who's on top? 🥊🔥\n"
            f"#BTC  #BITCOIN  #Crypto  #HarryPotterObamaSonic10Inu"
        ) 

    def _render_chart(self, prices):
        """Render a BTC vs $BITCOIN price comparison chart and return the image path."""
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        import numpy as np
        import os

        btc = prices["btc"]
        btc_pct = prices["btc_pct"]
        hpo = prices["hpo"]
        hpo_pct = prices["hpo_pct"]

        # Colors
        BTC_COLOR = "#175c2c"
        BTC_TEXT = "orange"
        HPO_COLOR = "#2a1a1a"
        HPO_TEXT = "#00aaff"
        TITLE_BG = "#111"
        TITLE_TEXT = "white"
        PRICE_WHITE = "white"
        PRICE_YELLOW = "#ffe600"
        GREEN = "#66ff66"
        RED = "#ff6666"

        fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
        ax.axis('off')
        fig.patch.set_facecolor('white')

        # Draw rounded rectangle background
        radius = 0.15
        rect = patches.FancyBboxPatch((0, 0), 1, 1, boxstyle=patches.BoxStyle("Round", pad=0.04, rounding_size=0.08),
                                      transform=ax.transAxes, linewidth=0, facecolor='white', zorder=0)
        ax.add_patch(rect)

        # Draw BTC panel (left)
        ax.add_patch(patches.Rectangle((0, 0), 0.5, 1, transform=ax.transAxes, color=BTC_COLOR, zorder=1))
        # Draw BITCOIN panel (right)
        ax.add_patch(patches.Rectangle((0.5, 0), 0.5, 1, transform=ax.transAxes, color=HPO_COLOR, zorder=1))

        # Title bar
        ax.add_patch(patches.Rectangle((0, 0.92), 1, 0.08, transform=ax.transAxes, color=TITLE_BG, zorder=10))
        ax.text(0.5, 0.96, "Bitcoin vs BITCOIN Price Comparison", ha="center", va="center", color=TITLE_TEXT, fontsize=20, weight="bold", transform=ax.transAxes, zorder=11)

        # BTC panel text
        ax.text(0.25, 0.78, "BTC", ha='center', va='center', fontsize=18, color=BTC_TEXT, fontweight='bold', transform=ax.transAxes, zorder=4)
        ax.text(0.25, 0.58, f"{btc/1000:.1f}K", ha='center', va='center', fontsize=44, color=PRICE_WHITE, fontweight='bold', transform=ax.transAxes, zorder=4)
        ax.text(0.25, 0.40, f"{btc_pct:+.2f}%", ha='center', va='center', fontsize=24, color=RED if btc_pct < 0 else GREEN, fontweight='bold', transform=ax.transAxes, zorder=4)

        # BITCOIN panel text
        ax.text(0.75, 0.78, "BITCOIN", ha='center', va='center', fontsize=18, color=HPO_TEXT, fontweight='bold', transform=ax.transAxes, zorder=4)
        ax.text(0.75, 0.58, f"{hpo:.4f}", ha='center', va='center', fontsize=44, color=PRICE_YELLOW, fontweight='bold', transform=ax.transAxes, zorder=4)
        ax.text(0.75, 0.40, f"{hpo_pct:+.2f}%", ha='center', va='center', fontsize=24, color=RED if hpo_pct < 0 else GREEN, fontweight='bold', transform=ax.transAxes, zorder=4)

        # Remove all axes and whitespace
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

        # Save image
        out_dir = "media"
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, f"btc_vs_bitcoin_{int(time.time())}.png")
        plt.savefig(out_path, bbox_inches='tight', pad_inches=0, facecolor=fig.get_facecolor(), transparent=False)
        plt.close(fig)
        return out_path 