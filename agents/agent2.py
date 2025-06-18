import time
import random
from agents.base import TwitterAgent
from eliza.shared_memory import get_shared_memory

class Agent2(TwitterAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    async def craft_post(self, *args, **kwargs):
        """Generate BTC vs HPO price comparison post."""
        # Simulate price data (in real implementation, fetch from API)
        btc_price = round(random.uniform(45000, 55000), 2)
        hpo_price = round(random.uniform(0.0001, 0.001), 6)
        
        # Calculate percentage difference
        diff_pct = ((hpo_price - btc_price) / btc_price) * 100
        
        # Generate price comparison post with more content to meet 140 char minimum
        if diff_pct > 0:
            post_text = f"📊 Market Update: $BITCOIN currently trading at ${btc_price:,.2f} while $HPOS10I shows ${hpo_price:.6f}. HPO is up {diff_pct:+.2f}% vs BTC today. The crypto markets continue their dynamic dance! #HarryPotterObamaSonic10Inu #Crypto"
        else:
            post_text = f"📊 Market Update: $BITCOIN currently trading at ${btc_price:,.2f} while $HPOS10I shows ${hpo_price:.6f}. HPO is down {abs(diff_pct):.2f}% vs BTC today. The crypto markets continue their dynamic dance! #HarryPotterObamaSonic10Inu #Crypto"
        
        return post_text, None
        
    async def post(self, content):
        """Override post to publish price_post event after successful post."""
        tweet_id = await super().post(content)
        
        # Check if post was successful (tweet_id can be string or int)
        if tweet_id and str(tweet_id) != "-1" and str(tweet_id) != "123":  # Successful post
            # Extract price data from content
            text = content[0] if isinstance(content, tuple) else content
            
            # Parse prices from text (updated parsing for new format)
            try:
                # Extract BTC price from new format
                btc_start = text.find("$BITCOIN currently trading at $") + 30
                btc_end = text.find(" while", btc_start)
                btc_price = float(text[btc_start:btc_end].replace(",", "").replace("$", ""))
                
                # Extract HPO price from new format
                hpo_start = text.find("$HPOS10I shows $") + 16
                hpo_end = text.find(". HPO", hpo_start)
                hpo_price = float(text[hpo_start:hpo_end].replace("$", ""))
                
                # Publish price_post event
                mem = get_shared_memory()
                mem.publish_event({
                    "type": "price_post",
                    "tweet_id": tweet_id,
                    "btc": btc_price,
                    "hpo": hpo_price,
                    "agent": self.name,
                    "ts": time.time(),
                    "text": text
                })
                
                print(f"Agent2 published price_post event: BTC=${btc_price}, HPO=${hpo_price}")
                
            except (ValueError, IndexError) as e:
                print(f"Failed to parse prices from post: {e}")
        
        return tweet_id 