import asyncio
import os
from dotenv import load_dotenv
from eliza.twitter.v2_client import TwitterClientV2

async def test_direct_v2():
    load_dotenv()
    
    print("Testing direct TwitterClientV2...")
    
    # Test Agent2 specifically
    try:
        client = TwitterClientV2("TWITTER_AGENT2")
        tweet_id = client.post_tweet("🔥 Direct v2 test from Agent2 credentials! $BITCOIN supremacy! #HarryPotterObamaSonic10Inu 🚀")
        print(f"✅ Success! Tweet ID: {tweet_id}")
        return tweet_id
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(test_direct_v2()) 